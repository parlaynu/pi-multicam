import time
from enum import IntEnum

from libcamera import controls
from picamera2 import Picamera2


MeteringModeEnum = IntEnum('MeteringModeEnum', ['CENTRE_WEIGHTED', 'SPOT', 'MATRIX', 'MANUAL'])
ExposureModeEnum = IntEnum('ExposureModeEnum', ['NORMAL', 'SHORT', 'LONG'])
ConstraintModeEnum = IntEnum('ConstraintModeEnum', ['NORMAL', 'HIGHLIGHT', 'SHADOWS'])

_metering_modes = {
    MeteringModeEnum.CENTRE_WEIGHTED: controls.AeMeteringModeEnum.CentreWeighted,
    MeteringModeEnum.SPOT: controls.AeMeteringModeEnum.Spot,
    MeteringModeEnum.MATRIX: controls.AeMeteringModeEnum.Matrix
}

_exposure_modes = {
    ExposureModeEnum.NORMAL: controls.AeExposureModeEnum.Normal,
    ExposureModeEnum.SHORT: controls.AeExposureModeEnum.Short,
    ExposureModeEnum.LONG: controls.AeExposureModeEnum.Long
}

_constraint_modes = {
    ConstraintModeEnum.NORMAL: controls.AeConstraintModeEnum.Normal,
    ConstraintModeEnum.HIGHLIGHT: controls.AeConstraintModeEnum.Highlight,
    ConstraintModeEnum.SHADOWS: controls.AeConstraintModeEnum.Shadows
}
    

def set_exposure(
    camera: Picamera2, 
    *, 
    metering_mode: MeteringModeEnum = MeteringModeEnum.CENTRE_WEIGHTED, 
    exposure_mode: ExposureModeEnum = ExposureModeEnum.NORMAL,
    constraint_mode: ConstraintModeEnum = ConstraintModeEnum.NORMAL,
    analogue_gain: int = 0, 
    exposure_time: int = 0, 
    wait: bool = False
) -> bool:
    """Set the camera exposure controls.

    If the metering mode is set to 'MeteringModeEnum.MANUAL', then use the 'analogue_gain' and 
    'exposure_time' parameters if they are non-zero. If they are zero, don't change them.

    If 'wait' is True, then monitor the 'AeLocked' attribute from the image metadata until
    it is True.
    """

    print(f"Setting exposure", flush=True)
    
    # set the camera exposure and wait for it to settle
    if metering_mode != MeteringModeEnum.MANUAL:
        camera.set_controls({
            'AeEnable': True,
            'AeMeteringMode': _metering_modes[metering_mode],
            'AeExposureMode': _exposure_modes[exposure_mode],
            'AeConstraintMode': _constraint_modes[constraint_mode]
        })
    
    else:
        mdata = camera.capture_metadata()
        if analogue_gain <= 0:
            analogue_gain = mdata['AnalogueGain']
        if exposure_time <= 0:
            exposure_time = mdata['ExposureTime']

        camera.set_controls({
            'AeEnable': False,
            'AnalogueGain': analogue_gain,
            'ExposureTime': exposure_time
        })
    
    if wait:
        # AeLocked seems to be updated for both auto and manual. And it can flip from
        # False to True to False while settling so wait for three in a row.
        count = 0
        while count < 3:
            mdata = camera.capture_metadata()
            if mdata['AeLocked'] == True:
                count += 1
            else:
                count = 0
            time.sleep(0.1)

    return True

