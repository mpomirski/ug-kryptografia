import hmac
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import hashlib
from typing import Any


def load_image(path: str) -> np.ndarray[Any, np.dtype[np.uint8]]:
    img: Image.Image = Image.open(path).convert("L")
    return np.array(img)


def split_into_blocks(image: np.ndarray[Any, np.dtype[np.uint8]], block_size: int) -> np.ndarray[Any, np.dtype[np.uint8]]:
    height: int
    width: int
    height, width = image.shape
    return image.reshape(height // block_size, block_size, width // block_size, block_size).swapaxes(1, 2).reshape(-1, block_size, block_size)


def join_blocks(blocks: np.ndarray[Any, np.dtype[np.uint8]], image_shape: tuple[int, ...]) -> np.ndarray[Any, np.dtype[np.uint8]]:
    height: int
    width: int
    height, width = image_shape
    block_size: int = blocks.shape[1]
    return blocks.reshape(height // block_size, width // block_size, block_size, block_size).swapaxes(1, 2).reshape(height, width)


def encode_single_block(block: np.ndarray[Any, np.dtype[np.uint8]], key: str = "") -> np.ndarray[Any, np.dtype[np.uint8]]:
    block_shape: tuple[int, ...] = block.shape
    byte_string: str = hmac.new(
        key.encode(), block.tobytes(), hashlib.md5).hexdigest()
    decoded_array = np.frombuffer(bytes.fromhex(
        byte_string), dtype=np.uint8)

    # padding with zeros if needed
    if len(decoded_array) < block.size:
        decoded_array = np.pad(
            decoded_array, (0, block.size - len(decoded_array)))
    decoded_array = decoded_array.reshape(block_shape)
    return decoded_array


def encode_blocks_ECB(blocks: np.ndarray[Any, np.dtype[np.uint8]], key: str = "") -> np.ndarray[Any, np.dtype[np.uint8]]:
    result: np.ndarray[Any, np.dtype[np.uint8]] = np.zeros(
        blocks.shape, dtype=np.uint8)
    for i, block in enumerate(blocks):
        result[i] = encode_single_block(block, key)

    return result


def encode_blocks_CBC(blocks: np.ndarray[Any, np.dtype[np.uint8]], key: str = "") -> np.ndarray[Any, np.dtype[np.uint8]]:
    result: np.ndarray[Any, np.dtype[np.uint8]] = np.zeros(
        blocks.shape, dtype=np.uint8)
    prev_block: np.ndarray[Any, np.dtype[np.uint8]] = np.random.randint(
        0, 2, blocks[0].shape, dtype=np.uint8)

    for i, block in enumerate(blocks):
        new_block: np.ndarray[Any, np.dtype[np.uint8]] = np.array([pixel ^ prev_pixel for pixel, prev_pixel in zip(
            block.flatten(), prev_block.flatten())])

        new_block = new_block.reshape(
            blocks[0].shape)
        new_block = encode_single_block(new_block, key)

        prev_block = new_block
        result[i] = new_block
    return result


def resizeImage(image: np.ndarray[Any, np.dtype[np.uint8]], block_size: int) -> np.ndarray[Any, np.dtype[np.uint8]]:
    return image[:image.shape[0] // block_size * block_size,
                 :image.shape[1] // block_size * block_size]


def encodeECBandSave(image: np.ndarray[Any, np.dtype[np.uint8]], block_size: int, key: str, debug: bool, blocks: np.ndarray[Any, np.dtype[np.uint8]]) -> None:
    image_encoded: np.ndarray[Any, np.dtype[np.uint8]
                              ] = encode_blocks_ECB(blocks, key)
    image_reconstructed: np.ndarray[Any, np.dtype[np.uint8]] = join_blocks(
        image_encoded, image.shape)

    plt.imsave(f"ecb_crypto.bmp", image_reconstructed, cmap="gray")
    if debug:
        print("ECB ENCODING:")
        print(f"Block size: {block_size}")
        print(f"Original image shape: {image.shape}")
        print(f"Blocks shape: {blocks.shape}")
        print(f"Encoded image shape: {image_encoded.shape}")
        print(f"Reconstructed image shape: {image_reconstructed.shape}")
        print(f"Images saved as ecb_crypto.bmp")


def encodeCBCandSave(image: np.ndarray[Any, np.dtype[np.uint8]], block_size: int, key: str, debug: bool, blocks: np.ndarray[Any, np.dtype[np.uint8]]) -> None:
    image_encoded: np.ndarray[Any, np.dtype[np.uint8]
                              ] = encode_blocks_CBC(blocks, key)
    image_reconstructed: np.ndarray[Any, np.dtype[np.uint8]] = join_blocks(
        image_encoded, tuple(image.shape))
    plt.imsave(f"cbc_crypto.bmp",
               image_reconstructed, cmap="gray")
    if debug:
        print("CBC ENCODING:")
        print(f"Block size: {block_size}")
        print(f"Original image shape: {image.shape}")
        print(f"Blocks shape: {blocks.shape}")
        print(f"Encoded image shape: {image_encoded.shape}")
        print(f"Reconstructed image shape: {image_reconstructed.shape}")
        print(f"Images saved as cbc_crypto.bmp")


def main() -> None:
    debug: bool = False
    block_size: int = 4
    image_name: str = "plain"
    key: str = ""
    try:
        with open("key.txt", "r") as file:
            key = file.read().strip()
    except FileNotFoundError:
        pass
    try:
        image: np.ndarray[Any, np.dtype[np.uint8]
                          ] = load_image(f'{image_name}.bmp')
    except FileNotFoundError:
        print(f"File {image_name}.bmp not found")
        return

    # Resizing image to be divisible by block size
    image = resizeImage(image, block_size)

    # Splitting image into blocks of size block_size x block_size
    blocks: np.ndarray[Any, np.dtype[np.uint8]
                       ] = split_into_blocks(image, block_size)

    # Encoding and saving images
    encodeECBandSave(image, block_size, key, debug, blocks)
    encodeCBCandSave(image, block_size, key, debug, blocks)


if __name__ == "__main__":
    main()
