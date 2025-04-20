from typing import Iterable, Generator
import cv2

import camkit.ops as ops


def resize(
    pipe: Iterable[dict], 
    *, 
    width: int = -1, 
    height: int = -1, 
    image_key: str = 'main.image'
) -> Generator[dict, None, None]:
    """Image processing operator that resizes the input image to the specified size.

    The image is looked up in the dict using the 'image_key' parameter. It is split into
    a list by the '.' and looked up recursively.
    """

    print("Building camkit.ops.imaging.resize")
    print(f"- image_key: {image_key}")
    if width == -1:
        print(f"- width: scaled")
    else:
        print(f"- width: {width}")
    if height == -1:
        print(f"- height: scaled")
    else:
        print(f"- height: {height}")

    image_keys = image_key.split('.')

    def gen():
        for item in pipe:
            image = ops.get_nested_value(item, image_keys)

            iheight, iwidth, _ = image.shape
            if width == -1 and height == -1:
                fx = 1.0
                fy = 1.0
            elif width == -1:
                fx = fy = height / iheight
            elif height == -1:
                fx = fy = width / iwidth
            else:
                fx = width / iwidth
                fy = height / iheight
        
            image = cv2.resize(image, None, fx=fx, fy=fy)
            ops.set_nested_value(item, image_keys, image)
            
            yield item

    return gen()


