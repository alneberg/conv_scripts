#!/usr/bin/python3

import argparse
import glob
import subprocess
import sys


def sizeof_fmt(num, suffix="B"):
    """Human readable format for file sizes

    From https://stackoverflow.com/a/1094933/
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f} Yi{suffix}"


def main(path_str, non_human_readable=False):
    paths = glob.glob(path_str)
    if not paths:
        sys.stderr.write("No paths found. Exiting\n")
        return

    total = 0
    for path in paths:
        # Check if path is not a directory
        if not os.path.isdir(path):
            statinfo = os.stat(path)
            bytes = statinfo.st_size
            if non_human_readable:
                print(f"{path} {bytes}")
            else:
                print(f"{path} {sizeof_fmt(bytes)}")
        else:  # Directory
            # Requires python 3.5 or higher
            result = subprocess.run(
                ["getfattr", "-n", "ceph.dir.rbytes", path], stdout=subprocess.PIPE
            )
            if result.returncode != 0:
                sys.stderr.write("Error running getfattr. Exiting\n")
                return
            lines = result.stdout.decode("utf-8").splitlines()
            for line in lines:
                if line.startswith("# file:"):
                    filename = line.split(" ")[2]
                    filename = filename.strip()
                if line.startswith("ceph.dir.rbytes"):
                    bytes = int((line.split("=")[1]).replace('"', ""))
                    bytes_readable = sizeof_fmt(bytes)
                    if non_human_readable:
                        print(f"{filename} {bytes}")
                    else:
                        print(f"{filename} {bytes_readable}")
                    total += int(bytes)

    if non_human_readable:
        print(f"Total: {total}")
    else:
        print(f"Total: {sizeof_fmt(total)}")


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
