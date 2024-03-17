from typing import List
from string import ascii_lowercase
import random
def xor_decrypt(lines):
    raise NotImplementedError()
    return decrypted_lines

# Example usage:
encrypted_lines = []

    
def encode_text(block_size: int = 64) -> List[str]:
    plaintext: List[str] = []
    res = []

    with open("plain.txt", "r") as f:
        plaintext = f.read().split('\n')

    with open("key.txt", "r") as f:
        key: str = f.read()

    line: str = ''
    for line in plaintext:
        res.append("".join([chr(ord(a) ^ ord(b)) for a, b in zip(line, key)]))    
    return res

print(*xor_decrypt(encode_text()), sep='\n')
# print(format(ord(' ') >> 5, '08b'))
# print(format(ord('a') >> 5, '08b'))
# print(format(ord('z') >> 5, '08b'))
# print(format((ord('z') ^ ord('a')) >> 5, '08b'))
# print(format((ord('z') ^ ord(' ')) >> 5, '08b'))
# a = ''
# for i in range(32, 97):
#     a += chr(i)
# print(a)