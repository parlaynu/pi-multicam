from typing import Iterable, Generator
import time

from picamera2 import Picamera2

from .image_dtypes import image_dtypes


def capture_sync(
    pipe: Iterable[dict], 
    camera: Picamera2, 
    *, 
    arrays: list = ['main'],
    immediate: bool = True
) -> Generator[dict, None, None]:
    """Implements the regular capture."""

    
    print(f"Building camkit.ops.camera.capture_sync")
    print(f"- arrays: {arrays}")
    print(f"- immediate: {immediate}")
    
    def gen():
    
        for idx, item in enumerate(pipe):
            # make sure 'idx' is in item
            item['idx'] = item.get('idx', idx)
        
            # capture the image
            #   if immediate is False, check the metadata to make sure that the capture started after 
            #   the request was made. See the camera documentation for details of the calculation 
            #   below - section '6.4.1. Capturing Requests at Specific Times'.
            item['stamp'] = stamp = item.get('stamp', time.monotonic_ns())
            while True:
                images, metadata = camera.capture_arrays(arrays, wait=True)
                start = metadata['SensorTimestamp'] - 1000 * metadata['ExposureTime']
                if immediate or start >= stamp:
                    break

            # assemble the item
            item['metadata'] = metadata
            for idx, array in enumerate(arrays):
                item[array] = camera.camera_config[array].copy()

                image_format = item[array]['format']
                image_dtype = image_dtypes[image_format]
            
                item[array]['image'] = images[idx].view(image_dtype)

            yield item

    return gen()
