from typing import Iterable, Generator
import os
import cv2
import numpy as np


bayer_codes = {
    'SBGGR10': cv2.COLOR_BayerRG2BGR,
    'SBGGR12': cv2.COLOR_BayerRG2BGR,
    'SBGGR16': cv2.COLOR_BayerRG2BGR,
    'SGRBG16': cv2.COLOR_BayerGB2BGR,
    'SGBRG16': cv2.COLOR_BayerGR2BGR,
    'SRGGB16': cv2.COLOR_BayerBG2BGR,
}

bayer_scale = {
    'SBGGR10': 65535.0/1023.0,
    'SBGGR12': 65535.0/4095.0,
    'SBGGR16': 1.0,
    'SGRBG16': 1.0,
    'SGBRG16': 1.0,
    'SRGGB16': 1.0,
}


def save_raw(
    pipe: Iterable[dict], 
    outdir: str, 
    *, 
    image_key: str = 'raw.image', 
    format_key: str = 'raw.format', 
    prefix: str = 'img'
) -> Generator[dict, None, None]:
    """Save raw images to disk in a demosaiced PNG file. 

    All formats are scaled up to reside in the top region of the 16bit word.

    The only processing that is done is to subtract the sensor black levels and to
    demosaic the image.
    """
    
    print("Building camkit.ops.sink.save_raw")
    print(f"- outdir: {outdir}")
    print(f"- image_key: {image_key}")
    print(f"- format_key: {format_key}")
    print(f"- prefix: {prefix}")
    
    os.makedirs(outdir, exist_ok=True)

    image_keys = image_key.split('.')
    format_keys = format_key.split('.')
    
    def gen():
        for items in pipe:
            idx = item['idx']
    
            image = item
            for key in image_keys:
                image = image[key]
            image_format = item
            for key in format_keys:
                image_format = image_format[key]

            # saving
            if name := item.get('name', None):
                img_path = os.path.join(outdir, f"{prefix}-{idx:04d}-{name}-raw.png")
            else:
                img_path = os.path.join(outdir, f"{prefix}-{idx:04d}-raw.png")

            print(f"Saving {img_path}")
            
            # scale the image up to the top part of the 16bit word
            image = image * bayer_scale[image_format]
            
            # subtract the sensor black levels
            black_level = item['metadata']['SensorBlackLevels'][0]
            image = np.maximum(image, black_level) - black_level
            
            # demosaic the image
            bayer_code = bayer_codes[image_format]
            image = cv2.demosaicing(image.astype(np.uint16), bayer_code)

            # save to disk
            cv2.imwrite(img_path, image)
    
            yield item

    return gen()


def save_raw8(
    pipe: Generator[dict, None, None], 
    outdir: str, 
    *, 
    image_key: str = 'raw.image', 
    format_key: str = 'raw.format', 
    prefix: str = 'img'
) -> Generator[dict, None, None]:
    """Save raw images to disk in an 8-bit PNG file. 

    Some very basic processing is done to subtract black levels, apply an sRGB-like gamma
    to the data and scale it to 0-255.
    """
    
    print("Building camkit.ops.sink.save_raw8")
    print(f"- outdir: {outdir}")
    print(f"- image_key: {image_key}")
    print(f"- format_key: {format_key}")
    print(f"- prefix: {prefix}")

    os.makedirs(outdir, exist_ok=True)

    image_keys = image_key.split('.')
    format_keys = format_key.split('.')
    
    scale = 255.0 / np.power(65535, 1.0/2.2)

    def gen():
        for items in pipe:
            if not isinstance(items, list):
                items = [items]
        
            for item in items:
                idx = item['idx']
                
                image = item
                for key in image_keys:
                    image = image[key]
                image_format = item
                for key in format_keys:
                    image_format = image_format[key]

                # saving
                if name := item.get('name', None):
                    img_path = os.path.join(outdir, f"{prefix}-{idx:04d}-{name}-raw8.png")
                else:
                    img_path = os.path.join(outdir, f"{prefix}-{idx:04d}-raw8.png")

                print(f"Saving {img_path}")

                # scale the image up to the top part of the 16bit word
                image = image * bayer_scale[image_format]

                # subtract the sensor black levels
                black_level = item['metadata']['SensorBlackLevels'][0]
                image = np.maximum(image, black_level) - black_level

                # demosaic the image
                bayer_code = bayer_codes[image_format]
                image = cv2.demosaicing(image.astype(np.uint16), bayer_code)

                # apply the gamma encoding and convert to 8bit range
                image = np.power(image, 1.0/2.2) * scale
                image = image.astype(np.uint8)

                # save the image
                cv2.imwrite(img_path, image)
        
                yield item

    return gen()

