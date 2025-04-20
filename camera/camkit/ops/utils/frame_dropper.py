from typing import Iterable, Generator


def frame_dropper(
    pipe: Iterable[dict], 
    num_drop: int
) -> Generator[dict, None, None]:
    """Downsamples the framerate by dropping frames."""
    
    print("Building camkit.ops.utils.frame_dropper")
    print(f"- num_drop: {num_drop}")

    def gen():
        count = 0
        for item in pipe:
            if count < num_drop:
                count += 1
                continue
            count = 0

            yield item

    return gen()
