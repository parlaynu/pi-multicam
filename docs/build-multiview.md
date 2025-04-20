# MultiView Application

This application is a C++ application that uses [Qt6/Qml6](https://doc.qt.io/qt-6.7/qmltypes.html) 
for the user interface. It's a bit more involved to get going than the python based camera toolkit
but hopefully the instructions are easy to follow.

There is documentation below for building and running on a RaspberryPi. I usually run the viewer on my
Mac laptop, and it will also build and run on Windows. I don't yet have build instructions for these
systems, but will add them as I get time.

## Installation - RaspberryPi

These build instructions assume a RaspberryPi running the `bookworm` version of the operating system. 
The  RaspberryPi website has good 
[documentation](https://www.raspberrypi.com/documentation/computers/getting-started.html)
to get you going.

### System Packages

First install the system packages for the necessary build tools and the Qt/Qml software:

    $ sudo apt install cmake

    $ sudo apt install qt6-declarative-dev qt6-multimedia-dev qt6-wayland \
                qml6-module-qtquick qml6-module-qtquick-window \
                qml6-module-qtquick-layouts qml6-module-qtmultimedia \
                qml6-module-qtqml qml6-module-qtqml-workerscript \
                qml-qt6

    $ sudo apt install libopencv-dev

### Rust

The Zenoh library is written in rust and you need the [Rust](https://www.rust-lang.org/tools/install)
language toolchain installed.

You can install with this single command:

    $ curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

### Zenoh Libraries

The Zenoh libraries needed are not available as installable packages and you need to clone
the source code and build locally.

[Zenoh-c](https://github.com/eclipse-zenoh/zenoh-c)

    $ git clone https://github.com/eclipse-zenoh/zenoh-c.git
    $ cd zenoh-c
    $ git checkout 1.3.3
    $ cmake -S . -B build
    $ cmake --build build --config Release
    $ sudo cmake --install build

[Zenoh-cpp](https://github.com/eclipse-zenoh/zenoh-cpp)

    $ git clone https://github.com/eclipse-zenoh/zenoh-cpp.git
    $ cd zenoh-cpp
    $ git checkout 1.3.3
    $ cmake -S . -B build
    $ sudo cmake --install build

### Build Multiview

To build the application, run these commands:

    $ cd multiview
    $ cmake -S . -B build
    $ cmake --build build

At the end of this, you will have a `multiview` application in the `build` directory.

## Quickstart

You run `multiview` from the command line and pass it as many Zenoh keys (up to 9) as you want to 
view. For example, to view the feed from two cameras that are running the camera software, you 
could run this:

    $ ./multiview/build/multiview home/pi-cam01/image home/pi-cam02/image

This assumes that your two RaspberryPi camera servers are called `pi-cam01` and `pi-cam02`.



