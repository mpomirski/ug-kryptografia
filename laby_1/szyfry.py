# Author: Michał Pomirski
# Date: 23.02.2024
from string import ascii_lowercase, ascii_uppercase
import argparse
import math


def affine_cipher(plaintext: str, key_a: int, key_b: int) -> str:
    # E(a,b,x)=a·x+b (mod 26), x in [0, 25]

    result: str = ""
    for letter in plaintext:
        if letter in ascii_uppercase:
            result += chr((key_a * (ord(letter) - ord('A')) + key_b) %
                          26 + ord('A'))
        elif letter in ascii_lowercase:
            result += chr((key_a * (ord(letter) - ord('a')) + key_b) %
                          26 + ord('a'))
        else:
            result += letter

    return result


def affine_decipher(encoded_text: str, key_a: int, key_b: int) -> str:
    result: str = ""
    inverse = find_inverse(key_a)

    for letter in encoded_text:
        if letter in ascii_uppercase:
            result += chr((inverse * (ord(letter) - ord('A') - key_b)) %
                          26 + ord('A'))
        elif letter in ascii_lowercase:
            result += chr((inverse * (ord(letter) - ord('a') - key_b)) %
                          26 + ord('a'))
        else:
            result += letter

    return result


def caesar_cipher(plaintext: str, key: int) -> str:
    return affine_cipher(plaintext, 1, key)


def caesar_decipher(encoded_text: str, key: int) -> str:
    return affine_decipher(encoded_text, 1, key)


def find_inverse(x: int) -> int:
    for i in range(1, 26):
        if (x * i) % 26 == 1:
            return i
    return 0


def encode_files_caesar():
    plaintext = ""
    key: list[int] = [0, 0]
    with open("plain.txt") as f:
        plaintext = f.read().strip()
    with open("key.txt") as f:
        key = list(map(int, f.read().strip().split()))
    with open("crypto.txt", "w") as f:
        f.write(caesar_cipher(plaintext, key[1]))
    return 0


def encode_files_affine():
    plaintext = ""
    key: list[int] = [0, 0]
    with open("plain.txt") as f:
        plaintext = f.read().strip()
    with open("key.txt") as f:
        key = list(map(int, f.read().strip().split()))
        if math.gcd(key[0], 26) != 1:
            print("Key A must be coprime with 26")
            return 1
    with open("crypto.txt", "w") as f:
        f.write(affine_cipher(plaintext, key[0], key[1]))
    return 0


def decode_files_caesar():
    encoded_text: str = ""
    key: list[int] = [0, 0]
    with open("crypto.txt") as f:
        encoded_text = f.read().strip()
    with open("key.txt") as f:
        key = list(map(int, f.read().strip().split()))
    with open("decrypt.txt", "w") as f:
        f.write(caesar_decipher(encoded_text, key[1]))
    return 0


def decode_files_affine():
    encoded_text: str = ""
    key: list[int] = [0, 0]
    with open("crypto.txt") as f:
        encoded_text = f.read().strip()
    with open("key.txt") as f:
        key = list(map(int, f.read().strip().split()))
        if math.gcd(key[0], 26) != 1:
            print("Key A must be coprime with 26")
            return 1
    with open("decrypt.txt", "w") as f:
        f.write(affine_decipher(encoded_text, key[0], key[1]))
    return 0


def full_analysis_affine():
    encoded_text = ""
    plaintext = ""
    with open("crypto.txt") as f:
        encoded_text = f.read().strip()
    with open("extra.txt") as f:
        plaintext = f.read().strip()
    for a in range(1, 26):
        if math.gcd(a, 26) != 1:
            continue
        for b in range(26):
            if affine_cipher(plaintext, a, b) == encoded_text:
                with open("key-new.txt", "w") as f:
                    f.write(f"{a} {b}")
                return 0
    print("Key not found")
    return 1


def key_analysis_affine():
    encoded_text = ""
    with open("crypto.txt") as f:
        encoded_text = f.read().strip()
    with open("key-new.txt", "w") as f:
        for a in range(1, 26):
            if math.gcd(a, 26) != 1:
                continue
            for b in range(26):
                f.write(
                    f"Key: {a} {b} : {affine_decipher(encoded_text, a, b)}\n")
    return 1


def full_analysis_caesar():
    encoded_text = ""
    plaintext = ""
    with open("crypto.txt") as f:
        encoded_text = f.read().strip()
    with open("extra.txt") as f:
        plaintext = f.read().strip()
    for b in range(26):
        if caesar_cipher(plaintext, b) == encoded_text:
            with open("key-new.txt", "w") as f:
                f.write(f"{b}")
            return 0
    print("Key not found")
    return 1


def key_analysis_caesar():
    encoded_text = ""
    with open("crypto.txt") as f:
        encoded_text = f.read().strip()
    with open("key-new.txt", "w") as f:
        for b in range(26):
            f.write(f"Key: {b} : {caesar_decipher(encoded_text, b)}\n")
    return 1


def cli():
    parser = argparse.ArgumentParser(
        description="Affine and Caesar cipher encoder/decoder.")
    group_ciphers = parser.add_mutually_exclusive_group()
    group_commands = parser.add_mutually_exclusive_group()
    group_cryptoanalysis = parser.add_mutually_exclusive_group()
    group_ciphers.add_argument(
        "-c", "--caesar", action="store_true", help="Use Caesar cipher")
    group_ciphers.add_argument(
        "-a", "--affine", action="store_true", help="Use Affine cipher")
    group_commands.add_argument(
        "-e", "--encode", action="store_true", help="Encode text")
    group_commands.add_argument(
        "-d", "--decode", action="store_true", help="Decode text")
    group_cryptoanalysis.add_argument(
        "-j", "--full-analysis", action="store_true", help="Guess the key given plaintext and ciphertext")
    group_cryptoanalysis.add_argument(
        "-k", "--key-analysis", action="store_true", help="Guess the key given only ciphertext")

    args = parser.parse_args()
    if args.caesar:
        if args.encode:
            encode_files_caesar()
            print("Encoded")
            print("Created crypto.txt")
        elif args.decode:
            decode_files_caesar()
            print("Decoded")
            print("Created decrypt.txt")
        elif args.full_analysis:
            if full_analysis_caesar() == 0:
                print("Key found")
                print("Created key-new.txt")

        elif args.key_analysis:
            key_analysis_caesar()
            print("Key analysis done")
            print("Created key-new.txt")

    elif args.affine:
        if args.encode:
            encode_files_affine()
            print("Encoded")
            print("Created crypto.txt")
        elif args.decode:
            decode_files_affine()
            print("Decoded")
            print("Created decrypt.txt")
        elif args.full_analysis:
            if full_analysis_affine() == 0:
                print("Key found")
                print("Created key-new.txt")

        elif args.key_analysis:
            key_analysis_affine()
            print("Key analysis done")
            print("Created key-new.txt")


def main():
    cli()


if __name__ == "__main__":
    main()
