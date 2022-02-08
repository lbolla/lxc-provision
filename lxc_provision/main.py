import argparse
import logging
from pathlib import Path
import shlex
import subprocess
import sys
import time

import coloredlogs
import yamlenv


def call(cmd):
    logging.debug("CMD: %s", cmd)
    return subprocess.check_call(shlex.split(cmd))


def parse_args():
    parser = argparse.ArgumentParser(description='Provision LXD vm')
    parser.add_argument('--verbose', '-v', action='count', default=0)
    parser.add_argument('filename', nargs='?')
    args = parser.parse_args()
    return args


def setup_logging(args):
    level = logging.WARNING

    if args.verbose == 1:
        level = logging.INFO
    else:
        level = logging.DEBUG

    coloredlogs.install(level=level)


def main():
    args = parse_args()
    setup_logging(args)

    if args.filename:
        fid = open(args.filename)
    else:
        logging.info('Reading from stdin')
        fid = sys.stdin

    logging.debug('Loading spec')
    spec = yamlenv.load(fid)

    logging.info('Initialising image')
    vm = ''
    secureboot = ''
    if spec.get('vm', True):
        vm = '--vm'
        if spec.get('secureboot', False):
            secureboot = '-c security.secureboot=true'

    call(
        f"lxc init images:{spec['image']} {spec['name']} "
        f"{vm} "
        f"{secureboot} "
        f"-c limits.memory={spec['limits']['memory']}")

    if vm:
        logging.info('Adding config device')
        call(
            f"lxc config device add {spec['name']} "
            f"config disk source=cloud-init:config")

    logging.info('Adding volumes')
    for vol in spec.get('volumes', []):
        vol_src = Path(vol['src']).expanduser()
        vol_dst = Path(vol['dst']).expanduser()
        vol_name = vol['name']
        call(
            f"lxc config device add {spec['name']} "
            f"{vol_name} disk source={vol_src} path={vol_dst}")

    logging.info('Waiting for image to start')
    call(f"lxc start {spec['name']}")
    wait_n = 0
    while True:
        try:
            call(f"lxc exec {spec['name']} ls")
        except subprocess.CalledProcessError:
            if wait_n < 60:
                wait_n += 1
                time.sleep(1)
            else:
                raise
        else:
            break

    logging.info('Copying data')
    for c in spec.get('copy', []):
        c_src = Path(c['src']).expanduser()
        c_dst = Path(c['dst']).expanduser()

        args = ''
        if c_src.is_dir():
            args = '--recursive'

        call(
            f"lxc file push --create-dirs {args} "
            f"{c_src} {spec['name']}{c_dst}")

    logging.info('Install basic packages')
    call(f"lxc exec {spec['name']} -- apt update")
    call(f"lxc exec {spec['name']} -- apt install --yes curl devscripts git gnupg")

    setup_script_lines = spec.get('setup_script')
    if setup_script_lines:
        logging.info('Executing setup script')
        for line in setup_script_lines:
            call(f"lxc exec {spec['name']} -- {line}")

    print(f'''Done.

Type:
    lxc exec {spec['name']} bash
to connect to your vm.

''')
