#!/usr/bin/env python3
#
# Copyright (C) 2023 Alexandre Jesus <https://adbjesus.com>, Carlos M. Fonseca <cmfonsec@dei.uc.pt>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from dataclasses import dataclass
import logging

def evaluate(inputfile, outputfile):
    n = int(inputfile.readline().strip())
    depot = [list(map(int, inputfile.readline().strip().split())),
             list(map(int, inputfile.readline().strip().split()))]
    plant = [list(map(int, inputfile.readline().strip().split())),
             list(map(int, inputfile.readline().strip().split()))]

    d00 = [list(map(int, inputfile.readline().strip().split())) for _ in range(n)]
    d01 = [list(map(int, inputfile.readline().strip().split())) for _ in range(n)]
    d11 = [list(map(int, inputfile.readline().strip().split())) for _ in range(n)]
    d10 = [list(map(int, inputfile.readline().strip().split())) for _ in range(n)]
    dist = [[d00, d01], [d10, d11]]

    lines = outputfile.readlines()
    path = []
    for line in lines:
        try:
            a, b = map(int, line.strip().split())
        except ValueError:
            logging.warning(f"Ignoring line (failed to parse): {line}")
            continue
        if b < 0 or b > 1:
            logging.error(f"Invalid direction, got {b}, expected 0 or 1")
            return None
        if a < 1 or a > n:
            logging.error(f"Invalid node number, got {b}, expected a value between 1 and {n}")
            return None
        path.append((a-1, b))
    if len(path) != n:
        logging.error(f"Invalid number of nodes, got {len(path)}, expected {n}")
        return None

    d = depot[path[0][1]][path[0][0]] + plant[path[-1][1]][path[-1][0]]
    for i in range(1, len(path)):
        prv = path[i-1]
        nxt = path[i]
        aux = dist[prv[1]][nxt[1]][prv[0]][nxt[0]]
        if aux == -1:
            logging.error(f"Using an invalid connection")
            return None
        d += aux

    return d

if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('inputfile', type=argparse.FileType('r'))
    parser.add_argument('outputfile', type=argparse.FileType('r'))
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stderr, level="INFO",
                        format="%(levelname)s;%(message)s")

    obj = evaluate(args.inputfile, args.outputfile)
    print("Objective value:", obj)
