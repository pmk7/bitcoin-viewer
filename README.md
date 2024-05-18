# Bitcoin Blockchain Viewer

## Description
This project is a Bitcoin blockchain viewer application. It connects to the Bitcoin network, receives broadcasts when new transactions are sent or new blocks are mined, and displays information about the blocks.

## Features
- Connects to the Bitcoin network
- Receives and parses `inv` payloads
- Requests block data from the network
- Displays block details including:
  - Date and time the block was added
  - List of transactions and their values
  - Nonce used to hash the block
  - Difficulty level
  - Verification of the block hash

## Requirements
- Python 3.6 or higher
- Dependencies specified in `requirements.txt`

## Installation
1. Install dependencies:
   `pip install -r requirements.txt`

2. Run program
   `python3 main.py`

## Files
- `main.py` : The entry point of the application. Manages connections to Bitcoin nodes.
- `network.py` : Handles network connections and communication with Bitcoin nodes.
- `protocol.py` : Constructs and parses Bitcoin protocol messages.
- `blockchain.py` : Parses block data and displays block information.



