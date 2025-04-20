"""Discover all connected cameras and print all information about them."""
import os
os.environ['LIBCAMERA_LOG_LEVELS'] = "*:ERROR"

import argparse
from picamera2 import Picamera2


def print_dict(data):
    maxk = max([len(k) for k in data.keys()])
    for k in sorted(data.keys()):
        v = data[k]
        print(f"    {k:>{maxk}}: {v}")


def camera_info(cam_id):
    
    picam2 = Picamera2(cam_id)
    
    # collect all the camera information
    cam_properties = picam2.camera_properties
    cam_controls = picam2.camera_controls

    sensor_modes = []
    for sensor_mode in picam2.sensor_modes:
        sensor_modes.append(sensor_mode)
    
    kwargs = {}
    if hasattr(picam2.still_configuration, 'sensor'):    
        kwargs['sensor'] = {
            'output_size': sensor_modes[2]['size'],
            'bit_depth': sensor_modes[2]['bit_depth']
        }

    still_cfg = picam2.create_still_configuration(**kwargs)
    picam2.align_configuration(still_cfg)
    picam2.configure(still_cfg)

    cam_properties = picam2.camera_properties.copy()
    cam_controls = picam2.camera_controls.copy()

    preview_cfg = picam2.create_preview_configuration()
    picam2.align_configuration(preview_cfg)

    video_cfg = picam2.create_video_configuration()
    picam2.align_configuration(video_cfg)


    # display the information
    print()
    
    print("  Properties:")
    print_dict(cam_properties)
    print()

    print("  Controls:")
    print_dict(cam_controls)
    print()

    for idx, sensor_mode in enumerate(sensor_modes):
        print(f"  Sensor Mode {idx}:")
        print_dict(sensor_mode)
        print()
    
    print("  Still Configuration:")
    print_dict(still_cfg)
    print()

    print("  Preview Configuration:")
    print_dict(preview_cfg)
    print()
    
    print("  Video Configuration:")
    print_dict(video_cfg)
    print()
    
    print("  Main Stream Configuration:")
    print_dict(picam2.stream_configuration("main"))
    print()

    
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--camera', help='the camera to query', type=int, default=-1)
    args = parser.parse_args()
    
    if args.camera != -1:
        print(f"Camera {args.camera}")
        camera_info(args.camera)
        
    else:
        cameras = Picamera2.global_camera_info()
        for idx, camera in enumerate(cameras):
            cam_id = camera.get('Num', idx)
        
            print("------------------------------------------------")
            print(f"Camera {cam_id}")
            camera_info(cam_id)    



