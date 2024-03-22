from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import hashlib
def load_image(path: str) -> np.ndarray:
    img = Image.open(path).convert("L")
    return np.array(img)

def split_into_blocks(image: np.ndarray, block_size: int) -> np.ndarray:
    height, width = image.shape
    return image.reshape(height // block_size, block_size, width // block_size, block_size).swapaxes(1, 2).reshape(-1, block_size, block_size)

def join_blocks(blocks: np.ndarray, image_shape: tuple) -> np.ndarray:
    height, width = image_shape
    block_size = blocks.shape[1]
    return blocks.reshape(height // block_size, width // block_size, block_size, block_size).swapaxes(1, 2).reshape(height, width)

def encode_blocks_EBC(blocks: np.ndarray, block_size: int) -> np.ndarray:
    result : np.ndarray = np.zeros(blocks.shape)
    for i, block in enumerate(blocks):
        # print(f"Block {i} before:\n {block}")
        new_block: np.ndarray = int.from_bytes(hashlib.md5(block).digest(), byteorder="big").to_bytes(block_size**2, byteorder="big")
        result[i] = np.frombuffer(new_block, dtype=np.uint8).reshape(block_size, block_size)
        # print(f"Block {i} after:\n {result[i]}")
    print(result.shape)

    return result

def encode_blocks_CBC(blocks: np.ndarray, block_size: int) -> np.ndarray:
    result = np.zeros(blocks.shape)
    prev_block = np.zeros((block_size, block_size), dtype=np.uint8)
    for i, block in enumerate(blocks):
        new_block = [char ^ prev_char for char, prev_char in zip(block.flatten(), prev_block.flatten())]
        new_block = np.array(new_block, dtype=np.uint8).reshape(block_size, block_size)
        prev_block = result[i]
    return result


def main() -> None:
    block_size = 8
    image = load_image("plain24bit.bmp")
    blocks = split_into_blocks(image, block_size)
    image_encoded = encode_blocks_EBC(blocks, block_size)
    image_reconstructed = join_blocks(image_encoded, image.shape)

    plt.imsave("plain24bit_encoded_ebc.bmp", image_reconstructed, cmap="gray")
    print("EBC ENCODING:")
    print(f"Block size: {block_size}")
    print(f"Original image shape: {image.shape}")
    print(f"Blocks shape: {blocks.shape}")
    print(f"Encoded image shape: {image_encoded.shape}")
    print(f"Reconstructed image shape: {image_reconstructed.shape}")
    print("Images saved as plain24bit_encoded_ebc.bmp")

    image_encoded = encode_blocks_CBC(blocks, block_size)
    image_reconstructed = join_blocks(image_encoded, image.shape)
    plt.imsave("plain24bit_encoded_cbc.bmp", image_reconstructed, cmap="gray")
    print("CBC ENCODING:")
    print(f"Block size: {block_size}")
    print(f"Original image shape: {image.shape}")
    print(f"Blocks shape: {blocks.shape}")
    print(f"Encoded image shape: {image_encoded.shape}")
    print(f"Reconstructed image shape: {image_reconstructed.shape}")
    print("Images saved as plain24bit_encoded_cbc.bmp")



if __name__ == "__main__":
    main()