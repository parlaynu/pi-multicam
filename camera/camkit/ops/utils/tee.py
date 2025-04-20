from typing import Iterable, Generator
import collections
import threading
import time


def tee(
    pipe: Iterable[dict], 
    *, 
    count: int, 
    threaded: bool = False
) -> Iterable[Generator[dict, None, None]]:
    """Splits the incoming pipe into multiple outputs which can then be processed in parallel.
    
    See itertools.tee for details.
    
    The parameter 'count' specifies how many outputs to generate.
    
    If working in a threaded environment, you can set 'threaded' to True to offer a stronger
    guarantee that the threads will behave in an orderly fashion.
    """
    
    print("Building camkit.ops.utils.tee")
    print(f"- count: {count}")

    barrier = threading.Barrier(count)
    lock = threading.Lock()
    deques = [collections.deque() for i in range(count)]

    def gen(mydeque):
        tid = threading.get_ident()
    
        while True:
            # using a barrier to ensure that all threads get a chance to
            # execute the code that follows before any one thread can 
            # loop through again.
            if threaded:
                barrier.wait()
            
            with lock:
                if len(mydeque) == 0:
                    try:
                        item = next(pipe)
                    except StopIteration:
                        return
                    
                    for d in deques:
                        d.append(item.copy())

            yield mydeque.popleft()

    return [gen(d) for d in deques]

