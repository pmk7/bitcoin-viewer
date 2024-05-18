from network import connect_to_node, receive_inv_payloads
import socket

if __name__ == "__main__":
    try:
        ip_addresses = socket.gethostbyname_ex('seed.bitcoin.sipa.be')
        print(f"Resolved IP addresses: {ip_addresses}")
        
        for ip in ip_addresses[2]:
            print(f"Connecting to {ip}:8333")
            sock = connect_to_node(ip)
            if sock:
                try:
                    receive_inv_payloads(sock)
                    break
                except KeyboardInterrupt:
                    sock.close()
                    break
                except Exception as e:
                    print(f"Error while receiving data from {ip}: {e}")
                    sock.close()
    except socket.gaierror as e:
        print(f"DNS lookup failed: {e}")
