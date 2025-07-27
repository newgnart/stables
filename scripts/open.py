import os, logging, json, ast
import pandas as pd
from stables.data.source.block_explorer import BlockExplorer
from stables.utils.logging import setup_logging

# Data type configurations
PARAM_SIZE_BYTES = 32  # Each parameter is 32 bytes
PARAM_SIZE_HEX = PARAM_SIZE_BYTES * 2  # 64 hex characters
ADDRESS_SIZE_HEX = 40  # 20 bytes = 40 hex chars

logger = logging.getLogger(__name__)
setup_logging()


def save_sourcecode():
    block_explorer = BlockExplorer(
        api_key=os.getenv("ETHERSCAN_API_KEY"), chain_name="mainnet"
    )

    contract_address = "0x323c03c48660fE31186fa82c289b0766d331Ce21"
    contract_metadata = block_explorer.get_contract_metadata(contract_address)
    logger.info(contract_metadata)
    block_explorer.save_sourcecode(contract_address, "data/sourcecode")
    if contract_metadata["Proxy"]:
        proxy_address = contract_metadata["Implementation"]
        logger.info(f"Proxy address: {proxy_address}")
        block_explorer.save_sourcecode(proxy_address, "data/sourcecode")


def save_contract_abi(contract_address: str):
    block_explorer = BlockExplorer(
        api_key=os.getenv("ETHERSCAN_API_KEY"), chain_name="mainnet"
    )
    abis = []
    save_paths = []
    contract_metadata = block_explorer.get_contract_metadata(contract_address)

    abis.append(block_explorer.get_contract_abi(contract_address))
    save_paths.append(f"data/abi/{contract_address}.json")
    if contract_metadata["Proxy"]:
        implementation_address = contract_metadata["Implementation"]
        abis.append(block_explorer.get_contract_abi(implementation_address))
        save_paths.append(f"data/abi/{contract_address}-implementation.json")

    # Save ABI to file
    os.makedirs("data/abi", exist_ok=True)
    for abi, save_path in zip(abis, save_paths):
        with open(save_path, "w") as f:
            json.dump(json.loads(abi), f, indent=2)
            logger.info(f"ABI saved to {save_path}")


def get_event_signature(event_abi):
    """Generate canonical event signature from ABI"""
    name = event_abi["name"]
    inputs = event_abi["inputs"]

    # Build parameter types list
    param_types = []
    for input_item in inputs:
        param_types.append(input_item["type"])

    # Create signature: EventName(type1,type2,...)
    signature = f"{name}({','.join(param_types)})"
    return signature


def get_event_topic0(signature):
    """Get keccak256 hash of event signature (topic0)"""
    from Crypto.Hash import keccak

    hash_obj = keccak.new(digest_bits=256)
    hash_obj.update(signature.encode("utf-8"))
    return "0x" + hash_obj.hexdigest()


def get_events(abi):
    """Extract events from ABI and generate signatures and hashes"""
    events = []
    for x in abi:
        if x["type"] == "event":
            signature = get_event_signature(x)
            topic0 = get_event_topic0(signature)

            # Separate indexed and non-indexed parameters
            topics = [topic0]  # topic0 is always the event signature hash
            data_params = []

            for input_item in x["inputs"]:
                if input_item.get("indexed", False):
                    topics.append(input_item)
                else:
                    data_params.append(input_item)

            events.append(
                {
                    "name": x["name"],
                    "signature": signature,
                    "topic0": topic0,
                    "inputs": x["inputs"],
                    "topics": topics,  # [signature_hash, ...indexed_params]
                    "data": data_params,  # non-indexed parameters
                }
            )
    return events


def decode_log_data(event_def, topics, data):
    """Decode complete log entry using event ABI definition"""
    decoded = {"event": event_def["name"]}

    # Decode indexed parameters from topics (skip topic0 = signature hash)
    topic_index = 1
    for param in event_def["inputs"]:
        if param.get("indexed", False):
            if topic_index < len(topics):
                decoded[param["name"]] = decode_parameter(
                    param["type"], topics[topic_index]
                )
                topic_index += 1

    # Decode non-indexed parameters from data field
    if data and data != "0x":
        data_params = [p for p in event_def["inputs"] if not p.get("indexed", False)]
        if data_params:
            decoded_data = decode_data_parameters(data_params, data)
            decoded.update(decoded_data)

    return decoded


def decode_parameter(param_type, value):
    """Decode single parameter based on Solidity type"""
    if not value or value == "0x":
        return None

    hex_value = value[2:] if value.startswith("0x") else value

    if param_type == "address":
        return "0x" + hex_value[-ADDRESS_SIZE_HEX:].lower()
    elif param_type.startswith("uint"):
        return int(hex_value, 16)
    elif param_type.startswith("int"):
        bit_size = int(param_type[3:]) if param_type[3:] else 256
        value = int(hex_value, 16)
        if value >= 2 ** (bit_size - 1):
            value -= 2**bit_size
        return value
    elif param_type == "bool":
        return int(hex_value, 16) != 0
    elif param_type.startswith("bytes"):
        return "0x" + hex_value
    else:
        return "0x" + hex_value


