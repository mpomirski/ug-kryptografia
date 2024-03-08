from string import ascii_lowercase, digits
import argparse
import math
import random

def prepare_text(block_length: int = 64) -> None:
    ALLOWED_CHARS = ascii_lowercase + " " + digits
    output = ""
    with open("orig.txt", "r") as f:
        output = f.read().strip()
        output = output.lower()
        output = "".join([c for c in output if c in ALLOWED_CHARS])
    with open("plain.txt", "w") as f:
        for i in range(0, len(output), block_length):
            f.write(output[i:i+block_length] + "\n") if i + block_length < len(output) else None
    print(f"Prepared plain.txt with block size of {block_length}.")
    
def encode_text() -> None:
    lines = []
    with open("plain.txt", "r") as f:
        lines = [line.strip() for line in f.readlines()]

    with open("key.txt", "r") as f:
        key = f.read().strip()

    with open("crypto", "w") as f:
        for line in lines:
            f.write(("".join([chr(ord(a) ^ ord(b)) for a, b in zip(line, key)]) + b'\n\n').encode("utf-8"))
    print("Encoded plain.txt with key.txt and saved to crypto.txt.")

def decode_text(block_length: int = 64) -> None:
    file = ""
    with open("crypto.txt", "rb") as f:
        file = f.read()
    print(len(file.split(b"\n\n")))
    

    # for line in file:
    #     print(line.decode("utf-8"))

    # with open("key.txt", "r") as f:
    #     key = f.read().strip()

    # with open("decoded.txt", "w") as f:
    #     for line in lines:
    #         f.write("".join([chr(ord(a) ^ ord(b)) for a, b in zip(line, key)]) + "\n")
    print("Decoded crypto.txt with key.txt and saved to decoded.txt.")

def cryptoanalysis() -> None:
    with open("crypto.txt", "r") as f:
        crypto = f.read().strip().split("\n")
    
    xors = []
    for i in range(0, len(crypto)):
        for j in range(i+1, len(crypto)):
            xors.append((i, j, "".join([chr(ord(a) ^ ord(b)) for a, b in zip(crypto[i], crypto[j])])))

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
