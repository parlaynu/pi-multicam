import time
from enum import IntEnum

from libcamera import controls
from picamera2 import Picamera2


AfModeEnum = IntEnum('AfModeEnum', ['MANUAL', 'AUTO', 'CONTINUOUS'])
AfSpeedEnum = IntEnum('AfSpeedEnum', ['NORMAL', 'FAST'])

_af_modes = {
    AfModeEnum.MANUAL: controls.AfModeEnum.Manual,
    AfModeEnum.AUTO: controls.AfModeEnum.Auto,
    AfModeEnum.CONTINUOUS: controls.AfModeEnum.Continuous
}

_af_speeds = {
    AfSpeedEnum.NORMAL: controls.AfSpeedEnum.Normal,
    AfSpeedEnum.FAST: controls.AfSpeedEnum.Fast
}


def set_focus(
    camera: Picamera2, 
    *,
    mode: AfModeEnum = AfModeEnum.AUTO,
    speed: AfSpeedEnum = AfSpeedEnum.NORMAL,
    lens_position: float = 1.0,
    not_available_ok: bool = False,
    wait: bool = False
) -> bool:
    """Set the camera focus controls.

    If the mode is set to 'AfModeEnum.MANUAL', then use the 'lens_position' parameter to
    directly control the lens position. 

    If 'not_available_ok' is True, then it will return success for cameras that don't have
    focus controls.

    If 'wait' is True, then monitor the 'AfState' attribute from the image metadata until
    it is '2'.
    """


    # check to make sure the camera supports focus
    if not_available_ok:
        mdata = camera.capture_metadata()
        can_focus = mdata.get('AfState', False) or mdata.get('AfMode', False)
        if can_focus == False:
            return True

    # now try and focus
    print("Setting focus", flush=True)
    
    # build the controls
    if mode == AfModeEnum.AUTO or mode == AfModeEnum.CONTINUOUS:
        ctrls = {
            'AfMode': _af_modes[mode],
            'AfSpeed': _af_speeds[speed],
        }
        if mode == AfModeEnum.AUTO:
            ctrls['AfTrigger'] = controls.AfTriggerEnum.Start
        
    else:
        ctrls = {
            'AfMode': _af_modes[mode],
            'LensPosition': lens_position
        }

    # set the controls
    camera.set_controls(ctrls)
    
    # wait for focus
    if wait:
        if mode == AfModeEnum.MANUAL:
            time.sleep(0.5)
        else:
            for i in range(20):
                mdata = camera.capture_metadata()
                if mdata.get('AfState', -1) == 2:
                    print(f"- Lens Position: {mdata['LensPosition']}")
                    print(f"- Focus FoM: {mdata['FocusFoM']}")
                    break
                time.sleep(0.1)


    return True

