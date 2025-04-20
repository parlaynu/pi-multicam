from typing import Iterable, Generator
import os
import cv2

import camkit.ops as ops


def save_file(
    pipe: Iterable[dict], 
    outdir: str, 
    *, 
    item_key: str = 'main.jpg', 
    file_extension: str = 'jpg',
    prefix: str = 'img'
) -> Generator[dict, None, None]:
    """Saves the main image to disk in the specified format."""
    
    print("Building camkit.ops.sink.save_file")
    print(f"- outdir: {outdir}")
    print(f"- item_key: {item_key}")
    print(f"- prefix: {prefix}")

    os.makedirs(outdir, exist_ok=True)

    item_keys = item_key.split('.')
    
    def gen():
        for items in pipe:
            if not isinstance(items, list):
                items = [items]
        
            for item in items:
                idx = item['idx']
                
                data = ops.get_nested_value(item, item_keys)
                
                if name := item.get('name', None):
                    item_path = os.path.join(outdir, f"{prefix}-{idx:04d}-{name}.{file_extension}")
                else:
                    item_path = os.path.join(outdir, f"{prefix}-{idx:04d}-rgb.{file_extension}")
        
                print(f"Saving {item_path}")
                with open(item_path, 'wb') as out:
                    out.write(data);

                yield item

    return gen()
