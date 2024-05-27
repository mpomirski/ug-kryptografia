# Michał Pomirski 24.05.2024
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, ResultSet, Tag

class Helper:
    @staticmethod
    def count_bitlength_from_hex(n: int) -> int:
        return len(str(hex(n))[2:])*4

    @staticmethod
    def save_encoded(stego: str) -> None:
        with open('watermark.html', 'w', encoding='utf-8') as file:
            file.write(stego)

    @staticmethod
    def save_decoded(plaintext: str) -> None:
        with open('detect.txt', 'w', encoding='utf-8') as file:
            file.write(plaintext)

class SteganoStrategy(ABC):
    cover: str = ''
    payload: int = 0

    @abstractmethod
    def __init__(self, cover: str, hex_payload: int) -> None:
        self.cover = cover
        self.payload = hex_payload
        if not self.is_file_big_enough_to_hide(cover, hex_payload):
            raise ValueError('The cover file is too small to hide the message.')

    @abstractmethod
    def encode(self, cover: str, hex_payload: int) -> str:
        pass

    @abstractmethod
    def decode(self, stego: str) -> str:
        pass

    @abstractmethod
    def save_encoded(self, stego: str) -> None:
        Helper.save_encoded(stego)

    @abstractmethod
    def save_decoded(self, plaintext: str) -> None:
        Helper.save_decoded(plaintext)
    
    @abstractmethod
    def is_file_big_enough_to_hide(self, cover: str, hex_payload: int) -> bool:
        pass

class SteganoUsingSpacesAtTheEnd(SteganoStrategy):
    '''
        This strategy uses spaces at the end of the line to encode the message.
        The message is encoded in the following way:
        1. The message is converted to binary.
        2. For each bit in the binary representation of the message, a space is added at the end of the line.
        3. At the end of the message, a special character (127) is added to indicate the end of the message.
    '''
    def __init__(self, cover: str, payload: int) -> None:
        super().__init__(cover, payload)

    def encode(self, cover: str, hex_payload: int) -> str:
        lines: list[str] = cover.split('\n')
        payload_bits: str = bin(hex_payload)[2:]
        number_of_bits: int = len(payload_bits)
        for i, bit in enumerate(payload_bits):
            if bit == '1':
                lines[i] += " "
        lines[number_of_bits] += chr(127) # End of text
        return '\n'.join(lines)

    def decode(self, stego: str) -> str:
        lines: list[str] = stego.split('\n')
        payload: str = ''
        result: str = ''
        for line in lines:
            if len(line) > 0 and line[-1] == ' ':
                payload += '1'
            elif len(line) > 0 and ord(line[-1]) == 127:
                break
            else:
                payload += '0'
        hex_payload: str = hex(int(payload, 2))[2:]
        for i in range(0, len(hex_payload), 2):
            result += chr(int(hex_payload[i] + hex_payload[i+1], 16))
        return result
    
    def save_encoded(self, stego: str) -> None:
        return super().save_encoded(stego)
    
    def save_decoded(self, plaintext: str) -> None:
        return super().save_decoded(plaintext)

    def is_file_big_enough_to_hide(self, cover: str, hex_payload: int) -> bool:
        return len(cover.split('\n')) >= Helper.count_bitlength_from_hex(hex_payload)

class SteganoUsingDoubleSpaces(SteganoStrategy):
    '''
        This strategy uses double spaces to encode the message.
        The message is encoded in the following way:
        1. The message is converted to binary.
        2. For each bit in the binary representation of the message, a space is replaced with a double space.
        3. At the end of the message, three spaces are added to indicate the end of the message.
    '''

    def __init__(self, cover: str, payload: int) -> None:
        super().__init__(cover, payload)
        cover_copy: list[str] = cover.split('\n')
        for i, line in enumerate(cover_copy):
            cover_copy[i] = ' '.join(line.split())
        self.cover = '\n'.join(cover_copy)

    def encode(self, cover: str, hex_payload: int) -> str:
        payload_bits: str = bin(hex_payload)[2:]
        number_of_bits: int = len(payload_bits)
        result: list[str] = []
        payload_index: int = 0
        while payload_index < number_of_bits+1:
            for char in cover:
                if char == ' ' and payload_index < number_of_bits and payload_bits[payload_index] == '1':
                    result.append('  ')
                    payload_index += 1
                elif char == ' ' and payload_index == number_of_bits:
                    result.append('   ')
                    payload_index += 1
                elif char == ' ' and payload_index < number_of_bits and payload_bits[payload_index] == '0':
                    result.append(' ')
                    payload_index += 1
                else:
                    result.append(char)
        return ''.join(result)

    def decode(self, stego: str) -> str:
        payload: str = ''
        result: str = ''
        i = 0
        while i < len(stego):
            char: str = stego[i]
            if i+2 < len(stego) and char == ' ' and stego[i+1] == ' ' and stego[i+2] == ' ':
                break
            elif i+1 < len(stego) and char == ' ' and stego[i+1] == ' ':
                payload += '1'
                i += 2
            elif char == ' ':
                payload += '0'
                i += 1
            else:
                i += 1
        hex_payload: str = hex(int(payload, 2))[2:]
        for i in range(0, len(hex_payload), 2):
            result += chr(int(hex_payload[i] + hex_payload[i+1], 16))
        return result
    
    def is_file_big_enough_to_hide(self, cover: str, hex_payload: int) -> bool:
        return cover.count(' ') >= Helper.count_bitlength_from_hex(hex_payload)
    
    def save_decoded(self, plaintext: str) -> None:
        return super().save_decoded(plaintext)
    
    def save_encoded(self, stego: str) -> None:
        return super().save_encoded(stego)

