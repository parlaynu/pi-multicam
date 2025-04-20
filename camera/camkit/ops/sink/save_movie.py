from typing import Iterable, Generator
import os
import shutil
import cv2


image_formats = { 
    'RGB888', 
    'BGR888'
}


def save_movie(
    pipe: Iterable[dict], 
    outdir: str, 
    *, 
    movie_fps: int = 2,
    max_width: int = 1280,
    max_height: int = 720,
    images_per_movie: int = 100, 
    image_file_format: str = 'jpg', 
    image_key: str = 'main.image', 
    format_key: str = 'main.format',
    cleanup: bool = True
) -> Generator[dict, None, None] :
    """Saves images as a movie file.

    The images are first cached to local disk, and when there are 'images_per_movie' 
    available, the movie file is created.
    """

    print("Building camkit.ops.sink.save_movie")
    print(f"- outdir: {outdir}")
    print(f"- movie_fps: {movie_fps}")
    print(f"- max_width: {max_width}")
    print(f"- max_height: {max_height}")
    print(f"- images_per_movie: {images_per_movie}")
    print(f"- image_file_format: {image_file_format}")
    print(f"- image_key: {image_key}")
    print(f"- format_key: {format_key}")
    print(f"- cleanup: {cleanup}")
    
    os.makedirs(outdir, exist_ok=True)

    image_keys = image_key.split('.')
    format_keys = format_key.split('.')
    
    def gen():
        movie_idx = 0
        movie_count = 0
        movie_cache = os.path.join(outdir, f"cache-{movie_idx:03d}")
        os.makedirs(movie_cache, exist_ok=True)

        for items in pipe:
            idx = item['idx']
    
            image = item
            for key in image_keys:
                image = image[key]
            image_format = item
            for key in format_keys:
                image_format = image_format[key]
    
            assert image_format in image_formats
        
            # make sure the image channels are in the native OpenCV order
            if image_format != 'RGB888':
                image = cv2.cvtColor(image, cv2.RGB2BGR)

            # check the image size is within limits
            height, width, _ = image.shape
            if width > max_width:
                height = int(max_width/width * height)
                width = max_width
            if height > max_height:
                width = int(max_height/height * width)
                height = max_height
        
            if height != image.shape[0] or width != image.shape[1]:
                image = cv2.resize(image, (width, height))

            img_path = os.path.join(movie_cache, f"img-{idx:04d}-rgb.{image_file_format}")
        
            print(f"Caching {img_path}", flush=True)
            cv2.imwrite(img_path, image)

            yield item
        
            movie_count += 1
            if movie_count >= images_per_movie:
                _make_movie(movie_cache, movie_idx, movie_fps, image_file_format, cleanup)
                movie_idx += 1
                movie_count = 0
                movie_cache = os.path.join(outdir, f"cache-{movie_idx:03d}")
                os.makedirs(movie_cache, exist_ok=True)
    
        if movie_count > 0:
            _make_movie(movie_cache, movie_idx, movie_fps, image_file_format, cleanup)
            
    return gen()


def _make_movie(
    cache_dir: str, 
    movie_idx: int, 
    movie_fps: int, 
    image_file_format: str, 
    cleanup: bool
) -> None:

    image_extension = image_file_format
    if not image_extension.startswith('.'):
        image_extension = '.' + image_extension
    
    outdir = os.path.dirname(cache_dir)
    movie_name = f"movie-{movie_idx:03d}.mov"
    movie_path = os.path.join(outdir, movie_name)

    print(f"Making movie {movie_path}")
    
    fourcc = cv2.VideoWriter.fourcc('a','v','c','1')
    vw = None
    
    for fname in sorted(os.listdir(cache_dir)):
        if not fname.endswith(image_extension):
            print(f"skipping {fname}")
            continue
        
        fpath = os.path.join(cache_dir, fname)
        image = cv2.imread(fpath)
        
        # don't know the image size until we load the first one
        if vw is None:
            height, width, _ = image.shape
            vw = cv2.VideoWriter(movie_path, fourcc, movie_fps, (width, height))
        
        vw.write(image)
    
    vw.release()

    if cleanup:
        print(f"Removing {cache_dir}")
        shutil.rmtree(cache_dir)

