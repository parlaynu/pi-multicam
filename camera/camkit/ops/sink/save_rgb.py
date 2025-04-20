from typing import Iterable, Generator
import os
import cv2

import camkit.ops as ops


image_formats = { 
    'RGB888', 
    'BGR888'
}


def save_rgb(
    pipe: Iterable[dict], 
    outdir: str, 
    *, 
    file_format: str = "jpg",
    image_key: str = 'main.image', 
    format_key: str = 'main.format', 
    prefix: str = 'img'
) -> Generator[dict, None, None]:
    """Saves the main image to disk in the specified format."""
    
    print("Building camkit.ops.sink.save_rgb")
    print(f"- outdir: {outdir}")
    print(f"- file_format: {file_format}")
    print(f"- image_key: {image_key}")
    print(f"- format_key: {format_key}")
    print(f"- prefix: {prefix}")

    os.makedirs(outdir, exist_ok=True)

    image_keys = image_key.split('.')
    format_keys = format_key.split('.')
    
    def gen():
        for items in pipe:
            if not isinstance(items, list):
                items = [items]
        
            for item in items:
                idx = item['idx']
                
                image = ops.get_nested_value(item, image_keys)
                
                image_format = ops.get_nested_value(item, format_keys)
                assert image_format in image_formats

                # make sure the image channels are in the native OpenCV order
                if image_format != 'RGB888':
                    image = cv2.cvtColor(image, cv2.RGB2BGR)

                if name := item.get('name', None):
                    img_path = os.path.join(outdir, f"{prefix}-{idx:04d}-{name}.{file_format}")
                else:
                    img_path = os.path.join(outdir, f"{prefix}-{idx:04d}-rgb.{file_format}")
        
                print(f"Saving {img_path}")
                cv2.imwrite(img_path, image)

                yield item

    return gen()
