# Michał Pomirski 24.05.2024
from abc import ABC, abstractmethod
from bs4 import BeautifulSoup, NavigableString, ResultSet, Tag
from argparse import ArgumentParser, Namespace
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

    @staticmethod
    @abstractmethod
    def decode(stego: str) -> str:
        pass
    
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

    @staticmethod
    def decode(stego: str) -> str:
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
        return Helper.save_encoded(stego)
    
    @staticmethod
    def save_decoded(plaintext: str) -> None:
        return Helper.save_decoded(plaintext)

    def is_file_big_enough_to_hide(self, cover: str, hex_payload: int) -> bool:
        return len(cover.split('\n')) > Helper.count_bitlength_from_hex(hex_payload)

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

    @staticmethod
    def decode(stego: str) -> str:
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
        return cover.count(' ') > Helper.count_bitlength_from_hex(hex_payload)
    
    def save_decoded(self, plaintext: str) -> None:
        return Helper.save_decoded(plaintext)
    
    def save_encoded(self, stego: str) -> None:
        return Helper.save_encoded(stego)

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
    
    @staticmethod
    def decode(stego: str) -> str:
        parser: BeautifulSoup = BeautifulSoup(stego, 'html.parser')
        paragraphs: ResultSet[Tag] = parser.find_all('p')
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
        return number_of_paragraphs_without_attributes > Helper.count_bitlength_from_hex(hex_payload)
    
    def save_decoded(self, plaintext: str) -> None:
        Helper.save_decoded(plaintext)
    
    def save_encoded(self, stego: str) -> None:
        Helper.save_encoded(stego)
    
class SteganoUsingRedundantTags(SteganoStrategy):
    '''
        This strategy uses redundant tags to encode the message.
        The message is encoded in the following way:
        1. The message is converted to binary.
        2. For each anchor tag in the cover file, unneccessary tags are added.
            An additional tag at the the start of the tag represents 1, and an additional tag at the end of the tag represents 0
            Eg. <a> anchor </a> -> <a></a><a> paragraph </a> represents 1
                <a> anchor </a> -> <a> paragraph </a><a></a> represents 0
        3. At the end of the message, the redundant tag is placed both at the start and at the end of the tag.
    '''
    def __init__(self, cover: str, payload: int) -> None:
        self.parser: BeautifulSoup = BeautifulSoup(cover, 'html.parser')
        self.cover = self.remove_redundant_tags()
        super().__init__(cover, payload)
    
    def remove_redundant_tags(self) -> str:
        html: ResultSet[Tag] = self.parser.find_all(lambda tag: not tag.contents and not tag.attrs)
        for tag in html:
            tag.extract()
        return self.parser.prettify()
    
    
    def save_decoded(self, plaintext: str) -> None:
        Helper.save_decoded(plaintext)
    
    def save_encoded(self, stego: str) -> None:
        Helper.save_encoded(stego)

    def save_sanitized(self) -> None:
        with open('sanitized.html', 'w', encoding='utf-8') as file:
            file.write(self.parser.prettify())
    
    def encode(self, cover: str, hex_payload: int) -> str:
        anchor_tags: ResultSet[Tag] = self.parser.find_all('a')
        payload_bits: str = bin(hex_payload)[2:]
        number_of_bits: int = len(payload_bits)
        for i, bit in enumerate(payload_bits):
            if bit == '1':
                anchor_tags[i].insert_before(self.parser.new_tag('a')) # type: ignore
            elif bit == '0':
                anchor_tags[i].insert_after(self.parser.new_tag('a')) # type: ignore
        anchor_tags[number_of_bits].insert_after(self.parser.new_tag('span')) # type: ignore
        anchor_tags[number_of_bits].insert_before(self.parser.new_tag('span')) # type: ignore
        return self.parser.prettify()
    
    @staticmethod
    def decode(stego: str) -> str:
        parser: BeautifulSoup = BeautifulSoup(stego, 'lxml')
        anchor_tags: ResultSet[Tag] = parser.find_all('a')
        payload: str = ''
        result: str = ''
        payload = ''
        i = 0
        while i < len(anchor_tags):
            a: Tag = anchor_tags[i]
            next_sibling: Tag | NavigableString | None = a.find_next_sibling()
            previous_sibling: Tag | NavigableString | None = a.find_previous_sibling()

            # <a> paragraph </a><a></a> represents 0
            if ((len(a.contents) != 0 or len(a.attrs) != 0 or len(a.contents) != 1) and next_sibling and next_sibling.name == 'a' and ((len(next_sibling.contents) == 0 and len(next_sibling.attrs) == 0) or len(next_sibling.contents) == 1)):
                payload += '0'
                i += 1
            
            # <a></a><a> paragraph </a> represents 1
            if ((len(a.contents) == 0 or len(a.contents) == 1) and next_sibling and next_sibling.name == 'a' and (len(next_sibling.contents) != 0 or len(next_sibling.attrs) != 0 or len(next_sibling.contents) != 1)):
                payload += '1'
                i += 2

            # <a> paragraph </a><span></span> is an end of the message
            elif ((len(a.contents) != 0 or len(a.contents) != 1)
                and next_sibling and next_sibling.name == 'span' and (len(next_sibling.contents) == 0 or len(next_sibling.contents) == 1)
                and previous_sibling and previous_sibling.name == 'span' and (len(previous_sibling.contents) == 0 or len(previous_sibling.contents) == 1)
                ): 
                break

            else:
                i += 1
        hex_payload: str = hex(int(payload, 2))[2:]
        print(payload, hex_payload)
        for i in range(0, len(hex_payload), 2):
            result += chr(int(hex_payload[i] + hex_payload[i+1], 16))
        return result
    
    def is_file_big_enough_to_hide(self, cover: str, hex_payload: int) -> bool:
        number_of_anchor_tags: int = len(self.parser.find_all('a'))
        return number_of_anchor_tags > Helper.count_bitlength_from_hex(hex_payload)

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
        content: str = file.read()
        return int(content, 16)

