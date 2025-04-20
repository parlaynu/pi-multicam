import numpy as np
import camkit.ops.imaging as imaging

import pytest


@pytest.mark.parametrize('width,height', [(640,480), (720,640)])
def test_ImagesAreResized(Images, width, height):
    pipe = imaging.resize(Images, width=width, height=height)
    
    for item in pipe:
        img = item['main']['image']
        
        assert img.shape == (height, width, img.shape[2])
        assert img.dtype == np.uint8


@pytest.mark.parametrize('factor', [(0.25), (0.33333333), (0.5), (0.666666667), (1.0)])
def test_ImagesAreScaled(Images, factor):
    pipe = imaging.scale(Images, factor_width=factor)
    
    for item in pipe:
        img = item['main']['image']
        orig_size = item['main']['orig_size']
        shape = (round(orig_size[1]*factor), round(orig_size[0]*factor), orig_size[2])
        
        assert img.shape == shape
        assert img.dtype == np.uint8


