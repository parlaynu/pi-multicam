from typing import Iterable, Generator
import sys
import threading
import queue


def worker(
    pipe: Iterable[dict], 
    *, 
    qlen: int = 1
) -> Generator[dict, None, None]:
    """Creates a worker thread to call the upstream pipeline and yield results in the calling thread.

    Different parts of the pipeline can run in different threads. This is subject to the limitations
    of the python interpreter, but it can help in some situations, for example to separate IO and compute
    parts of the pipeline into different threads, or to run branched pipelines in parallel.
    """

    print("Building camkit.ops.utils.worker")
    print(f"- qlen: {qlen}")

    q = queue.Queue(maxsize=qlen)
    worker = Worker(pipe, q)
    worker.start()
    
    def gen():
        while True:
            item = q.get()
            if isinstance(item, Exception):
                raise item
            if item is None:
                break
            yield item
    
        worker.join()
    
    return gen()


class Worker(threading.Thread):
    def __init__(self, pipe, q):
        super().__init__(daemon=True)
        self.pipe = pipe
        self.queue = q
    
    def run(self):
        try:
            for item in self.pipe:
                self.queue.put(item)
            self.queue.put(None)
        except Exception as e:
            self.queue.put(e)