def read_encoded() -> str:
    # Read the encoded file
    with open('watermark.html', 'r', encoding='utf-8', errors='ignore') as file:
        return file.read()

def menu() -> Namespace:
    parser: ArgumentParser = ArgumentParser(
        prog='stegano.py',
        description='Steganography using HTML files.'
    )
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument('-e', '--encode', action='store_true', help='Encode the message.')
    choice.add_argument('-d', '--decode', action='store_true', help='Decode the message.')
    type_of_stegano = parser.add_mutually_exclusive_group(required=True)
    type_of_stegano.add_argument('-1', '--spaces', action='store_true', help='Use spaces at the end of the line.')
    type_of_stegano.add_argument('-2', '--double_spaces', action='store_true', help='Use double spaces.')
    type_of_stegano.add_argument('-3', '--typos', action='store_true', help='Use typos.')
    type_of_stegano.add_argument('-4', '--redundant_tags', action='store_true', help='Use redundant tags.')

    return parser.parse_args()


def main() -> None:
    args: Namespace = menu()
    # Handle the arguments
    if args.encode:
        cover: str = read_cover()
        payload: int = read_payload()
        if args.spaces:
            stego: SteganoStrategy = SteganoUsingSpacesAtTheEnd(cover, payload)
            stego.save_encoded(stego.encode(stego.cover, stego.payload))
        elif args.double_spaces:
            stego: SteganoStrategy = SteganoUsingDoubleSpaces(cover, payload)
            stego.save_encoded(stego.encode(stego.cover, stego.payload))
        elif args.typos:
            stego: SteganoStrategy = SteganoUsingTypos(cover, payload)
            stego.save_encoded(stego.encode(stego.cover, stego.payload))
        elif args.redundant_tags:
            stego: SteganoStrategy = SteganoUsingRedundantTags(cover, payload)
            stego.save_encoded(stego.encode(stego.cover, stego.payload))
    elif args.decode:
        encoded: str = read_encoded()
        if args.spaces:
            print(SteganoUsingSpacesAtTheEnd.decode(encoded))
            Helper.save_decoded(SteganoUsingSpacesAtTheEnd.decode(encoded))
        elif args.double_spaces:
            print(SteganoUsingDoubleSpaces.decode(encoded))
            Helper.save_decoded(SteganoUsingDoubleSpaces.decode(encoded))
        elif args.typos:
            print(SteganoUsingTypos.decode(encoded))
            Helper.save_decoded(SteganoUsingTypos.decode(encoded))
        elif args.redundant_tags:
            print(SteganoUsingRedundantTags.decode(encoded))
            Helper.save_decoded(SteganoUsingRedundantTags.decode(encoded))


if __name__ == '__main__':
    main()

# TODO: Fix the redundant tags strategy