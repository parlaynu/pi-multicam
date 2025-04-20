import os
import json
try:
    from picamera2 import Picamera2
except:
    Picamera2 = None

from .stringify import stringify_dict


def save_camera_configs(camera: Picamera2, outdir: str, *, prefix: str = "cam") -> bool:
    """Utility function to save the various camera settings to files."""
    
    os.makedirs(outdir, exist_ok=True)
    
    # save camera information
    infopath = os.path.join(outdir, f"{prefix}-properties.json")
    with open(infopath, "w") as f:
        print(json.dumps(camera.camera_properties, sort_keys=True, indent=2), file=f)

    infopath = os.path.join(outdir, f"{prefix}-controls.json")
    with open(infopath, "w") as f:
        print(json.dumps(camera.camera_controls, sort_keys=True, indent=2), file=f)

    sensor_mode = stringify_dict(camera.configured_mode)

    infopath = os.path.join(outdir, f"{prefix}-sensor.json")
    with open(infopath, "w") as f:
        print(json.dumps(sensor_mode, sort_keys=True, indent=2), file=f)

    camera_config = stringify_dict(camera.camera_configuration())

    infopath = os.path.join(outdir, f"{prefix}-config.json")
    with open(infopath, "w") as f:
        print(json.dumps(camera_config, sort_keys=True, indent=2), file=f)

    return True
