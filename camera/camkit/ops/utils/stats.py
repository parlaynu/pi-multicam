from typing import Iterable, Generator
import time
import numpy as np


def stats(
    pipe: Iterable[dict],
    *,
    interval=5,
) -> Generator[dict, None, None]:
    """Generate aggregate stats over 'interval' seconds.
    """
    
    print("Building camkit.ops.debug.stats")

    def gen():
        start = time.monotonic()
        count = 0
        for idx, item in enumerate(pipe):
            yield item
            
            count += 1
            duration = time.monotonic() - start
            if duration < interval:
                continue
            
            fps = count / interval
            print(f"fps: {fps:0.2f}")
            
            start = time.monotonic()
            count = 0

    return gen()

