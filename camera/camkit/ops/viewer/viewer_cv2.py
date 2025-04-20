import io
import cv2

import numpy as np
from PIL import Image


def viewer_cv2(pipe, *, image_key="main.image", fullscreen=False):

    print("Building camkit.ops.viewer.viewer_cv2")
    print(f"- image key: {image_key}")
    print(f"- fullscreen: {fullscreen}")

    if fullscreen == True:
        cv2.namedWindow("image", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("image",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)

    image_keys = image_key.split(".")

    def gen():
        
        for item in pipe:
            # display the image
            image = item
            for key in image_keys:
                image = image[key]
            cv2.imshow('image', image)
                
            # check for a quit key
            key = cv2.pollKey()
            if key == ord('q') or key == ord('x'):
                break

            # pass it on
            yield item

    return gen()

