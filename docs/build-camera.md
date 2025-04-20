# Camera Toolkit - Setup and Usage

This application is a toolkit for building custom camera capture tools for the RaspberryPi using a 
configuration file to compose capture and processing dataflow pipelines. I built it because I got tired of
writing very similar capture tools for slightly different situations.

To use this, you need to have a RaspberryPi with a camera installed with the OS setup and ready to use. The
RaspberryPi website has good [documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html)
to get you going.

## Setup

### Core Software

Install the core system packages:

    $ sudo apt install -y python3-pip python3-libcamera python3-picamera2 \
                python3-numpy python3-opencv python3-pil \
                python3-jinja2 python3-ruamel.yaml

Install the Eclipse Zenoh python package. This isn't available as a system package and needs to be 
installed using `pip`. I install it into the user installation area to keep separate from system packages.

    $ pip install --user --break-system-packages eclipse-zenoh==1.3.3

Don't be alarmed by the `--break-system-packages` flag, it won't hurt them in this case. It's due to
python's [PEP 668](https://peps.python.org/pep-0668/) being implemented in the lastest RaspberryPi OS.
Have a read if you're curious.

To run the unit tests, install the pytest package:

    $ sudo apt install -y python3-pytest

### Optional Software

There are a number of other operators that can be used to process images in the dataflow
pipeline. To use them, install the additional packages below.

To use the [ZeroMQ](https://zeromq.org/) operators:

    $ sudo apt install -y python3-zmq  python3-psutil

To use a [Flirc USB receiver](https://flirc.tv/products/flirc-usb-receiver?variant=43513067569384):

    $ sudo apt install -y python3-evdev

To use [AWS S3](https://aws.amazon.com/s3/) as an Image Source

    $ sudo apt install -y python3-boto3 awscli

## Quickstart

There are three console tools provided with the camera software as outlined in the table below:

| Tool       | Description                                                         |
| ---------- | ------------------------------------------------------------------- |
| pi-caminfo | prints information about the camera including modes and resolutions |
| ck-run     | runs the dataflow pipelines defined in the configuration files      |
| ck-config  | loads and expands a configuration template and prints to the output |

The main tool is `ck-run`. This loads a configuration template that defines a set of operations
configured in a dataflow pipeline, expands the template and builds the pipeline. It then
executes the pipeline. This process is explained in other documentation.

There are a number of configuration files defined in the [configs](../camera/configs) directory.
The main one used to work with `multiview` is `zenoh.yaml`. To run this config, from
the `root` of this repository, run this command:

    $ ./camera/ck-run camera/configs/zenoh/zenoh.yaml

This will build and run the dataflow pipeline defined in the configuration file. The final operator
in the pipeline creates a [zenoh publisher](https://zenoh.io/docs/getting-started/first-app/)
that publishes a stream of jpeg encoded images using the key `home/{{ hostname }}/image`. The 
template variable `{{ hostname }}` is expanded to be the hostname of the RaspberryPi your running on, 
with all domain components removed.

You can pass template variables to the runner on the command line. For example, if your 
RaspberryPi is attached to a monitor and you want to locally preview the images that are being
sent over the network, you can enable previewing like this:

    $ ./camera/ck-run camera/configs/zenoh/zenoh.yaml preview=true

There is nothing special about the `preview` keyword other than it is defined in the configuration
file, with a default value of `false`, and passing it on the command line like above overrides
the default value. There are a number of other template variables available which you can easily
see by browsing the [configuration file](../camera/configs/zenoh/zenoh.yaml).

There are quite a few configurations made and ready to use, most of which have nothing to do
with `multiview`. Have a [browse](../camera/configs).