class SteganoUsingTypos(SteganoStrategy):
    '''
        This strategy uses typos to encode the message.
        The message is encoded in the following way:
        1. The message is converted to binary.
        2. The cover file is parsed, and for each paragraph tag, without margin-bottom and line-height attributes,
              these attributes are added, such that one typo represents a 0 and two typos represent a 1.
            Eg. <p> -> <p style="margin-botom: 0cm; line-height: 100%;"> represents 0 (typo in botom)
                <p> -> <p style="margin-botom: 0cm; lineheight: 100%;"> represents 1 (typo in botom and lineheight)
        3. At the end of the message, a special typo (margin-bottoom: 0cm; line-height: 100%;) is added.
    '''
    def __init__(self, cover: str, payload: int) -> None:
        self.parser: BeautifulSoup = BeautifulSoup(cover, 'html.parser')
        self.cover = self.remove_typos()
        super().__init__(cover, payload)

    def remove_typos(self) -> str:
        paragraphs: ResultSet[Tag] = self.parser.find_all('p')
        for p in paragraphs:
            if 'margin-botom' in p.attrs:
                p.attrs['margin-bottom'] = p.attrs['margin-botom']
                del p.attrs['margin-botom']
            if 'margin-bottoom' in p.attrs:
                p.attrs['margin-bottom'] = p.attrs['margin-bottoom']
                del p.attrs['margin-bottoom']
            if 'lineheight' in p.attrs:
                p.attrs['line-height'] = p.attrs['lineheight']
                del p.attrs['lineheight']
        return self.parser.prettify()

    def encode(self, cover: str, hex_payload: int) -> str:
        paragraphs: ResultSet[Tag] = self.parser.find_all('p')
        payload_bits: str = bin(hex_payload)[2:]
        number_of_bits: int = len(payload_bits)
        for i, bit in enumerate(payload_bits):
            if bit == '1':
                paragraphs[i].attrs['margin-botom'] = '0cm'
                paragraphs[i].attrs['line-height'] = '100%'
            elif bit == '0':
                paragraphs[i].attrs['margin-botom'] = '0cm'
                paragraphs[i].attrs['lineheight'] = '100%'
        paragraphs[number_of_bits].attrs['margin-bottoom'] = '0cm'
        paragraphs[number_of_bits].attrs['line-height'] = '100%'
        return self.parser.prettify()
    
    def decode(self, stego: str) -> str:
        paragraphs: ResultSet[Tag] = self.parser.find_all('p')
        payload: str = ''
        result: str = ''
        for p in paragraphs:
            if 'margin-botom' in p.attrs and 'line-height' in p.attrs:
                payload += '1'
            elif 'margin-botom' in p.attrs and 'lineheight' in p.attrs:
                payload += '0'
            elif 'margin-bottoom' in p.attrs and 'line-height' in p.attrs:
                break
        hex_payload: str = hex(int(payload, 2))[2:]
        for i in range(0, len(hex_payload), 2):
            result += chr(int(hex_payload[i] + hex_payload[i+1], 16))
        return result
    
    def is_file_big_enough_to_hide(self, cover: str, hex_payload: int) -> bool:
        all_paragraphs: ResultSet[Tag] = self.parser.find_all('p')
        number_of_paragraphs_without_attributes: int = len([p for p in all_paragraphs if 'margin-bottom' not in p.attrs and 'line-height' not in p.attrs])
        return number_of_paragraphs_without_attributes >= Helper.count_bitlength_from_hex(hex_payload)
    
    def save_decoded(self, plaintext: str) -> None:
        super().save_decoded(plaintext)
    
    def save_encoded(self, stego: str) -> None:
        super().save_encoded(stego)
    
class SteganoUsingSelfRedundantTags(SteganoStrategy):
    '''
        This strategy uses redundant tags to encode the message.
        The message is encoded in the following way:
        1. The message is converted to binary.
        2. For each self-closing tag in the cover file, the tag is replaced with an explicit closing tag.
            Eg. <img src="image.jpg" /> -> <img src="image.jpg"></img> represents 0
                <img src="image.jpg" /> -> <img src="image.jpg"></img></img> represents 1
    '''
    def __init__(self, cover: str, payload: int) -> None:
        raise NotImplementedError

def read_cover() -> str:
    # Read the cover file removing empty lines
    with open('cover.html', 'r', encoding='utf-8', errors='ignore') as file:
        file_content: str = ''
        for line in file:
            if line.strip():
                file_content += line
        return file_content

def read_payload() -> int:
    # Read the payload file encoded in hex
    with open('mess.txt', 'r', encoding='utf-8', errors='ignore') as file:
        return int(file.read(), 16)

def read_encoded() -> str:
    # Read the encoded file
    with open('watermark.html', 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()


def main() -> None:
    # First type
    cover: str = read_cover()
    payload: int = read_payload()
    # stego: SteganoStrategy = SteganoUsingSpacesAtTheEnd(cover, payload)
    # stego.save_encoded(stego.encode(stego.cover, stego.payload))
    # stego.save_decoded(stego.decode(read_encoded()))
    # Second type
    # stego_2: SteganoStrategy = SteganoUsingDoubleSpaces(cover, payload)
    # stego_2.save_encoded(stego_2.encode(stego_2.cover, stego_2.payload))
    # stego_2.save_decoded(stego_2.decode(read_encoded()))
    # Third type
    stego_3: SteganoStrategy = SteganoUsingTypos(cover, payload)
    stego_3.save_encoded(stego_3.encode(stego_3.cover, stego_3.payload))
    stego_3.save_decoded(stego_3.decode(read_encoded()))


if __name__ == '__main__':
    main()