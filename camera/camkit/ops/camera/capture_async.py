from typing import Iterable, Generator

from picamera2 import Picamera2

from .image_dtypes import image_dtypes


def capture_async(
    pipe: Iterable[dict], 
    camera: Picamera2, 
    *, 
    arrays: list = ['main']
) -> Generator[dict, None, None]:
    """Implements the async capture."""
    
    print(f"Building camkit.ops.camera.capture_async")
    print(f"  arrays: {arrays}")
    
    def gen():
    
        # submit the initial capture
        job = camera.capture_arrays(arrays, wait=False)
    
        for item in pipe:
            # wait for the current capture
            images, metadata = camera.wait(job)
        
            # kick off the next capture
            job = camera.capture_arrays(arrays, wait=False)
        
            # # assemble the item
            item['metadata'] = metadata

            for idx, array in enumerate(arrays):
                item[array] = camera.camera_config[array].copy()

                image_format = item[array]['format']
                image_dtype = image_dtypes[image_format]
            
                item[array]['image'] = images[idx].view(image_dtype)

            yield item

    return gen()
