import os
os.environ['LIBCAMERA_LOG_LEVELS'] = "*:ERROR"

from itertools import count
import time

from picamera2 import Picamera2, Preview
from libcamera import Transform, ColorSpace, Rectangle, controls


def Camera(
    camera_id: int, 
    mode: int, 
    *, 
    main_format: str = 'RGB888', # NOTE: the OpenCV format
    vflip: bool = False, 
    hflip: bool = False, 
    max_fps: float = 0.0, 
    initial_controls: dict = {},
    tuning_file: str = None,
    preview: bool = False, 
    preview_crop: bool = False,
    preview_crop_offsets: list = None,
    preview_device: str = "/dev/fb0",
) -> Picamera2:
    """Build a Picamera2 object and apply initial configuration and controls.

    Parameters
    ----------
    camera_id : int
        The id of the camera on the system to use. Generally set to '0', but on Pi5 can also be '1'.
    mode : int
        The sensor mode to use. Available options depend on the camera in use.
    main_format: str, optional
        The format for images from the main stream. Despite the naming, the 'RGB888' format creates
        images in the OpenCV BGR format.
    vflip : bool, optional
        Apply vertical flip to the image.
    hflip: bool, optional
        Apply a horizontal flip to the image.
    preview: bool, optional
        Preview the image on a DRM display.
    max_fps : float, optional
        Sets the maximum frames per second to capture/
    initial_controls : dict, optional
        Set additional controls on the camera. There are a lot of available controls and they can
        be found in the Picamera2 official documentation.
    """

    # check for tuning file override
    tuning = None if tuning_file is None else Picamera2.load_tuning_file(tuning_file)

    # create the camera object
    cam = Picamera2(camera_id, tuning=tuning)

    # the sensor format information
    sensor_size = cam.camera_properties['PixelArraySize']
    sensor_mode = cam.sensor_modes[mode]
    mode_format = sensor_mode['unpacked']
    mode_size = sensor_mode['size']
    mode_crop = sensor_mode['crop_limits']
    mode_bit_depth = sensor_mode['bit_depth']
    
    # keep track of the configured mode on the object
    cam.configured_mode = sensor_mode

    # the base camera configuration
    kwargs = {
        'buffer_count': 3,
        'colour_space': ColorSpace.Sycc(),
        'main': {
            'size': mode_size,
            'format': main_format
        },
        'raw': {
            'size': mode_size,
            'format': str(mode_format)
        },
        'queue': False
    }

    # some older versions of the library don't support 'sensor'. if it's in
    #   the default configuration, it's ok to include it
    if hasattr(cam.still_configuration, 'sensor'):
        kwargs['sensor'] = {
            'output_size': mode_size,
            'bit_depth': mode_bit_depth
        }

    # if preview is requested, configure the lores stream for display
    if preview:
        _clear_screen(preview_device)
        
        # print("before")
        # print(f" sensor: {sensor_size}")
        # print(f"   crop: {mode_crop}")
        # print(f"   size: {mode_size}")
        
        mode_crop = _calc_scaler_crop(sensor_size, mode_crop, mode_size) if preview_crop else list(mode_crop)
        if preview_crop_offsets is not None:
            mode_crop[0] = mode_crop[0] + preview_crop_offsets[0]
            mode_crop[1] = mode_crop[1] + preview_crop_offsets[1]

        preview_size = _calc_preview_size(sensor_size, mode_crop, mode_size)

        # print("after")
        # print(f"  crop: {mode_crop}")
        # print(f"  size: {preview_size}")

        initial_controls = initial_controls.copy()
        initial_controls.update({
            'ScalerCrop': mode_crop
        })

        kwargs['lores'] = {
            'size': preview_size
        }
        kwargs['display'] = 'lores'

    # configure transforms
    if vflip or hflip:
        kwargs['transform'] = Transform(vflip=vflip, hflip=hflip)

    # set noise recudtion control
    kwargs['controls'] = {
        'NoiseReductionMode': controls.draft.NoiseReductionModeEnum.HighQuality
    }

    # create the full configuration
    config = cam.create_still_configuration(**kwargs)
    cam.align_configuration(config)
    
    # apply the configuration
    cam.configure(config)        

    # start the camera
    if preview:
        x = (1920 - preview_size[0]) // 2
        y = (1080 - preview_size[1]) // 2
        cam.start_preview(Preview.DRM, x=x, y=y, width=preview_size[0], height=preview_size[1])
    cam.start()

    # apply any additional controls to the camera
    ctrls = initial_controls.copy()
    if max_fps > 0.0:
        # the min frame duration in microseconds
        min_frameduration = int(1000000.0/max_fps)
        
        minfd, maxfd, _ = cam.camera_controls['FrameDurationLimits']
        minfd = int(min(max(minfd, min_frameduration), maxfd))
        ctrls.update({
            'FrameDurationLimits': (minfd, maxfd)
        })
    cam.set_controls(ctrls)
    
    return cam


def _clear_screen(fb_device):
    # write zeros to the device until the end is reached
    #   ...and a write exception is thrown
    zeros = bytearray(5000000)
    with open(fb_device, "wb") as fd:
        try:
            for i in count():
                fd.write(zeros)
        except Exception as e:
            pass


def _calc_scaler_crop(sensor_size, mode_crop, mode_size):

    if _size_fits_on_screen(mode_size):
        return list(mode_crop)
    
    sensor_w, sensor_h = sensor_size
    crop_x, crop_y, crop_w, crop_h = mode_crop
    size_w, size_h = mode_size
    
    hd_aspect = 1920.0/1080.0
    crop_aspect = crop_w/crop_h
    
    if crop_aspect < hd_aspect:
        # taller than HD
        crop_h = crop_w / min(1920, size_w) * 1080
        crop_y = (sensor_h - crop_h)/2
        
    elif crop_aspect > hd_aspect:
        # wider than HD
        crop_w = crop_h / min(1080, size_h) * 1920
        crop_x = (sensor_w - crop_w)/2

    return [round(v) for v in [crop_x, crop_y, crop_w, crop_h]]


def _calc_preview_size(sensor_size, mode_crop, mode_size):

    if _size_fits_on_screen(mode_size):
        return mode_size
    
    *_, crop_w, crop_h = mode_crop
    
    mode_scale = min(1920/crop_w, 1080/crop_h)
    
    return [round(crop_w*mode_scale), round(crop_h*mode_scale)]


def _size_fits_on_screen(mode_size):
    mode_w, mode_h = mode_size
    return mode_w <= 1920 and mode_h <= 1080

