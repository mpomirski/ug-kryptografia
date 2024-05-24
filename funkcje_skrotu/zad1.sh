#!/bin/bash
# Michał Pomirski 293676
md5sum personal.txt > hash.txt
sha1sum personal.txt >> hash.txt
sha224sum personal.txt >> hash.txt
sha256sum personal.txt >> hash.txt
sha384sum personal.txt >> hash.txt
sha512sum personal.txt >> hash.txt
b2sum personal.txt >> hash.txt