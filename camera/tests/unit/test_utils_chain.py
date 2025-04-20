import itertools
import pytest
import camkit.ops.utils as utils


def test_SequencesAreChained():
    
    seq1 = ['a', 'b', 'c']
    seq2 = ['d', 'e', 'f', 'g']
    
    def gen1():
        for idx, value in enumerate(seq1):
            item = {
                'idx': idx,
                'value': value
            }
            yield item
    
    def gen2():
        for idx, value in enumerate(seq2):
            item = {
                'idx': idx,
                'value': value
            }
            yield item

    pipe1 = gen1()
    pipe2 = gen2()
    
    pipe = utils.chain(pipe1, 'pipe1', pipe2, 'pipe2')
    
    for item, value in zip(pipe, itertools.chain(seq1, seq2)):
        assert item['value'] == value

