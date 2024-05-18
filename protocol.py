import struct
import socket
import time
import hashlib

def create_version_payload():
    """
    Create the version payload for establishing a connection to a Bitcoin node.
    
    This function constructs a version message as per the Bitcoin protocol,
    which is used to establish a connection with a Bitcoin node.
    
    Returns:
    bytes: The constructed version payload.
    """
    version = 70015  # Protocol version
    services = 0
    timestamp = int(time.time())
    addr_recv_services = 0
    addr_recv_ip = "0.0.0.0"
    addr_recv_port = 8333
    addr_trans_services = 0
    addr_trans_ip = "0.0.0.0"
    addr_trans_port = 8333
    nonce = 0
    user_agent_bytes = 0
    start_height = 0
    relay = 0

    # Construct the payload
    payload = struct.pack('<iQq', version, services, timestamp)
    payload += struct.pack('<Q', addr_recv_services)
    payload += socket.inet_aton(addr_recv_ip)
    payload += struct.pack('>H', addr_recv_port)
    payload += struct.pack('<Q', addr_trans_services)
    payload += socket.inet_aton(addr_trans_ip)
    payload += struct.pack('>H', addr_trans_port)
    payload += struct.pack('<Q', nonce)
    payload += struct.pack('B', user_agent_bytes)
    payload += struct.pack('<i', start_height)
    payload += struct.pack('<?', relay)

    # Prepend the Bitcoin message header
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    message = (
        b'\xf9\xbe\xb4\xd9' +  # Magic bytes
        b'version' +           # Command
        b'\x00' * (12 - len(b'version')) +  # Padding
        struct.pack('<I', len(payload)) +  # Length of the payload
        checksum +             # Checksum
        payload
    )

    return message

def parse_inv_payload(data):
    """
    Parse an 'inv' payload received from a Bitcoin node.
    
    This function parses the 'inv' payload which contains inventory vectors.
    Each inventory vector indicates the type of event (transaction or block)
    and the corresponding hash.
    
    Parameters:
    data (bytes): The raw 'inv' payload data.
    
    Returns:
    dict: A dictionary containing the count of inventory vectors and the list of inventories.
    """
    print(f"Raw inv payload data: {data.hex()}")  # Debugging output
    if len(data) < 4:
        print("Invalid inv payload length")
        return {'count': 0, 'inventories': []}

    count = data[0]
    print(f"Count from inv payload: {count}")
    inventories = []
    
    offset = 1
    for _ in range(count):
        if len(data) < offset + 36:
            print(f"Invalid inventory vector length. Data length: {len(data)}, required: {offset + 36}")
            break

        # Extract inventory type and hash
        inv_type = struct.unpack('<I', data[offset:offset+4])[0]
        inv_hash = data[offset+4:offset+36]
        inventories.append({'type': inv_type, 'hash': inv_hash})
        offset += 36
    
    print(f"Parsed {len(inventories)} inventories from inv payload")
    return {'count': count, 'inventories': inventories}
