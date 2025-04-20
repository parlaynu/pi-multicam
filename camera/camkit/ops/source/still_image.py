from typing import Generator
from itertools import count
import time
import cv2


def still_image(
    image_file: str, 
    *, 
    fps: int = 2, 
) -> Generator[dict, None, None]:
    """Read an image and display it continually
    """

    # the logging
    print(f"Building camkit.ops.sources.still_image")
    print(f"- image_file: {image_file}")
    print(f"- fps: {fps}")

    # convert frames-per-second to seconds-per-frame
    spf = 1.0 / fps

    image = cv2.imread(image_file, cv2.IMREAD_COLOR)
    def gen():
        
        start = time.monotonic()
        for idx in count():
            item = {
                'idx': idx,
                'stamp': time.monotonic_ns(),
                'metadata': {
                    'name': image_file,
                },
                'main': {
                    'format': 'RGB888',
                    'image': image.copy()
                }
            }
            yield item

            delay = time.monotonic() - start
            if delay < spf:
                time.sleep(spf-delay)
            start = time.monotonic()

    return gen()


    