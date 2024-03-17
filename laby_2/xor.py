from string import ascii_lowercase, digits
import argparse
from typing import List
import math
import random
from functools import reduce

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
    
def encode_text() -> None:
    plaintext: str = ""
    with open("plain.txt", "r") as f:
        plaintext = f.read()

    with open("key.txt", "r") as f:
        key: str = f.read()

    with open("crypto.txt", "w") as f:
        for i, char in enumerate(plaintext):
            f.write(chr(ord(char) ^ ord(key[i % len(key)])))
    print("Encoded plain.txt with key.txt and saved to crypto.txt.")

def decode_text() -> None:
    file: str = ""
    key: str = ""

    with open("crypto.txt", "r") as crypto:
        file = crypto.read()
    with open("key.txt", "r") as key_file:
        key = key_file.read()

    with open("decoded.txt", "w") as f:
        for i, char in enumerate(file):
            if chr(ord(char) ^ ord(key[i % len(key)])) == "'":
                f.write(" ")
            else:
                f.write(chr(ord(char) ^ ord(key[i % len(key)])))
    print("Decoded crypto.txt with key.txt and saved to decoded.txt.")

def cryptoanalysis(block_size: int = 64) -> None:
    with open("crypto.txt", "r") as f:
        crypto_text: str = f.read()
    crypto = [crypto_text[i:i+block_size] for i in range(0, len(crypto_text), block_size)]
    
    xors = []
    for i in range(len(crypto)-1):
        xors.append("".join([chr(ord(a) ^ ord(b)) for a, b in zip(crypto[i], crypto[i+1])]))
    print(xors)
    # found_key = ""

    # print(found_key)    
    

    

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
