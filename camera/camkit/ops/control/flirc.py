from typing import Generator
import select
import time

from .exceptions import FlircNotFoundError


def flirc(
    timeout: float = 1.0
) -> Generator[dict, None, None]:
    """Controller that only captures when the flirc IR remote is pressed"""

    print(f"Building camkit.ops.control.flirc")
    print(f"- timeout: {timeout}")

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
    
    def gen():
        over = False
        idx = 0
    
        while not over:
            # wait for a click event...
            r, *_ = select.select([device], [], [], timeout)

            if len(r) == 0:
                continue
        
            for event in device.read():
                if event.type != ecodes.EV_KEY:
                    continue

                kev = event_factory[event.type](event)
                if kev.keystate != KeyEvent.key_up:
                    continue

                if kev.scancode == ecodes.KEY_ENTER:
                    yield {
                        'stamp': time.monotonic_ns(),
                        'idx': idx
                    }
                    idx += 1
                    break
            
                elif kev.scancode == ecodes.KEY_ESC:
                    over = True
                    break
    
    return gen()


