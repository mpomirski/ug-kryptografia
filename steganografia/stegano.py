# Michał Pomirski 24.05.2024

def read_cover() -> str:
    with open('cover.html', 'r') as file:
        return file.read()

def read_payload() -> int:
    with open('mess.txt', 'r') as file:
        return int(file.read(), 16)

def read_encoded() -> str:
    with open('watermark.html', 'r') as file:
        return file.read()

def count_bits(n: int) -> int:
    return len(str(hex(n))[2:])*4

def is_file_big_enough_to_hide_first(file: str, hex_payload: str) -> bool:
    lines_in_file = len(file.split('\n'))
    bits_in_payload = count_bits(hex_payload)
    return lines_in_file >= bits_in_payload

def hide_payload_in_file(file: str, hex_payload: str) -> str:
    lines = file.split('\n')
    payload_bits = bin(hex_payload)[2:]
    number_of_bits = len(payload_bits)
    print(f"Payload bits: {payload_bits}")
    for i, bit in enumerate(payload_bits):
        if bit == '1':
            lines[i] += " "
    lines[number_of_bits] += chr(127)
    return '\n'.join(lines)

def encode_first_type() -> None:
    cover = read_cover()
    hex_payload = read_payload()
    if is_file_big_enough_to_hide_first(cover, hex_payload):
        stego = hide_payload_in_file(cover, hex_payload)
        with open('watermark.html', 'w') as file:
            file.write(stego)
    else:
        print('Payload is too big to hide in cover')

def decode_first_type(file: str) -> str:
    lines = file.split('\n')
    payload = ''
    result = ''
    for line in lines:
        if len(line) > 0 and line[-1] == ' ':
            payload += '1'
        elif len(line) > 0 and ord(line[-1]) == 127:
            break
        else:
            payload += '0'
    hex_payload = hex(int(payload, 2))[2:]
    for i in range(0, len(hex_payload), 2):
        print(int(hex_payload[i] + hex_payload[i+1], 16))
        result += chr(int(hex_payload[i] + hex_payload[i+1], 16))
    return result


encode_first_type()
print(decode_first_type(read_encoded()))