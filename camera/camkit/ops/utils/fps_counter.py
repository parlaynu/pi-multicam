from typing import Iterable, Generator
import time

def fps_counter(
    pipe: Iterable[dict], 
    count_secs: int = 5,
    label: str = "fps"
) -> Generator[dict, None, None]:
    """Downsamples the framerate by dropping frames."""
    
    print("Building camkit.ops.utils.fps_counter")
    print(f"- count_secs: {count_secs}")
    print(f"-      label: {label}")

    def gen():
        start = time.monotonic()
        count = 0
        for item in pipe:
            count += 1
            runtime = time.monotonic() - start
            if runtime > count_secs:
                print(f"{label}: {count/runtime:0.2f}")
                count = 0
                start = time.monotonic()

            yield item

    return gen()
