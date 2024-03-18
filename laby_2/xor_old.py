from string import ascii_lowercase, digits
import argparse
from typing import List


def prepare_text(block_length: int = 64) -> None:
    ALLOWED_CHARS = ascii_lowercase + " " + digits
    output = ""
    with open("orig.txt", "r") as f:
        output = f.read()
        output = output.lower()
        output = "".join([c for c in output if c in ALLOWED_CHARS])
    with open("plain.txt", "w") as f:
        for i in range(0, len(output), block_length):
            if i + block_length < len(output):
                f.write(output[i:i+block_length])
            if i < len(output)-2*block_length:
                f.write('\n')
    print(f"Prepared plain.txt with block size of {block_length}.")
    
def encode_text(block_size: int = 64) -> None:
    plaintext: List[str]
    with open("plain.txt", "r") as f:
        plaintext = [line.rstrip("\n") for line in f.readlines()]

    with open("key.txt", "r") as f:
        key: str = f.read()

    with open("crypto.txt", "w") as f:
        for line in plaintext:
            for i in range(block_size):
                f.write(chr(ord(line[i]) ^ ord(key[i])))
    print("Encoded plain.txt with key.txt and saved to crypto.txt.")

def decode_text(block_size: int = 64) -> None:
    file: str = ""
    key: str = ""

    with open("crypto.txt", "r") as crypto:
        file = crypto.read()
    with open("key.txt", "r") as key_file:
        key = key_file.read()

    with open("decoded.txt", "w") as f:
        for i in range(0, len(file), block_size):
            f.write("".join([chr(ord(file[i+j]) ^ ord(key[j])) for j in range(block_size)]))
            f.write("\n") if i < len(file)-block_size else None
        
    print("Decoded crypto.txt with key.txt and saved to decoded.txt.")

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


def cryptoanalysis(block_size: int = 64) -> None:
    with open("crypto.txt", "r") as f:
        crypto_text: str = f.read()
    
    blocks = ([crypto_text[i:i+block_size] for i in range(0, len(crypto_text), block_size)])
    with open("decrypt.txt", "w") as f:
        f.write("\n".join(xor_decrypt(blocks)))
    print("Performed cryptoanalysis on crypto.txt and saved to decrypt.txt.")

def cli():
    parser = argparse.ArgumentParser(
        description="Repeating the same one-time key.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "-p", "--prepare", action="store_true", help="Prepare text")
    actions.add_argument(
        "-e", "--encode", action="store_true", help="Encode text")
    actions.add_argument(
        "-d", "--decode", action="store_true", help="Decode text")
    actions.add_argument(
        "-k", "--cryptoanalysis", action="store_true", help="Perform cryptoanalysis")


    args = parser.parse_args()
    if args.prepare:
        prepare_text()
        # Create the key
        # print(''.join(random.choices(ascii_lowercase, k=64)))
    elif args.encode:
        encode_text()
    elif args.cryptoanalysis:
        cryptoanalysis()
    elif args.decode:
        decode_text()


def main():
    cli()


if __name__ == "__main__":
    main()
