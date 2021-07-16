# HCRA Server

This is the server for HamClock Remote Access. It is a Python web app written
using Tornado.

On its own, the server is useless; it requires HamClock, available at
http://clearskyinstitute.com/ham/HamClock/ (installed on the same machine as
the HCRA server), and the HCRA client (see `../client`).

## Installation

The server itself does not need to be installed; it is simply run with
`python3 wss.py` in this directory. However, it does have some dependencies
(both Python packages and binaries).

### Python packages

    pip3 install -r requirements.txt

### Binaries

#### Ubuntu, Mint, possibly Debian, etc.

    sudo apt install $(cat ubuntu-pkgs.txt)

#### Other distros

Unfortunately, I only have Mint computers, so I can't help with other
distros.

You will need the following:

* ImageMagick 6
* X11 development headers
* `Xvfb`
* `xdotool`
* `xwd`

## Backends

The server can connect to HamClock in one of two ways; it can either use
HamClock's built-in port 8080 service, or it can use X11. The X11 method is
highly recommended when it can be used, because it does not occasionally
freeze when HamClock is on certain screens like the port 8080 backend does.

A variant on the X11 backend, called the SaaS backend, is also available. It
works the same way, except it starts HamClock on its own and stops it when
the user disconnects. This is intended for cloud/SaaS environments that may
run multiple HamClocks for different users.

### Port 8080

The Port 8080 backend just requires a running instance of 800x480 HamClock.

### X11

The X11 backend requires 800x480 HamClock to be running on Xvfb at a
resolution of `800x480x24`.

For example:

    Xvfb :1 -screen 0 800x480x24
    DISPLAY=:1 path-to-hamclock

Replace :1 with the desired display number.

### SaaS

The SaaS backend 

### Custom

If you write your own backend, just put it in the `backends` folder and
specify its file name (without `.py`) in `conf.txt`. Make sure you don't
accidentally commit it if you don't want to!
<!-- TODO: document API -->

## `conf.txt`

The server will not work without a `conf.txt` file. This file is a
space-separated table of configuration data. See the included file for a
reference. (That file will work for testing, but should not be used on an
Internet-accessible server. The password is `Testing123`. It uses the X11
backend, `DISPLAY=:1`.)

### `backend`

Use `x11` for the X11 backend, or `port8080` for the port 8080 backend.

### `display`

X11 display to use, such as `:1`. Must be the same as the one used for Xvfb
and HamClock. Has no effect with the `port8080` backend.

### `password_argon2`

Argon2-hashed password. Use `pwhash.py` to generate a hashed password.
