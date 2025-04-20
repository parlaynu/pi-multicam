from typing import Iterable, Generator
import numpy as np


def fake_capture(
    pipe: Iterable[dict], 
    *, 
    width: int = 640, 
    height: int = 480
) -> Generator[dict, None, None]:
    """A fake capture operator to allow testing when there is no camera available."""

    print("Building camkit.ops.debug.fake_capture")
    print(f"- width: {width}")
    print(f"- height: {height}")

    def gen():
        for item in pipe:
            item['metadata'] = {
                'fake': True
            }
            item['main'] = {
                'image': np.random.randint(0, 255, size=(height, width, 3), dtype=np.uint8),
                'format': 'RGB888'
            }
            yield item

    return gen()
