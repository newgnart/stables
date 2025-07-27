"""Configuration constants for event decoding."""

# Data type configurations
PARAM_SIZE_BYTES = 32  # Each parameter is 32 bytes
PARAM_SIZE_HEX = PARAM_SIZE_BYTES * 2  # 64 hex characters
ADDRESS_SIZE_HEX = 40  # 20 bytes = 40 hex chars

# File paths
ABI_DIR = "data/abi"
EVENT_DIR = "data/event"