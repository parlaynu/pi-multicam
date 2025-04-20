import pytest
import camkit.ops.utils as utils


@pytest.mark.parametrize('limit', [(1), (5), (10), (20)])
def test_LimitIsEnforced(limit):
    
    seq = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    
    def gen():
        for idx, value in enumerate(seq):
            item = {
                'idx': idx,
                'value': value
            }
            yield item
    
    pipe = gen()
    pipe = utils.limit(pipe, max_frames=limit)
    
    for idx, item in enumerate(pipe):
        pass
    
    assert idx == min(len(seq), limit) - 1
    assert item['value'] == seq[idx]

