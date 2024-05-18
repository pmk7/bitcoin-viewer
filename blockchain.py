import struct
import hashlib
import datetime

def request_block(sock, block_hash):
    """
    Request a specific block from the Bitcoin network.
    
    Parameters:
    sock (socket.socket): The socket connected to the Bitcoin node.
    block_hash (bytes): The hash of the block to request.
    """
    getdata_payload = (
        b'\xf9\xbe\xb4\xd9' +  # Magic bytes
        b'getdata' +           # Command
        b'\x00' * 4 +          # Padding
        struct.pack('<I', 37) +  # Length of the payload
        hashlib.sha256(hashlib.sha256(b'\x01\x00\x00\x00' + b'\x02' + block_hash).digest()).digest()[:4] +  # Checksum
        struct.pack('<I', 1) +  # Number of inventory vectors
        struct.pack('<I', 2) +  # Type: block
        block_hash              # The block hash
    )

    sock.sendall(getdata_payload)
    
    block_data = b''
    while True:
        part = sock.recv(1024)
        if not part:
            break
        block_data += part
    
    parsed_block = parse_block(block_data, block_hash)
    display_block(parsed_block)

def parse_block(data, block_hash):
    """
    Parse a block from the raw data.
    
    Parameters:
    data (bytes): The raw block data.
    block_hash (bytes): The hash of the block.
    
    Returns:
    dict: Parsed block data.
    """
    block = {
        'version': struct.unpack('<I', data[0:4])[0],
        'prev_block': data[4:36],
        'merkle_root': data[36:68],
        'timestamp': struct.unpack('<I', data[68:72])[0],
        'bits': struct.unpack('<I', data[72:76])[0],
        'nonce': struct.unpack('<I', data[76:80])[0],
        'transactions': [],  # Transactions to be parsed
        'block_hash': block_hash  # Actual block hash from the network
    }

    tx_count, offset = decode_varint(data[80:])
    for _ in range(tx_count):
        tx, offset = parse_transaction(data, offset)
        if tx:
            block['transactions'].append(tx)

    return block

def decode_varint(data):
    """
    Decode a variable length integer.
    
    Parameters:
    data (bytes): The data containing the varint.
    
    Returns:
    tuple: The decoded integer and the size of the varint.
    """
    first = data[0]
    if first < 0xfd:
        return first, 1
    elif first == 0xfd:
        return struct.unpack('<H', data[1:3])[0], 3
    elif first == 0xfe:
        return struct.unpack('<I', data[1:5])[0], 5
    else:
        return struct.unpack('<Q', data[1:9])[0], 9

def parse_transaction(data, offset):
    """
    Parse a transaction from the raw data.
    
    Parameters:
    data (bytes): The raw transaction data.
    offset (int): The current offset in the data.
    
    Returns:
    tuple: The parsed transaction and the new offset.
    """
    tx = {'outputs': []}
    offset += 4  # Skip the transaction length
    output_count, varint_size = decode_varint(data[offset:])
    offset += varint_size

    for _ in range(output_count):
        value = struct.unpack('<Q', data[offset:offset+8])[0]
        offset += 8  # Skip value
        script_length, varint_size = decode_varint(data[offset:])
        offset += varint_size + script_length  # Skip script length and script itself
        tx['outputs'].append({'value': value})

    return tx, offset

def display_block(block):
    """
    Display block information in a human-readable format.
    
    Parameters:
    block (dict): The parsed block data.
    """
    timestamp = datetime.datetime.fromtimestamp(block['timestamp']).strftime('%d %B %Y at %H:%M')
    transactions = block['transactions']
    nonce = block['nonce']
    difficulty = block['bits']
    
    print(f"Block added on: {timestamp}")
    print(f"Transactions: {len(transactions)}")
    for i, tx in enumerate(transactions):
        print(f"Transaction {i+1}:")
        for j, output in enumerate(tx['outputs']):
            print(f"  Output {j+1}: {output['value']} satoshis")
    print(f"Nonce: {nonce}")
    print(f"Difficulty: {difficulty}")
    
    verify_block_hash(block)

def verify_block_hash(block):
    """
    Verify the hash of the block.
    
    Parameters:
    block (dict): The parsed block data.
    """
    # Create the block header for hashing
    block_header = (
        struct.pack('<I', block['version']) +
        block['prev_block'] +
        block['merkle_root'] +
        struct.pack('<I', block['timestamp']) +
        struct.pack('<I', block['bits']) +
        struct.pack('<I', block['nonce'])
    )
    
    # Compute the block hash
    computed_hash = hashlib.sha256(hashlib.sha256(block_header).digest()).digest()
    print(f"Computed block hash: {computed_hash.hex()}")
    
    # Compare the computed hash with the actual block hash
    if computed_hash == block['block_hash']:
        print("Block hash verified successfully!")
    else:
        print("Block hash verification failed!")
