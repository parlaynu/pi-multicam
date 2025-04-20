import fcntl
import ctypes
from enum import IntEnum
import mmap
import numpy as np

# To set the framebuffer depth to 24bpp:
#   edit /boot/firmware/cmdline.txt and add this at the start:
#     video=HDMI-A-1:1920x1080M-24@60


class FrameBuffer:
    
    def __init__(self, device="/dev/fb0"):
        self.device = device
        
        self.fd = open(self.device, "r+b")
        self.mm = None
        self.np_array = None

        # load the screen information - exception raised on error
        self.fix_screeninfo = fb_fix_screeninfo()
        fcntl.ioctl(self.fd, FbIoctl.FBIOGET_FSCREENINFO, self.fix_screeninfo)
        
        self.var_screeninfo = fb_var_screeninfo()
        fcntl.ioctl(self.fd, FbIoctl.FBIOGET_VSCREENINFO, self.var_screeninfo)

    def __enter__(self):
        return self
    
    def __exit__(self, *exc_details):
        if self.fd is not None:
            self.close()
    
    def close(self):
        # close the mapped memory if it's been mapped
        if self.mm is not None:
            self.np_array = None
            self.mm.close()
            self.mm = None
        
        # reset the framebuffer
        fcntl.ioctl(self.fd, FbIoctl.FBIOPUT_VSCREENINFO, self.var_screeninfo)
        
        # finally close
        self.fd.close()
        self.fd = None
    
    def resolution(self):
        return (self.var_screeninfo.xres, self.var_screeninfo.yres)

    def bits_per_pixel(self):
        return self.var_screeninfo.bits_per_pixel
    
    def channels(self):
        cinfo = {
            "red": (self.var_screeninfo.red.offset, self.var_screeninfo.red.length),
            "green": (self.var_screeninfo.green.offset, self.var_screeninfo.green.length),
            "blue": (self.var_screeninfo.blue.offset, self.var_screeninfo.blue.length),
            "alpha": (self.var_screeninfo.transp.offset, self.var_screeninfo.transp.length),
        }
        return cinfo
    
    def array(self) -> np.ndarray:
        # make sure we're memory mapped
        if self.mm is None:
            self.mm = mmap.mmap(
                self.fd.fileno(), 
                offset=self.fix_screeninfo.smem_start, 
                length=self.fix_screeninfo.smem_len, 
                flags=mmap.MAP_SHARED, 
                prot=mmap.PROT_READ|mmap.PROT_WRITE
            )
            
            depth = self.var_screeninfo.bits_per_pixel // 8
            self.np_array = np.ndarray(
                shape=(self.var_screeninfo.yres, self.var_screeninfo.xres, depth),
                dtype=np.uint8,
                buffer=self.mm,
            )
        
        return self.np_array


class FbIoctl(IntEnum):
    FBIOGET_VSCREENINFO = 0x4600
    FBIOPUT_VSCREENINFO = 0x4601
    FBIOGET_FSCREENINFO = 0x4602


class FbType(IntEnum):
    PACKED_PIXELS      = 0  # packed pixels
    PLANES             = 1  # non-interleaved planes
    INTERLEAVED_PLANES = 2  # interleaved planes
    TEXT               = 3  # text/attributes
    VGA_PLANES         = 4  # EGA/VGA planes
    FOURCC             = 5  # type identified by a V4L2 FOURCC


class FbVisual(IntEnum):
    MONO01             = 0  # monochr. 1=black 0=white
    MONO10             = 1  # monochr. 1=white 0=black
    TRUECOLOR          = 2  # true color
    PSEUDOCOLOR        = 3  # pseudo color (like atari)
    DIRECTCOLOR        = 4  # direct color
    STATIC_PSEUDOCOLOR = 5  # pseudo color readonly
    FOURCC             = 6  # visual identified by a V4L2 FOURCC


class fb_fix_screeninfo(ctypes.Structure):
    _fields_ = [
        ('id', ctypes.c_char*16),         # identification string eg "TT Builtin"
        ('smem_start', ctypes.c_ulong),     # start of frame buffer mem (physical address)
        ('smem_len', ctypes.c_uint32),      # length of frame buffer mem
        ('type', ctypes.c_uint32),          # see FB_TYPE_*
        ('type_aux', ctypes.c_uint32),      # interleave for interleaved Planes
        ('visual', ctypes.c_uint32),        # see FB_VISUAL_*
        ('xpanstep', ctypes.c_uint16),      # zero if no hardware panning
        ('ypanstep', ctypes.c_uint16),      # zero if no hardware panning
        ('ywrapstep', ctypes.c_uint16),     # zero if no hardware ywrap
        ('line_length', ctypes.c_uint32),   # length of a line in bytes
        ('mmio_start', ctypes.c_ulong),     # start of Memory Mapped I/O (physical address)
        ('mmio_len', ctypes.c_uint32),      # length of Memory Mapped I/O
        ('accel', ctypes.c_uint32),         # indicate to driver which specific chip/card we have
        ('capabilities', ctypes.c_uint16),  # see FB_CAP_*
        ('reserved', ctypes.c_uint16*2),    # reserved for future compatibility
    ]

    def dump(self):
        print(f"id: {self.id}")
        print(f"  smem_start: {self.smem_start}")
        print(f"    smem_len: {self.smem_len}")
        print(f"        type: {self.type}")
        print(f"    type_aux: {self.type_aux}")
        print(f"      visual: {self.visual}")
        print(f"    xpanstep: {self.xpanstep}")
        print(f"    ypanstep: {self.ypanstep}")
        print(f"   ywrapstep: {self.ywrapstep}")
        print(f" line_length: {self.line_length}")
        print(f"  mmio_start: {self.mmio_start}")
        print(f"    mmio_len: {self.mmio_len}")
        print(f"       accel: {self.accel}")
        print(f"capabilities: {self.capabilities}")


