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
    M, P = map(int, inputfile.readline().strip().split())
    d = list(map(int, inputfile.readline().strip().split()))
    T = sum(d)
    a = []
    r = [0] * P
    for p in range(P):
        a.append(list(map(int, inputfile.readline().strip().split())))
        for i in range(M):
            r[p] += a[-1][i] * d[i]
        r[p] /= T

    lines = outputfile.readlines()
    u = []
    for line in lines:
        try:
            u.append(int(line.strip()))
        except ValueError:
            logging.warning(f"Failed to parse line, ignoring: {line}")
    if len(u) != T:
        logging.error(f"Invalid number of models, got {len(u)}, expected {T}")
        return None

    J = 0
    dsol = [0] * M
    aux = [0] * P
    for (t, mod) in enumerate(u):
        if mod < 0 or mod >= M:
            logging.error(f"Invalid model number {mod}")
            return None
        dsol[mod] += 1
        if dsol[mod] > d[mod]:
            logging.error(f"Too many models of type {mod}")
            return None
        for p in range(P):
            aux[p] += a[p][mod]
            J += ((t+1) * r[p] - aux[p])**2

    return J

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
    print(f"Objective value: {obj:.6f}")


