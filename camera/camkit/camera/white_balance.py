import time
from enum import IntEnum

from libcamera import controls
from picamera2 import Picamera2


AwbModeEnum = IntEnum('AwbMode', ['AUTO', 'INCANDESCENT', 'TUNGSTEN', 'FLUORESCENT', 'INDOOR', 'DAYLIGHT', 'CLOUDY', 'CUSTOM', 'MANUAL'])

_awb_modes = {
    AwbModeEnum.AUTO: controls.AwbModeEnum.Auto,
    AwbModeEnum.INCANDESCENT: controls.AwbModeEnum.Incandescent,
    AwbModeEnum.TUNGSTEN: controls.AwbModeEnum.Tungsten,
    AwbModeEnum.FLUORESCENT: controls.AwbModeEnum.Fluorescent,
    AwbModeEnum.INDOOR: controls.AwbModeEnum.Indoor,
    AwbModeEnum.DAYLIGHT: controls.AwbModeEnum.Daylight,
    AwbModeEnum.CLOUDY: controls.AwbModeEnum.Cloudy,
    AwbModeEnum.CUSTOM: controls.AwbModeEnum.Custom
}

# imx219_noir tuning file

def set_whitebalance(
    camera: Picamera2, 
    *, 
    mode: AwbModeEnum = AwbModeEnum.AUTO, 
    red_gain: float = 0.0, 
    blue_gain: float = 0.0, 
) -> bool:
    """Set the camera white balance.

    If the mode is set to 'AwbModeEnum.MANUAL', then use the 'red_gain' and 'blue_gain' parameters
    to directly set the gains if they are non zero. If they are zero, then don't change the current
    value.
    """

    print("Setting white balance", flush=True)
    
    if mode != AwbModeEnum.MANUAL:
        camera.set_controls({
            'AwbEnable': True,
            'AwbMode': _awb_modes[mode]
        })
    
    else:
        mdata = camera.capture_metadata()
        if red_gain <= 0.0:
            red_gain = mdata['ColourGains'][0]
        if blue_gain <= 0.0:
            blue_gain = mdata['ColourGains'][1]
        
        camera.set_controls({
            'AwbEnable': False,
            'ColourGains': (red_gain, blue_gain)
        })
            
        
    return True

