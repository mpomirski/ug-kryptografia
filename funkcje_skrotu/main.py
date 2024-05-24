# Michał Pomirski 293676
def diff_bits(hash1, hash2):
    diff = 0
    for byte1, byte2 in zip(hash1, hash2):
        diff += bin(byte1 ^ byte2).count('1')
    return diff

with open('hash.txt', 'r') as f:
    hashes = [line.split()[0] for line in f.readlines()]
with open('diff.txt', 'w') as f:
    for i in range(0, len(hashes), 2):
            f.write(hashes[i] + ' ' + hashes[i+1] + ' ')
            f.write(str(diff_bits(bytes.fromhex(hashes[i]), bytes.fromhex(hashes[i+1]))))
            f.write('\n')