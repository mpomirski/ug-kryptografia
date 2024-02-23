#Author: Michał Pomirski
#Date: 23.02.2024
from string import ascii_lowercase, ascii_uppercase
import argparse, os, shutil
import math

def affine_cipher(plaintext: str, key_a: int, key_b: int) -> str:
    #E(a,b,x)=a·x+b (mod 26), x in [0, 25]
    
    result: str = ""
    for letter in plaintext:
        if letter in ascii_uppercase:
            result += chr((key_a * (ord(letter) - ord('A')) + key_b) % 26 + ord('A'))
        elif letter in ascii_lowercase:
            result += chr((key_a * (ord(letter) - ord('a')) + key_b) % 26 + ord('a'))
        else:
            result += letter

    return result


def affine_decipher(encoded_text: str, key_a: int, key_b: int) -> str:
    result: str = ""
    inverse = find_inverse(key_a)

    for letter in encoded_text:
        if letter in ascii_uppercase:
            result += chr((inverse * (ord(letter) - ord('A') - key_b)) % 26 + ord('A'))
        elif letter in ascii_lowercase:
            result += chr((inverse * (ord(letter) - ord('a') - key_b)) % 26 + ord('a'))
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

def main():
    word = "teSTing 123"
    key_a = 11
    key_b = 11

    print(caesar_cipher(word, key_a))
    print(caesar_decipher(caesar_cipher(word, key_a), key_a))
    assert caesar_decipher(caesar_cipher(word, key_a), key_a) == word

    print(affine_cipher(word, key_a, key_b))
    print(affine_decipher(affine_cipher(word, key_a, key_b), key_a, key_b))

    assert affine_decipher(affine_cipher(word, key_a, key_b), key_a, key_b) == word
    

if __name__ == "__main__":
    main()
