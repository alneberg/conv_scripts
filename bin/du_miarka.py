#!/usr/bin/python3

import argparse
import glob
import subprocess
import sys


def main(path_str, non_human_readable=False):
    paths = glob.glob(path_str)
    if not paths:
        sys.stderr.write("No paths found. Exiting")
        return
    # Requires python 3.5 or higher
    result = subprocess.run(
        ["getfattr", "-n", "ceph.dir.rbytes"] + paths, stdout=subprocess.PIPE
    )
    print(result.stdout)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A faster version of `du` for our cluster Miarka, using ceph supplied space consumption."
    )
    parser.add_argument("path", help="The path that should be looked into")
    parser.add_argument(
        "-n",
        "--non-human-readable",
        action="store_true",
        help="Print sizes in bytes instead of human readable format (e.g. 1K 234M 2G)",
    )

    args = parser.parse_args()

    main(args.path, args.non_human_readable)
