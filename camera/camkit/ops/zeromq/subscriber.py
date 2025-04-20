import io
import zmq

import numpy as np
from PIL import Image


def subscriber(publish_url):

    print("Building camkit.ops.network.subscriber")
    print(f"- publish url: {publish_url}")

    context = zmq.Context()
    sub_sock = context.socket(zmq.SUB)
    sub_sock.set_hwm(2)

    def gen():
        
        sub_sock.connect(publish_url)
        sub_sock.setsockopt(zmq.SUBSCRIBE, b'')
        
        while True:
            mask = sub_sock.poll(100)
            if mask != 0:
                # receive the multipart message
                idx, data = sub_sock.recv_multipart()
                
                # decode and display the image
                jpeg = io.BytesIO(data)
                image = np.array(Image.open(jpeg))
                
                # construct an item from the information available
                item = {
                    'idx': idx,
                    'main': {
                        'image': image
                    }
                }
                
                # pass it on
                yield item

    return gen()

