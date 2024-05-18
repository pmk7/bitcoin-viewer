import socket

def test_dns_and_connectivity():
    try:
        ip_addresses = socket.gethostbyname_ex('seed.bitcoin.sipa.be')
        print(f"Resolved IP addresses: {ip_addresses}")
        
        for ip in ip_addresses[2]:
            print(f"Testing connection to {ip}:8333")
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(10)  # 10 seconds timeout
                sock.connect((ip, 8333))
                print(f"Successfully connected to {ip}:8333")
                sock.close()
                return ip  
            except Exception as e:
                print(f"Failed to connect to {ip}:8333 - {e}")
    except socket.gaierror as e:
        print(f"DNS lookup failed: {e}")
    return None

if __name__ == "__main__":
    ip = test_dns_and_connectivity()
    if ip:
        print(f"Using IP address {ip} for further connection.")
    else:
        print("Failed to resolve and connect to any IP address.")
