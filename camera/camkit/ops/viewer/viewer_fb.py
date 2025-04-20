import io

import numpy as np
from PIL import Image

from .framebuffer import FrameBuffer


def viewer_fb(pipe, *, image_key="main.image", fb_device="/dev/fb0"):

    print("Building camkit.ops.network.viewer")
    print(f"- image key: {image_key}")
    print(f"- fb device: {fb_device}")
    
    fb = FrameBuffer(fb_device)
    assert fb.bits_per_pixel() == 24
    fb.close()

    def gen():
        
        image_keys = image_key.split(".")
        
        with FrameBuffer(fb_device) as fb:
            fb_array = fb.array()
            fb_array[...] = 0
    
            fb_rows, fb_cols, _ = fb_array.shape

            for item in pipe:
                # display the image
                image = item
                for key in image_keys:
                    image = image[key]
            
                im_rows, im_cols, _ = image.shape
            
                if fb_rows >= im_rows:
                    fb_row_i = (fb_rows - im_rows) // 2
                    fb_row_o = fb_row_i + im_rows
                    im_row_i = 0
                    im_row_o = im_rows
                else:
                    fb_row_i = 0
                    fb_row_o = fb_rows
                    im_row_i = (im_rows - fb_rows) // 2
                    im_row_o = im_row_i + fb_rows
            
                if fb_cols >= im_cols:
                    fb_col_i = (fb_cols - im_cols) // 2
                    fb_col_o = fb_col_i + im_cols
                    im_col_i = 0
                    im_col_o = im_cols
                else:
                    fb_col_i = 0
                    fb_col_o = fb_cols
                    im_col_i = (im_cols - fb_cols) // 2
                    im_col_o = im_col_i + fb_cols
                
                fb_array[fb_row_i:fb_row_o, fb_col_i:fb_col_o, :] = image[im_row_i:im_row_o, im_col_i:im_col_o, :]

            # pass it on
            yield item

    return gen()
