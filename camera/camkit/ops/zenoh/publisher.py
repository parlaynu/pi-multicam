from typing import Iterable
import io
import json
from pprint import pprint

import zenoh

import camkit.ops as ops


def publisher(
    pipe: Iterable[dict],
    zenoh_key: str,
    *, 
    data_key: str = "main.jpg",
    local_only: bool = False,
    ipv4_only: bool = False,
    interface: str = "wlan0"
) -> None:

    print("Building camkit.ops.zenoh.publisher")
    print(f"- zenoh key: {zenoh_key}")

    data_keys = data_key.split('.')

    cfg = zenoh.Config()
    cfg.insert_json5('mode', json.dumps('peer'))
    # cfg.insert_json5('scouting/multicast/enabled', json.dumps(True))
    # cfg.insert_json5('scouting/multicast/address', json.dumps('224.0.0.224:7446'))
    # cfg.insert_json5('scouting/multicast/interface', json.dumps(interface))
    # cfg.insert_json5('scouting/multicast/autoconnect', json.dumps({ 'router': [], 'peer': ['router', 'peer'] }))
    # cfg.insert_json5('scouting/multicast, jsonlisten', 'true')
    # cfg.insert_json5('scouting/multicast/ttl', '1')

    cfg.insert_json5('transport/link/tx/queue/size/data', json.dumps(16))

    if local_only and ipv4_only:
        cfg.insert_json5('listen/endpoints', json.dumps({'peer': ['tcp/127.0.0.1:0']}))
    elif ipv4_only:
        cfg.insert_json5('listen/endpoints', json.dumps({'peer': ['tcp/0.0.0.0:0']}))
    elif local_only:
        cfg.insert_json5('listen/endpoints', json.dumps({'peer': ['tcp/[::1]:0']}))

    def gen():
        zenoh.init_log_from_env_or("info")
        session = zenoh.open(cfg)
        pub = session.declare_publisher(
            zenoh_key, 
            express=True,
            congestion_control=zenoh.CongestionControl.BLOCK,
            reliability=zenoh.Reliability.RELIABLE
        )

        for item in pipe:
            idx = item['idx']
            
            # get the image data
            data = ops.get_nested_value(item, data_keys)
            print(f"{idx:04d}: putting image: {len(data)} bytes")

            # publish the data
            # pub.put(f"{idx:04d}")
            if isinstance(data, memoryview):
                pub.put(data.tobytes(), encoding=f"image/{data_keys[-1]}")
            else:
                pub.put(data, encoding=f"image/{data_keys[-1]}")
            
            yield item

    return gen()

