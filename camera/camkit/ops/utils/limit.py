from typing import Iterable, Generator
import time


def limit(
    pipe: Iterable[dict], 
    *, 
    max_frames: int = -1, 
    max_seconds: float = -1
) -> Generator[dict, None, None]:
    """Enforces a max frame or time limit on the processing.

    When either the frame limit or the time limit is exceeded, the loop terminates.
    """

    print("Building camkit.ops.utils.limit")
    if max_frames > 0:
        print(f"- max_frames: {max_frames}")
    if max_seconds > 0:
        print(f"- max_seconds: {max_seconds}")

    def gen():
        start = time.monotonic()
        for count, item in enumerate(pipe, start=1):
            runtime = time.monotonic() - start
            if (max_frames > 0 and count > max_frames) or (max_seconds > 0 and runtime > max_seconds):
                break
        
            yield item

    return gen()
