from typing import List
from string import ascii_lowercase
def xor_decrypt(lines):
    cols = []

    # Transpose the lines into columns
    for i in range(len(lines[0])):
        col = [line[i] for line in lines]
        cols.append(col)
    
    decrypted_cols = []
    for col in cols:
        line: List[str] = ["" for _ in range(len(col))]
        diffs = []
        for i in range(len(col)-1):
            diffs.append(ord(col[i]) ^ ord(col[i+1]))

        i = 0
        while i < len(diffs)-3:
	        # m1 ^ m2 = 000... && m2 ^ m3 = 010... && m3 ^ m4 = 010...
            #   m1 = m1 ^ m2 ^ 00000000
            #   m2 = 00100000
            #   m3 = m2 ^ m3 ^ 00100000
            if diffs[i] >> 5 == 0 and diffs[i+1] >> 5 == 2 and diffs[i+2] >> 5 == 2:
                line[i] = (chr(diffs[i] ^ diffs[i+1] ^ 0b00100000))
                line[i+1] = (chr(0b00100000 ^ diffs[i+1]))
                line[i+2] = (chr(0b00100000 ^ diffs[i+2]))
                i += 3
            # m1 ^ m2 = 010... && m2 ^ m3 = 010... && m3 ^ m4 = 000...
            elif diffs[i] >> 5 == 2 and diffs[i+1] >> 5 == 2 and diffs[i+2] >> 5 == 0 and i < len(line)-2:
                line[i] = (chr(0b00100000 ^ diffs[i]))
                line[i+1] = chr(0b00100000)
                line[i+2] = (chr(0b00100000 ^ diffs[i+1]))
                i += 3
            # m1 ^ m2 = 010... && m2 ^ m3 = 000... && m3 ^ m4 = 010...
            elif diffs[i] == diffs[i+2] and diffs[i] >> 5 == 0 and diffs[i+1] >> 5 == 2:
                line[i] = (chr(0b00100000))
                line[i+1] = (chr(diffs[i+1] ^ 0b00100000))
                line[i+2] = (chr(0b00100000))
                i += 3
            # m1 ^ m2 = 000... && m2 ^ m3 = 010... && m3 ^ m4 = 000...
            elif diffs[i] >> 5 == 0 and diffs[i+1] >> 5 == 2 and diffs[i+2] >> 5 == 0:
                line[i] = (chr(diffs[i] ^ diffs[i+1] ^ 0b00100000))
                line[i+1] = (chr(0b00100000 ^ diffs[i+1]))
                line[i+2] = (chr(0b00100000))
                i += 3
            # m1 ^ m2 = 010... && m2 ^ m3 = 000... && m3 ^ m4 = 000...
            elif diffs[i] >> 5 == 2 and diffs[i+1] >> 5 == 0 and diffs[i+2] >> 5 == 0:
                line[i] = (chr(0b00100000))
                line[i+1] = (chr(diffs[i] ^ 0b00100000))
                line[i+2] = (chr(diffs[i+1] ^ diffs[i] ^ 0b00100000))
                i += 1

            else:
                line[i] = ("_")
                i += 1
        decrypted_cols.append("".join(line))
    decrypted_lines = []

    # Transpose the columns back into lines
    for i in range(len(decrypted_cols[0])):
        decrypted_lines.append("".join([col[i] for col in decrypted_cols]))

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