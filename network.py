import socket
import struct
import hashlib
from protocol import create_version_payload, parse_inv_payload
from blockchain import request_block

def connect_to_node(ip, port=8333):
    """
    Connect to a Bitcoin node.
    
    Parameters:
    ip (str): The IP address of the Bitcoin node.
    port (int): The port to connect to (default is 8333).
    
    Returns:
    socket.socket: The connected socket if successful, None otherwise.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(20)  # Set a timeout for the connection
    print(f"Connecting to {ip}:{port}")
    
    try:
        s.connect((ip, port))
    except Exception as e:
        print(f"Failed to connect to node: {e}")
        return None
    
    # Send version payload
    version_payload = create_version_payload()
    print(f"Sending version payload: {version_payload.hex()}")
    s.sendall(version_payload)
    
    # Receive version response
    try:
        version_response = s.recv(1024)
        print(f"Received version response: {version_response.hex() if version_response else 'None'}")
        if not version_response:
            return None
    except Exception as e:
        print(f"Failed to receive version response: {e}")
        return None

    # Receive verack response
    try:
        verack_response = s.recv(1024)
        print(f"Received verack response: {verack_response.hex() if verack_response else 'None'}")
        if not verack_response:
            return None
    except Exception as e:
        print(f"Failed to receive verack response: {e}")
        return None
    
    # Send verack payload
    verack_payload = (
        b'\xf9\xbe\xb4\xd9' +  # Magic bytes
        b'verack' +            # Command
        b'\x00' * (12 - len(b'verack')) +  # Padding
        struct.pack('<I', 0) +  # Length of the payload
        hashlib.sha256(hashlib.sha256(b'').digest()).digest()[:4]  # Checksum
    )
    print(f"Sending verack payload: {verack_payload.hex()}")
    s.sendall(verack_payload)
    
    return s

def receive_inv_payloads(sock):
    """
    Receive and process inv payloads from the Bitcoin network.
    
    Parameters:
    sock (socket.socket): The socket connected to the Bitcoin node.
    """
    while True:
        try:
            response = sock.recv(1024)
            if not response:
                break
            print("Received response:", response.hex())  # Debugging output

            # Parse the inv payload
            inv_payload = parse_inv_payload(response)
            print(f"Parsed inv payload: {inv_payload}")
            
            for inventory in inv_payload['inventories']:
                if inventory['type'] == 2:  # If it's a block
                    block_hash = inventory['hash']
                    print(f"Requesting block with hash: {block_hash.hex()}")
                    request_block(sock, block_hash)
        except Exception as e:
            print(f"Error receiving inv payload: {e}")
            break
