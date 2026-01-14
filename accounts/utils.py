import base64

def decode_base64_to_binary(data):
    return base64.b64decode(data)

def encode_binary_to_base64(binary_data):
    if binary_data:
        return base64.b64encode(binary_data).decode('utf-8')
    return None
