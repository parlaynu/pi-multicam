from typing import Iterable, Generator


def chain(
    pipe1: Iterable[dict], 
    name1: str, 
    pipe2: Iterable[dict], 
    name2: str
) -> Generator[dict, None, None]:
    """Chains two generators together - see itertools.chain."""

    print("Building camkit.ops.utils.chain")
    print(f"- name1: {name1}")
    print(f"- name2: {name2}")
    
    def gen():
        for item in pipe1:
            item['name'] = name1
            yield item
        for item in pipe2:
            item['name'] = name2
            yield item

    return gen()



