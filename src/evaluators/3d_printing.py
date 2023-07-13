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

import logging

def evaluate(inputfile, outputfile):
    nums = list(map(int, inputfile.read().strip().split()))
    if len(nums) % 3 != 0:
        logging.error(f"Input length of numbers not divisible by 3")
        return None
    n = len(nums) // 3
    p = nums[:n]
    w = nums[n:2*n]
    d = nums[2*n:]

    try:
        sol = list(map(int, outputfile.read().strip().split()))
    except ValueError:
        logging.error("Failed to parse output")
        return None
    if len(sol) != n:
        logging.error(f"Output length wrong, got {len(sol)}, expected {n}")
        return None
    if sorted(sol) != sorted(range(1, n+1)):
        logging.error(f"Output not a permutation of 1 to n")
        return None

    obj = 0
    C = 0
    for i in sol:
        C += p[i-1]
        T = max(C - d[i-1], 0)
        obj += w[i-1]*T

    return obj

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

