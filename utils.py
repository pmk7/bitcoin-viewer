import hashlib

def double_sha256(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()
