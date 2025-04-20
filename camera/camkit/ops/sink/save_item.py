from typing import Iterable, Generator
import os
import json
import numpy as np


def save_item(
    pipe: Iterable[dict], 
    outdir: str, 
    *, 
    prefix: str = 'img', 
    mdata_key: str = 'metadata'
) -> Generator[dict, None, None]:
    """Save image metadata to disk. Will generally have the same name as the image, but will be a json file.

    The files are saved to 'outdir' with a file name that starts with 'prefix'.

    The parameter 'mdata_key' is the dict item that has the metadata.
    """

    print("Building camkit.ops.sink.save_item")
    print(f"- outdir: {outdir}")
    print(f"- prefix: {prefix}")
    print(f"- mdata_key: {mdata_key}")
    
    os.makedirs(outdir, exist_ok=True)
    
    def gen():
        for items in pipe:
            idx = item['idx']
    
            local_item = item.copy()
    
            # clean the metadata
            metadata = local_item[mdata_key]
            for k in list(metadata.keys()):
                if k.endswith('StatsOutput'):
                    del metadata[k]
    
            # remove any images
            for kk, vv in local_item.items():
                if not isinstance(vv, dict):
                    continue
        
                local_item[kk] = vv = vv.copy()
                for k in list(vv.keys()):
                    v = vv[k]
                    if isinstance(v, np.ndarray):
                        del vv[k]
    
            # save the item
            if colour := item.get('colour', None):
                red, green, blue = colour['red'], colour['green'], colour['blue']
                item_path = os.path.join(outdir, f"{prefix}-{idx:04d}-r{red:03d}-g{green:03d}-b{blue:03d}.json")
            elif name := item.get('name', None):
                item_path = os.path.join(outdir, f"{prefix}-{idx:04d}-{name}.json")
            else:
                item_path = os.path.join(outdir, f"{prefix}-{idx:04d}.json")

            print(f"Saving {item_path}")

            with open(item_path, "w") as f:
                print(json.dumps(local_item, sort_keys=True, indent=2), file=f)
    
            yield item

    return gen()
