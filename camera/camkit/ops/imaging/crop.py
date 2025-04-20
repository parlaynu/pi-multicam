from typing import Iterable, Generator


def centre_crop(
    pipe: Iterable[dict],
    *, 
    factor: float, 
    image_key: str = 'main.image'
) -> Generator[dict, None, None]:
    """Image processing operator that crops the centre portion of the input image by the specified factor.

    The image is looked up in the dict using the 'image_key' parameter. It is split into
    a list by the '.' and looked up recursively.
    """

    print("Building camkit.ops.imaging.centre_crop")
    print(f"- image_key: {image_key}")
    print(f"- factor: {factor}")

    image_keys = image_key.split('.')

    def gen():
        for item in pipe:
            image_item = None
            image = item
            for key in image_keys:
                image_item = image
                image = image[key]
        
            height, width, *_ = image.shape
            
            new_height = round(height*factor)
            new_width = round(width*factor)
            
            hstart = (height - new_height) // 2
            hend = hstart + new_height
            
            wstart = (width - new_width) // 2
            wend = wstart + new_width
            
            image_item[image_keys[-1]] = image[hstart:hend, wstart:wend, ...]

            yield item

    return gen()

