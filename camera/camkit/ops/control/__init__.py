"""Implements various controllers for the capture pipelines.

These are the first item in the pipeline and can control the pace and
timing of running the pipeline based on things like frame rates and 
maximum number of frames to capture.

There are also implementations that make use of flirc IR receivers
to trigger capturing of images.
"""
from .simple import simple

from .flirc import flirc
from .flirc_exit import flirc_exit

from .exceptions import FlircNotFoundError
