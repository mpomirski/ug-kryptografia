#!/bin/bash
# Michał Pomirski 293676
cat hash-.pdf personal.txt | md5sum > hash.txt
cat hash-.pdf personal_.txt | md5sum >> hash.txt
cat hash-.pdf personal.txt | sha1sum >> hash.txt
cat hash-.pdf personal_.txt | sha1sum >> hash.txt
cat hash-.pdf personal.txt | sha224sum >> hash.txt
cat hash-.pdf personal_.txt | sha224sum >> hash.txt
cat hash-.pdf personal.txt | sha256sum >> hash.txt
cat hash-.pdf personal_.txt | sha256sum >> hash.txt
cat hash-.pdf personal.txt | sha384sum >> hash.txt
cat hash-.pdf personal_.txt | sha384sum >> hash.txt
cat hash-.pdf personal.txt | sha512sum >> hash.txt
cat hash-.pdf personal_.txt | sha512sum >> hash.txt
cat hash-.pdf personal.txt | b2sum >> hash.txt
cat hash-.pdf personal_.txt | b2sum >> hash.txt