class fb_bitfield(ctypes.Structure):
    _fields_ = [
        ('offset', ctypes.c_uint32),     # beginning of bitfield
        ('length', ctypes.c_uint32),     # length of bitfield
        ('msb_right', ctypes.c_uint32),  # != 0 : most significant bit is right
    ]
    
class fb_var_screeninfo(ctypes.Structure):
    _fields_ = [
        ('xres', ctypes.c_uint32),            # visible resolution
        ('yres', ctypes.c_uint32),
        ('xres_virtual', ctypes.c_uint32),    # virtual resolution
        ('yres_virtual', ctypes.c_uint32),
        ('xoffset', ctypes.c_uint32),         # offset from virtual to visual resolution
        ('yoffset', ctypes.c_uint32),
        ('bits_per_pixel', ctypes.c_uint32),  # bits per pixel
        ('grayscale', ctypes.c_uint32),       # 0=color, 1=grayscale, >1=FOURCC
        ('red', fb_bitfield),                 # bitfield in fb mem if true color, else only length is significant
        ('green', fb_bitfield),
        ('blue', fb_bitfield),
        ('transp', fb_bitfield),              # transparency
        ('nonstd', ctypes.c_uint32),          # != 0 Non standard pixel format
        ('activate', ctypes.c_uint32),        # see FB_ACTIVATE_*
        ('height', ctypes.c_uint32),          # height of picture in mm
        ('width', ctypes.c_uint32),           # width of picture in mm
        ('accel_flags', ctypes.c_uint32),     # obsolete; see fb_info.flags
        
        # timing: all values in pixclocks, except pixclock (of course)
        ('pixclock', ctypes.c_uint32),        # pixel clock in ps (pico seconds)
        ('left_margin', ctypes.c_uint32),     # time from sync to picture
        ('right_margin', ctypes.c_uint32),    # time from picture to sync
        ('upper_margin', ctypes.c_uint32),    # time from sync to picture
        ('lower_margin', ctypes.c_uint32),
        ('hsync_len', ctypes.c_uint32),       # length of horizontal sync
        ('vsync_len', ctypes.c_uint32),       # length of vertical sync
        ('sync', ctypes.c_uint32),            # see FB_SYNC_*
        ('vmode', ctypes.c_uint32),           # see FB_VMODE_*
        ('rotate', ctypes.c_uint32),          # angle we rotate counter clockwise
        ('colorspace', ctypes.c_uint32),      # colorspace for FOURCC-based modes
        ('reserved', ctypes.c_uint32*4),
    ]
    
    def dump(self):
        print(f"xres: {self.xres}")
        print(f"yres: {self.yres}")
        print(f"xres_virtual: {self.xres_virtual}")
        print(f"yres_virtual: {self.yres_virtual}")
        print(f"xoffset: {self.xoffset}")
        print(f"yoffset: {self.yoffset}")
        print(f"bits_per_pixel: {self.bits_per_pixel}")
        print(f"grayscale: {self.grayscale}")
        print(f"red: {self.red}")
        print(f"green: {self.green}")
        print(f"blue: {self.blue}")
        print(f"transp: {self.transp}")


# class fb_fillrect(ctypes.Structure):
#     _fields_ = [
#         ("dx", ctypes.c_uint32),   # screen-relative
#         ("dy", ctypes.c_uint32),
#         ("width", ctypes.c_uint32),
#         ("height", ctypes.c_uint32),
#         ("color", ctypes.c_uint32),
#         ("rop", ctypes.c_uint32),
#     ]
#
#
# class fb_cmap(ctypes.Structure):
#     _fields_ = [
#         ("start", ctypes.c_uint32),     # first entry
#         ("len", ctypes.c_uint32),       # number of entries
#         ("red", ctypes.c_uint16_p),     # red values
#         ("green", ctypes.c_uint16_p),
#         ("blue", ctypes.c_uint16_p),
#         ("transp", ctypes.c_uint16_p),  # transparency
#     ]
#
#
# class fb_image(ctypes.Structure):
#     _fields_ = [
#         ("dx", ctypes.c_uint32),        # where to place image
#         ("dy", ctypes.c_uint32),
#         ("width", ctypes.c_uint32),     # size of image
#         ("height", ctypes.c_uint32),
#         ("fg_color", ctypes.c_uint32),  # only used when a mono bitmap
#         ("bg_color", ctypes.c_uint32),
#         ("depth", ctypes.c_uint8),      # depth of the image
#         ("data", ctypes.c_char_p),      # pointer to image data
#         ("cmap", fb_cmap),              # colormap info
#     ]


def test():
    import time
    
    with FrameBuffer() as fb:
        print(f"{fb.resolution()} {fb.bits_per_pixel()}")
        print(f"{fb.channels()}")
        
        fb.fix_screeninfo.dump()
        fb.var_screeninfo.dump()
        
        arr = fb.array()
        arr[...] = 55
        
        time.sleep(10)


if __name__ == "__main__":
    test()

