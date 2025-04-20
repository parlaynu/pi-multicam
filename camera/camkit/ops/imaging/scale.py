from typing import Iterable, Generator
import cv2

import camkit.ops as ops


def scale(
    pipe: Iterable[dict], 
    *, 
    factor_width: float = -1,
    factor_height: float = -1, 
    image_key: str = 'main.image'
) -> Generator[dict, None, None]:
    """Image processing operator that scales the input image by the specified factor.

    The image is looked up in the dict using the 'image_key' parameter. It is split into
    a list by the '.' and looked up recursively.
    """
    if factor_width == -1 and factor_height == -1:
        factor_width = 1.0
        factor_height = 1.0
    elif factor_width == -1:
        factor_width = factor_height
    elif factor_height == -1:
        factor_height = factor_width

    print("Building camkit.ops.imaging.scale")
    print(f"- image_key: {image_key}")
    print(f"- factor width: {factor_width}")
    print(f"- factor height: {factor_height}")

    image_keys = image_key.split('.')

    def gen():
        for item in pipe:
            image = ops.get_nested_value(item, image_keys)
            image = cv2.resize(image, None, fx=factor_width, fy=factor_height)
            ops.set_nested_value(item, image_keys, image)

            yield item

    return gen()

