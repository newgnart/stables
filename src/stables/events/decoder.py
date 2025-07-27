"""Core event decoding functionality."""

import json
from typing import Dict, List, Any, Optional
from Crypto.Hash import keccak

from .config import PARAM_SIZE_HEX, ADDRESS_SIZE_HEX
from .types import DecodedEvent, EventDefinition


def get_event_signature(event_abi: Dict[str, Any]) -> str:
    """Generate canonical event signature from ABI."""
    name = event_abi["name"]
    inputs = event_abi["inputs"]
    
    # Build parameter types list
    param_types = []
    for input_item in inputs:
        param_types.append(input_item["type"])
    
    # Create signature: EventName(type1,type2,...)
    signature = f"{name}({','.join(param_types)})"
    return signature


def get_event_topic0(signature: str) -> str:
    """Get keccak256 hash of event signature (topic0)."""
    hash_obj = keccak.new(digest_bits=256)
    hash_obj.update(signature.encode("utf-8"))
    return "0x" + hash_obj.hexdigest()


def get_events(abi: List[Dict[str, Any]]) -> List[EventDefinition]:
    """Extract events from ABI and generate signatures and hashes."""
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
            
            events.append({
                "name": x["name"],
                "signature": signature,
                "topic0": topic0,
                "inputs": x["inputs"],
                "topics": topics,  # [signature_hash, ...indexed_params]
                "data": data_params,  # non-indexed parameters
            })
    return events


def decode_parameter(param_type: str, value: str) -> Any:
    """Decode single parameter based on Solidity type."""
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


def decode_data_parameters(params: List[Dict[str, Any]], data: str) -> Dict[str, Any]:
    """Decode non-indexed parameters from packed data field."""
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


def decode_log_data(event_def: EventDefinition, topics: List[str], data: str) -> Dict[str, Any]:
    """Decode complete log entry using event ABI definition."""
    decoded = {"event": event_def["name"]}
    
    # Decode indexed parameters from topics (skip topic0 = signature hash)
    topic_index = 1
    for param in event_def["inputs"]:
        if param.get("indexed", False):
            if topic_index < len(topics):
                decoded[param["name"]] = decode_parameter(param["type"], topics[topic_index])
                topic_index += 1
    
    # Decode non-indexed parameters from data field
    if data and data != "0x":
        data_params = [p for p in event_def["inputs"] if not p.get("indexed", False)]
        if data_params:
            decoded_data = decode_data_parameters(data_params, data)
            decoded.update(decoded_data)
    
    return decoded


class EventDecoder:
    """Main event decoder class."""
    
    def __init__(self, events_by_topic0: Dict[str, EventDefinition]):
        """Initialize decoder with event definitions."""
        self.events_by_topic0 = events_by_topic0
    
    def decode_log_entry(self, address: str, topics: List[str], data: str) -> DecodedEvent:
        """Decode a single log entry."""
        if not topics:
            return DecodedEvent(
                address=address,
                event_name="unknown",
                parameters={},
                topic0="",
                is_unknown=True,
                raw_topics=topics,
                raw_data=data
            )
        
        topic0 = topics[0]
        
        if topic0 not in self.events_by_topic0:
            return DecodedEvent(
                address=address,
                event_name="unknown",
                parameters={},
                topic0=topic0,
                is_unknown=True,
                raw_topics=topics,
                raw_data=data
            )
        
        event_def = self.events_by_topic0[topic0]
        decoded_params = decode_log_data(event_def, topics, data)
        
        # Extract event name and remove it from parameters
        event_name = decoded_params.pop("event", "unknown")
        
        return DecodedEvent(
            address=address,
            event_name=event_name,
            parameters=decoded_params,
            topic0=topic0,
            is_unknown=False
        )