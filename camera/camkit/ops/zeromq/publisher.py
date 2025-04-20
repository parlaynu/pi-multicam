from typing import Iterable
import socket
import psutil
import re
import io

import zmq
from PIL import Image
import numpy as np


def publisher(
    pipe: Iterable[dict],
    *, 
    port: int = 8090,
    image_key: str = 'main.image', 
    image_format: str = 'jpeg',
    local_listen: bool = False
) -> None:

    print("Building camkit.ops.network.publisher")

    image_keys = image_key.split('.')
    
    if local_listen:
        pub_url = f"tcp://127.0.0.1:{port}"
    else:
        pub_url = f"tcp://0.0.0.0:{port}"
    
    all_urls = _connect_urls(pub_url)
    for u in all_urls:
        print(f"- listen url: {u}")

    context = zmq.Context()
    pub_sock = context.socket(zmq.PUB)
    pub_sock.set_hwm(2)
    pub_sock.bind(pub_url)
    
    def gen():
        for item in pipe:
            idx = item['idx']
            idx = f"{idx}".encode('utf-8')
            
            # get the image data
            image = item
            for key in image_keys:
                image = image[key]

            # means = np.mean(image, axis=(0,1))
            # print(means)

            # encode the image as a jpeg
            image = Image.fromarray(image)
            jpeg = io.BytesIO()
            image.save(jpeg, format=image_format, quality=95)
            jpeg.seek(0, io.SEEK_SET)
            
            # publish the jpeg data
            pub_sock.send_multipart([idx, jpeg.getvalue()], copy=False)
            
            yield item
    
    return gen()


def _connect_urls(listen_url):
    """Get all the URLs that can be used to connect to the listen URL."""

    # split the url
    tcp_re = re.compile("^tcp://(?P<address>.+?):(?P<port>\d+)$")
    mo = tcp_re.match(listen_url)
    if mo is None:
        raise ValueError(f"unable to parse {listen_url}")

    address = mo['address']
    port = mo['port']

    urls = []
    if address == "0.0.0.0":
        local_addresses = _local_ips()
        for address in local_addresses['ipv4']:
            urls.append(f'tcp://{address}:{port}')

    else:
        urls.append(url)

    return urls


def _local_ips():
    """Returns all the local IP addresses on the host."""
    
    ipv4s = []
    ipv6s = []
    
    interfaces = psutil.net_if_addrs()
    for interface, if_addresses in interfaces.items():
        for if_address in if_addresses:
            if if_address.family == socket.AF_INET:
                ipv4s.append(if_address.address)
            elif if_address.family == socket.AF_INET6:
                ipv6s.append(if_address.address)
    
    addresses = {
        'ipv4': ipv4s,
        'ipv6': ipv6s
    }

    return addresses


