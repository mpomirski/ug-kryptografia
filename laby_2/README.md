[zadanie](https://inf.ug.edu.pl/~amb/krypto15-lab/xor.html)

usage: python3 xor.py [-h] [-p | -e | -k]

orig.txt: plik zawierający dowolny tekst,
-p: plain.txt: plik z tekstem zawierającym co najmniej kilkanaście linijek równej długości, np. 64,
key.txt: plik zawierający klucz, który jest ciągiem dowolnych znaków podanej wyżej długości,
-e: crypto.txt: plik z tekstem zaszyfrowanym, każda jego linijka jest operacją ⊕ z kluczem,
-k: decrypt.txt: plik z tekstem odszyfrowanym. Jeśli litery tekstu jawnego nie można odszyfrować, należy wstawić znak podkreślnika _.
  
options  
  -h, --help:  show this help message and exit  
  -p, --prepare         Prepare the text   
  -e, --encode         Encode the text
  -k, --cryptoanalysis         Cryptoanalysis
