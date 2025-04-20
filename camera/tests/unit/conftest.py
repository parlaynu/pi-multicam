import numpy as np
import pytest


@pytest.fixture(params=[(1024, 768, 3), (1920, 1080, 3)])
def Images(request):
    shape = (request.param[1], request.param[0], request.param[2])
    items = []
    for i in range(4):
        items.append(
            {
                'id': i,
                'main': {
                    'image': np.random.randint(0, 255, shape, np.uint8),
                    'orig_size': request.param
                }
            }
        )
    return items

