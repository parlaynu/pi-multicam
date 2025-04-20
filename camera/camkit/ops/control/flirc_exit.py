from typing import Generator
import time
import select
from itertools import count

from .exceptions import FlircNotFoundError


def flirc_exit(
    fps: float = 0.0, 
    max_frames: int = 0
) -> Generator[dict, None, None]:
    """Controller that can stop the capture based on the exit signal from a flirc IR remote."""

    print(f"Building camkit.ops.control.flirc_exit")
    if fps > 0:
        print(f"- fps: {fps}")
    if max_frames > 0:
        print(f"- max_frames: {max_frames}")
    
    # import inside function to avoid errors if not using this module
    import evdev
    from evdev import ecodes, KeyEvent, event_factory

    # find the flirc device
    devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
    for device in devices:
        if device.name.startswith("flirc.tv"):
            break
        device = None
    
    if device is None:
        raise FlircNotFoundError()

    print(f"- controller: {device.path} {device.name}")
    
    # work out the loop time
    loop_time = 1.0/fps if fps > 0 else 0
    
    def gen():
        # NOTE: no timeout the first time through
        tout = 0.0
        over = False
        idx = 0

        start = time.monotonic()
        while True:
            # wait for a click event...
            r, *_ = select.select([device], [], [], tout)
            if len(r) > 0:
                for idx, event in enumerate(device.read()):
                    if event.type != ecodes.EV_KEY:
                        continue

                    kev = event_factory[event.type](event)
                    if kev.keystate != KeyEvent.key_up:
                        continue

                    elif kev.scancode == ecodes.KEY_ESC:
                        over = True
                        break
        
            if over:
                break
        
            # check the elapsed time
            elapsed = time.monotonic() - start
            if elapsed < tout:
                tout = tout - elapsed
                continue
        
            # timeout reached, yield and go again
            start = time.monotonic()
            yield {
                'stamp': time.monotonic_ns(),
                'idx': idx
            }
            idx += 1
        
            if max_frames > 0 and idx >= max_frames:
                break
        
            tout = max(0.0, loop_time - (time.monotonic() - start))

    return gen()


