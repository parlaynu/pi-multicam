import numpy as np
import camkit.ops.imaging as imaging

import pytest


@pytest.mark.parametrize('factor', [(0.25), (0.33333333), (0.5), (0.666666667), (1.0)])
def test_ImagesAreCropped(Images, factor):
    pipe = imaging.centre_crop(Images, factor=factor)
    
    for item in pipe:
        img = item['main']['image']
        orig_size = item['main']['orig_size']
        
        new_shape = (round(orig_size[1]*factor), round(orig_size[0]*factor), orig_size[2])
        
        assert img.shape == new_shape
        assert img.dtype == np.uint8


