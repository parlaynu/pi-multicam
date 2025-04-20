from typing import Iterable, Generator
import time

def fps_setter(
    pipe: Iterable[dict], 
    fps: int
) -> Generator[dict, None, None]:
    """Override the incoming fps by dropping frames if necessary."""
    
    print("Building camkit.ops.utils.fps_setter")
    print(f"- fps: {fps}")

    spf = 1.0 / fps

    def gen():
        start = time.monotonic()
        for item in pipe:
            if time.monotonic() - start < spf:
                continue
            start = time.monotonic()

            yield item

    return gen()
