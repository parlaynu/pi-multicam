from typing import Iterable, Generator
import os
import cv2

import camkit.ops as ops


image_formats = { 
    'RGB888', 
    'BGR888'
}


def as_image_file(
    pipe: Iterable[dict], 
    *, 
    file_format: str = "jpg",
    image_key: str = 'main.image', 
    format_key: str = 'main.format',
    output_key: str = 'main.jpg'
) -> Generator[dict, None, None]:
    """Saves the main image to disk in the specified format."""
    
    print("Building camkit.ops.encoding.as_image_file")
    print(f"- file_format: {file_format}")
    print(f"- image_key: {image_key}")
    print(f"- format_key: {format_key}")
    print(f"- output_key: {output_key}")

    extension = file_format
    if not extension.startswith("."):
        extension = "." + extension

    image_keys = image_key.split('.')
    format_keys = format_key.split('.')
    output_keys = output_key.split(".")

    
    def gen():
        for item in pipe:
            idx = item['idx']
            
            image = ops.get_nested_value(item, image_keys)
            
            image_format = ops.get_nested_value(item, format_keys)
            assert image_format in image_formats

            # make sure the image channels are in the native OpenCV order
            if image_format != 'RGB888':
                image = cv2.cvtColor(image, cv2.RGB2BGR)
    
            rv, output = cv2.imencode(extension, image)
            if rv == False:
                print(f"Error: failed to encode image as {file_format}")
                return

            ops.set_nested_value(item, output_keys, output.data)

            yield item

    return gen()
