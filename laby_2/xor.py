import argparse
from typing import List


def prepare_text(block_length: int = 64) -> None:
    allowed_chars = "abcdefghijklmnopqrstuvwxyz0123456789 "
    output = ""
    with open("orig.txt", "r") as f:
        output = f.read().lower()
        output = "".join([c for c in output if c in allowed_chars])

    with open("plain.txt", "w") as f:
        for i in range(0, len(output), block_length):
            if i + block_length < len(output):
                f.write(output[i:i+block_length])
            if i < len(output) - 2 * block_length:
                f.write('\n')
    print(f"Prepared plain.txt with block size of {block_length}.")


def encode_text(block_size: int = 64) -> None:
    with open("plain.txt", "r") as f:
        plaintext = [line.rstrip("\n") for line in f.readlines()]

    with open("key.txt", "r") as f:
        key = f.read()

    with open("crypto.txt", "w") as f:
        for line in plaintext:
            for i in range(block_size):
                f.write(chr(ord(line[i]) ^ ord(key[i])))
    print("Encoded plain.txt with key.txt and saved to crypto.txt.")


def decode_text(block_size: int = 64) -> None:
    with open("crypto.txt", "r") as crypto:
        file = crypto.read()
    with open("key.txt", "r") as key_file:
        key = key_file.read()

    with open("decoded.txt", "w") as f:
        for i in range(0, len(file), block_size):
            for j in range(block_size):
                if chr(ord(file[i+j]) ^ ord(key[j])) == '\'':
                    f.write(" ")
                else:
                    f.write(chr(ord(file[i+j]) ^ ord(key[j])))
            f.write("\n") if i < len(file) - block_size else None

    print("Decoded crypto.txt with key.txt and saved to decoded.txt.")


def xor_decrypt(lines: List[str]) -> List[str]:
    cols = [[line[i] for line in lines] for i in range(len(lines[0]))]
    decrypted_cols = []

    for col in cols:
        line = ["" for _ in range(len(col))]
        diffs = [ord(col[i]) ^ ord(col[i+1]) for i in range(len(col)-1)]

        i = 0
        while i <= len(diffs):
            try:
                if diffs[i] >> 5 == 0 and diffs[i+1] >> 5 == 2 and diffs[i+2] >> 5 == 2:
                    line[i] = chr(diffs[i] ^ diffs[i+1] ^ 0b00100000)
                    line[i+1] = chr(0b00100000 ^ diffs[i+1])
                    line[i+2] = chr(0b00100000 ^ diffs[i+2])
                    i += 3
                elif diffs[i] >> 5 == 2 and diffs[i+1] >> 5 == 2 and diffs[i+2] >> 5 == 0 and i < len(line) - 2:
                    line[i] = chr(0b00100000 ^ diffs[i])
                    line[i+1] = chr(0b00100000)
                    line[i+2] = chr(0b00100000 ^ diffs[i+1])
                    i += 3
                elif diffs[i] == diffs[i+2] and diffs[i] >> 5 == 0 and diffs[i+1] >> 5 == 2:
                    line[i] = chr(0b00100000)
                    line[i+1] = chr(diffs[i+1] ^ 0b00100000)
                    line[i+2] = chr(0b00100000)
                    i += 3
                elif diffs[i] >> 5 == 0 and diffs[i+1] >> 5 == 2 and diffs[i+2] >> 5 == 0:
                    line[i] = chr(diffs[i] ^ diffs[i+1] ^ 0b00100000)
                    line[i+1] = chr(0b00100000 ^ diffs[i+1])
                    line[i+2] = chr(0b00100000)
                    i += 3
                elif diffs[i] >> 5 == 2 and diffs[i+1] >> 5 == 0 and diffs[i+2] >> 5 == 0:
                    line[i] = chr(0b00100000)
                    line[i+1] = chr(diffs[i] ^ 0b00100000)
                    line[i+2] = chr(diffs[i+1] ^ diffs[i] ^ 0b00100000)
                    i += 1
                else:
                    line[i] = "_"
                    i += 1
            except IndexError:
                line[i] = "_"
                i += 1

        decrypted_cols.append("".join(line))

    decrypted_lines = ["".join([col[i] for col in decrypted_cols]) for i in range(len(decrypted_cols[0]))]
    return decrypted_lines


def cryptoanalysis(block_size: int = 64) -> None:
    with open("crypto.txt", "r") as f:
        crypto_text = f.read()
    blocks = [crypto_text[i:i+block_size] for i in range(0, len(crypto_text), block_size)]
    with open("decrypt.txt", "w") as f:
        f.write("\n".join(xor_decrypt(blocks)))
    print("Performed cryptoanalysis on crypto.txt and saved to decrypt.txt.")


def cli():
    parser = argparse.ArgumentParser(description="Repeating the same one-time key.")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("-p", "--prepare", action="store_true", help="Prepare text")
    actions.add_argument("-e", "--encode", action="store_true", help="Encode text")
    actions.add_argument("-d", "--decode", action="store_true", help="Decode text")
    actions.add_argument("-k", "--cryptoanalysis", action="store_true", help="Perform cryptoanalysis")

    args = parser.parse_args()
    if args.prepare:
        prepare_text()
    elif args.encode:
        encode_text()
    elif args.cryptoanalysis:
        cryptoanalysis()
    elif args.decode:
        decode_text()


if __name__ == "__main__":
    cli()
