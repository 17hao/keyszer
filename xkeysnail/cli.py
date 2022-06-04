# -*- coding: utf-8 -*-
from .logger import *
from .info import __version__, __name__

CONFIG_HEADER = b"""
# -*- coding: utf-8 -*-
import re
from xkeysnail.transform import with_mark, set_mark, with_or_set_mark
from xkeysnail.config_api import *
"""

def eval_config(path):
    with open(path, "rb") as file:
        config_code = CONFIG_HEADER + file.read()
        exec(compile(config_code, path, 'exec'), globals())


def uinput_device_exists():
    from os.path import exists
    return exists('/dev/uinput')


def has_access_to_uinput():
    from evdev.uinput import UInputError
    try:
        from xkeysnail.output import _uinput  # noqa: F401
        return True
    except UInputError:
        return False


def main():
    print(f"{__name__} v{__version__}")

    # Parse args
    import argparse
    from appdirs import user_config_dir
    parser = argparse.ArgumentParser(description='Yet another keyboard remapping tool for X environment.')
#    parser.add_argument('config', metavar='config.py', type=str, default=user_config_dir('xkeysnail/config.py'), nargs='?',
#                        help='configuration file (See README.md for syntax)')
    parser.add_argument('-c', '--config', dest="config", metavar="config_file", type=str, 
                        default=user_config_dir('xkeysnail/config.py'),
                        help='configuration file (See README.md for syntax)')
    parser.add_argument('-d', '--devices', dest="devices", metavar='device', type=str, nargs='+',
                        help='keyboard devices to remap (if omitted, xkeysnail choose proper keyboard devices)')
    parser.add_argument('-w', '--watch', dest='watch', action='store_true',
                        help='watch keyboard devices plug in ')
    parser.add_argument('-q', '--quiet', dest='quiet', action='store_true',
                        help='suppress output of key events')
    parser.add_argument('--list-devices', dest='list_devices', action='store_true')
    parser.add_argument('--version', dest='show_version', action='store_true',
                        help='show version')
    args = parser.parse_args()

    if args.show_version:
        exit(0)

    if args.list_devices:
        from .input import get_devices_list, print_device_list
        print_device_list(get_devices_list())
        exit(0)

    # Make sure that the /dev/uinput device exists
    if not uinput_device_exists():
        print("""The '/dev/uinput' device does not exist.
Please check kernel configuration.""")
        import sys
        sys.exit(1)

    # Make sure that user have root privilege
    if not has_access_to_uinput():
        print("""Failed to open `uinput` in write mode.
Please check access permissions for /dev/uinput.""")
        import sys
        sys.exit(1)

    # Load configuration file
    eval_config(args.config)

    log(f"CONFIG: {args.config}")

    if args.quiet:
        log("QUIET: key output supressed.")

    if args.watch:
        log("WATCH: Watching for new devices to hot-plug.")

    # Enter event loop
    from xkeysnail.input import main_loop
    main_loop(args.devices, args.watch, args.quiet)