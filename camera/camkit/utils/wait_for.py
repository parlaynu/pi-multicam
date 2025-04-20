import time


def wait_for(seconds: float) -> bool:
    """Pause for a number of seconds.
    
    Can be used in configuration files to, for example, wait for a camera to settle
    after applying settings.
    """
    print(f"Waiting for {seconds} seconds")
    time.sleep(seconds)

    return True