def decode_data_parameters(params, data):
    """Decode non-indexed parameters from packed data field"""
    if not data or data == "0x":
        return {}

    hex_data = data[2:] if data.startswith("0x") else data
    decoded = {}

    for i, param in enumerate(params):
        start = i * PARAM_SIZE_HEX
        end = start + PARAM_SIZE_HEX
        if end <= len(hex_data):
            param_hex = hex_data[start:end]
            decoded[param["name"]] = decode_parameter(param["type"], "0x" + param_hex)

    return decoded


def process_log_entry(events_by_topic0, address, topics, data):
    """Process single log entry and return decoded event or unknown event info"""
    if not topics:
        return None

    topic0 = topics[0]
    if topic0 not in events_by_topic0:
        return {
            "unknown_event": topic0,
            "address": address,
            "topics": topics,
            "data": data,
        }

    event_def = events_by_topic0[topic0]
    decoded = decode_log_data(event_def, topics, data)
    decoded["address"] = address

    return decoded


def load_all_events():
    """Load events from all available ABIs"""
    contract_address = "0x323c03c48660fE31186fa82c289b0766d331Ce21"
    events = []

    # Load proxy ABI
    with open(f"data/abi/{contract_address}.json", "r") as f:
        proxy_abi = json.load(f)
    events.extend(get_events(proxy_abi))

    # Load implementation ABI
    implementation = f"{contract_address}-implementation"
    with open(f"data/abi/{implementation}.json", "r") as f:
        impl_abi = json.load(f)
    events.extend(get_events(impl_abi))

    return {event["topic0"]: event for event in events}


def process_dataframe(df_path):
    """Process CSV dataframe and add topic0 and decoded columns"""
    # Load dataframe
    df = pd.read_csv(df_path)

    # Load all events
    events_by_topic0 = load_all_events()

    # Parse topics column (convert string representation of list to actual list)
    df["topics_parsed"] = df["topics"].apply(
        lambda x: ast.literal_eval(x) if pd.notna(x) else []
    )

    # Extract topic0
    df["topic0"] = df["topics_parsed"].apply(
        lambda topics: topics[0] if topics else None
    )

    # Decode events
    def decode_row(row):
        topics = row["topics_parsed"]
        if not isinstance(topics, list) or len(topics) == 0:
            return None
        return process_log_entry(events_by_topic0, row["address"], topics, row["data"])

    df["decoded"] = df.apply(decode_row, axis=1)

    # Drop temporary column
    df = df.drop("topics_parsed", axis=1)

    return df


def test_with_csv_data():
    """Test end-to-end decoding with sample CSV data"""

    # Load events from both proxy and implementation ABIs
    contract_address = "0x323c03c48660fE31186fa82c289b0766d331Ce21"

    # Load proxy ABI
    with open(f"data/abi/{contract_address}.json", "r") as f:
        proxy_abi = json.load(f)
    events = get_events(proxy_abi)

    # Load implementation ABI
    implementation = f"{contract_address}-implementation"
    with open(f"data/abi/{implementation}.json", "r") as f:
        impl_abi = json.load(f)
    events.extend(get_events(impl_abi))

    # Create lookup by topic0
    events_by_topic0 = {event["topic0"]: event for event in events}

    # Test with first few rows from CSV
    test_logs = [
        {
            "address": "0x323c03c48660fe31186fa82c289b0766d331ce21",
            "topics": [
                "0x59b7c8b22741836fc393dc21baa2e8157e039b28c3ee59310f38b2847a2dd29c",
                "0x000000000000000000000000365accfca291e7d3914637abf1f7635db165bb09",
            ],
            "data": "0x",
        },
        {
            "address": "0x57e114b691db790c35207b2e685d4a43181e6061",
            "topics": [
                "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
                "0x000000000000000000000000323c03c48660fe31186fa82c289b0766d331ce21",
                "0x0000000000000000000000004c8560c395869edcdacc96f1a49f2c8bbf752312",
            ],
            "data": "0x0000000000000000000000000000000000000000000009654c693efd74e41b0b",
        },
    ]

    logger.info("=== Testing Log Decoding ===")
    for i, log in enumerate(test_logs):
        decoded = process_log_entry(
            events_by_topic0, log["address"], log["topics"], log["data"]
        )
        logger.info(f"Log {i}: {decoded}")


def test_dataframe_processing():
    """Test processing the CSV dataframe with topic0 and decoded columns"""
    logger.info("=== Testing Dataframe Processing ===")

    # Process the CSV
    df = process_dataframe("notebooks/e.csv")

    # Display results
    logger.info(f"Dataframe shape: {df.shape}")
    logger.info(f"Columns: {df.columns.tolist()}")

    # Show first few decoded events
    for idx, row in df.head(5).iterrows():
        logger.info(f"Row {idx}:")
        logger.info(f"  Address: {row['address']}")
        logger.info(f"  Topic0: {row['topic0']}")
        logger.info(f"  Decoded: {row['decoded']}")
        logger.info("---")

    return df


if __name__ == "__main__":
    # Test dataframe processing
    df_result = test_dataframe_processing()
    df_result.to_csv("r.csv")
