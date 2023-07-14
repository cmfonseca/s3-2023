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
    @dataclass
    class Node:
        x: int
        y: int
        h: int
        b: int

    def manhattan_distance(u: Node, v: Node) -> int:
        return abs(u.x - v.x) + abs(u.y - v.y)

    def candle_score(u: Node, d: int, last: Node) -> int:
        return max(0, u.h - u.b * (d + manhattan_distance(u, last)))

    n = int(inputfile.readline().strip())
    nodes = []
    x, y = map(int, inputfile.readline().strip().split())
    nodes.append(Node(x, y, 0, 0))
    for _ in range(1, n):
        x, y, h, b = map(int, inputfile.readline().strip().split())
        nodes.append(Node(x, y, h, b))

    lines = outputfile.readlines()
    path = []
    for line in lines:
        try:
            path.append(int(line.strip()))
        except ValueError:
            logging.warning(f"Ignoring line (failed to parse): {line}")
            continue
        if path[-1] >= n or path[-1] < 1:
            logging.error(f"Invalid node value {path[-1]}")
            return None
    if len(set(path)) != len(path):
        logging.error("Repeated nodes in path")
        return None

    score = 0
    dist = 0
    nonzero = 0
    last = nodes[0]
    for i in range(len(path)):
        nxt = nodes[path[i]]
        incr = candle_score(nxt, dist, last)
        if incr > 0:
            nonzero += 1
        score += incr
        dist += manhattan_distance(last, nxt)
        last = nxt

    return score

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

