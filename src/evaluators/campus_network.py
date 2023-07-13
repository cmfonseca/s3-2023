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
from math import sqrt
import logging

def evaluate(inputfile, outputfile):
    @dataclass
    class Node:
        x: int
        y: int

    def euclidean_distance(u: Node, v: Node) -> int:
        dx = u.x - v.x
        dy = u.y - v.y
        return sqrt(dx*dx + dy*dy)

    vals = inputfile.readline().strip().split()
    assert len(vals) == 3
    n = int(vals[0])
    c0 = float(vals[1])
    c1 = float(vals[2])
    nodes = []
    for _ in range(n):
        x, y = map(float, inputfile.readline().strip().split())
        nodes.append(Node(x, y))

    lines = outputfile.readlines()
    con = [[] for _ in range(n)]

    for line in lines:
        try:
            u, v = map(int, line.strip().split())
        except ValueError:
            logging.warning(f"Ignoring line (failed to parse): {line}")
            continue
        if u < 1 or u > n:
            logging.error(f"Invalid node value {u}")
            return None
        if v < 1 or v > n:
            logging.error(f"Invalid node value {v}")
            return None
        con[u-1].append(v-1)
        con[v-1].append(u-1)

    q = [(0, 0, -1)]
    vis = {0}
    cable = 0
    trench = 0
    while len(q) > 0:
        u, d, p = q.pop()
        for v in con[u]:
            if v == p:
                continue
            if v in vis:
                logging.error("Cycle detected")
                return None
            vis.add(v)
            eucd = euclidean_distance(nodes[u], nodes[v])
            newd = d + eucd
            cable += newd
            trench += eucd
            q.append((v, newd, u))
    
    if len(vis) != n:
        logging.error("Not all nodes reachable")
        return None
            
    return c0 * cable + c1 * trench

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
