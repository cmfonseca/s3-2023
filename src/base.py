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

from __future__ import annotations

from copy import copy
from typing import TextIO, Optional, Any
from collections.abc import Iterable, Hashable

import logging

Objective = Any


class Component:
    @property
    def cid(self) -> Hashable:
        raise NotImplementedError


class LocalMove:
    ...


class Solution:
    def __init__(self,
                 problem: Problem,
                 obj_value: float) -> None:
        self.problem = problem
        self.containers = []  # list of all containers between depot and treatment plant
        self.directions = []  # list of directions proportionate to the containers
        self.picked = []  # list of all picked containers
        self.not_picked = []  # list of all not yet picked containers
        self.obj_value = obj_value

    def output(self) -> str:
        """
        Generate the output string for this solution
        """
        for i in range(len(self.containers)):
            print(self.containers[i] + " " + self.directions[i])

    def copy(self) -> Solution:
        """
        Return a copy of this solution.

        Note: changes to the copy must not affect the original
        solution. However, this does not need to be a deepcopy.
        """
        return self.__class__(self.problem,
                              copy(self.containers),
                              copy(self.picked),
                              copy(self.not_picked),
                              self.obj_value)

    def is_feasible(self) -> bool:
        """
        Return whether the solution is feasible or not
        """
        return len(self.not_picked) == 0

    def objective(self) -> Optional[Objective]:
        """
        Return the objective value for this solution if defined, otherwise
        should return None
        """
        # case the solution is not completed
        if len(self.not_picked) > 0:
            return None

        obj_value = 0
        for idx in range(len(self.containers)):
            # add the route from the depot to the first container
            if idx == 0:
                obj_value += self.problem.depot_to_container[self.directions[idx]][self.containers[idx]]

            # add route between containers
            else:
                # construct the direction index by concat the directions to a binary string a read it in dec
                dir_idx = int(str(self.directions[idx - 1]) + str(self.directions[idx]), 2)
                obj_value += self.problem.container_to_container[dir_idx][self.containers[idx - 1]][
                    self.containers[idx]]

        # add the route from the last container to the plant
        obj_value += self.problem.container_to_plant[self.directions[-1]][self.containers[-1]]

        return obj_value

    def lower_bound(self) -> Optional[Objective]:
        """
        Return the lower bound value for this solution if defined,
        otherwise return None
        """
        obj_value = 0
        for idx in range(len(self.containers)):
            # add the route from the depot to the first container
            if idx == 0:
                obj_value += self.problem.depot_to_container[self.directions[idx]][self.containers[idx]]

            # add route between containers
            else:
                # construct the direction index by concat the directions to a binary string a read it in dec
                dir_idx = int(str(self.directions[idx - 1]) + str(self.directions[idx]), 2)
                obj_value += self.problem.container_to_container[dir_idx][self.containers[idx - 1]][
                    self.containers[idx]]

        for dest_con in self.not_picked:
            options = []
            for dep_con in self.not_picked:
                for dir_idx in range(4):
                    if dep_con != dest_con:
                        options.append(self.problem.container_to_container[dir_idx][dep_con][dest_con])

            # add the minimum value
            obj_value += min(options)

        # add the route from the last container to the plant
        options = []
        for dep_con in self.not_picked:
            for dir_idx in range(4):
                options.append(self.problem.container_to_plant[dir_idx][dep_con])
        obj_value += min(options)

        return obj_value

    def add_moves(self) -> Iterable[Component]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all components that can be added to the solution
        """
        raise NotImplementedError

    def local_moves(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves that can be applied to the solution
        """
        raise NotImplementedError

    def random_local_move(self) -> Optional[LocalMove]:
        """
        Return a random local move that can be applied to the solution.

        Note: repeated calls to this method may return the same
        local move.
        """
        raise NotImplementedError

    def random_local_moves_wor(self) -> Iterable[LocalMove]:
        """
        Return an iterable (generator, iterator, or iterable object)
        over all local moves (in random order) that can be applied to
        the solution.
        """
        raise NotImplementedError

    def heuristic_add_move(self) -> Optional[Component]:
        """
        Return the next component to be added based on some heuristic
        rule.
        """
        raise NotImplementedError

    def add(self, component: Component) -> None:
        """
        Add a component to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """
        raise NotImplementedError

    def step(self, lmove: LocalMove) -> None:
        """
        Apply a local move to the solution.

        Note: this invalidates any previously generated components and
        local moves.
        """
        raise NotImplementedError

    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]:
        """
        Return the objective value increment resulting from applying a
        local move. If the objective value is not defined after
        applying the local move return None.
        """
        raise NotImplementedError

    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]:
        """
        Return the lower bound increment resulting from adding a
        component. If the lower bound is not defined after adding the
        component return None.
        """
        raise NotImplementedError

    def perturb(self, ks: int) -> None:
        """
        Perturb the solution in place. The amount of perturbation is
        controlled by the parameter ks (kick strength)
        """
        raise NotImplementedError

    def components(self) -> Iterable[Component]:
        """
        Returns an iterable to the components of a solution
        """
        raise NotImplementedError


class Problem:
    def __init__(self, n: int, depot_to_container: list, container_to_plant: list, container_to_container: list) -> None:
        self.n = n
        self.depot_to_container = depot_to_container
        self.container_to_plant = container_to_plant
        # index - combination: 0 - 00, 1 - 10, 2 - 11, 3 - 10
        self.container_to_container = container_to_container

    @classmethod
    def from_textio(cls, f: TextIO) -> Problem:
        """
        Create a problem from a text I/O source `f`
        """
        depot_to_container = [[], []]
        container_to_plant = [[], []]
        # index - combination: 0 - 00, 1 - 01, 2 - 11, 3 - 10
        container_to_container = [[], [], [], []]

        n = int(f.readline())
        for idx in range(1, 5 + 4 * n):
            line = f.readline().strip()  # Remove leading/trailing whitespaces
            elements = [int(x) for x in line.split()]  # Split line by spaces
            if idx == 1:
                depot_to_container[0] = elements
            elif idx == 2:
                depot_to_container[1] = elements
            elif idx == 3:
                container_to_plant[0] = elements
            elif idx == 4:
                container_to_plant[1] = elements
            elif idx < n + 5:
                container_to_container[0].append(elements)
            elif idx < 2 * n + 5:
                container_to_container[1].append(elements)
            elif idx < 3 * n + 5:
                container_to_container[3].append(elements)
            else:
                container_to_container[2].append(elements)

        return cls(n, depot_to_container, container_to_plant, container_to_container)


if __name__ == '__main__':
    from api.solvers import *
    from time import perf_counter
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--log-level',
                        choices=['critical', 'error', 'warning', 'info', 'debug'],
                        default='warning')
    parser.add_argument('--log-file', type=argparse.FileType('w'), default=sys.stderr)
    parser.add_argument('--csearch',
                        choices=['beam', 'grasp', 'greedy', 'heuristic', 'as', 'mmas', 'none'],
                        default='none')
    parser.add_argument('--cbudget', type=float, default=5.0)
    parser.add_argument('--lsearch',
                        choices=['bi', 'fi', 'ils', 'rls', 'sa', 'none'],
                        default='none')
    parser.add_argument('--lbudget', type=float, default=5.0)
    parser.add_argument('--input-file', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('--output-file', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    logging.basicConfig(stream=args.log_file,
                        level=args.log_level.upper(),
                        format="%(levelname)s;%(asctime)s;%(message)s")

    p = Problem.from_textio(args.input_file)
    s: Optional[Solution] = p.empty_solution()

    start = perf_counter()

    if s is not None:
        if args.csearch == 'heuristic':
            s = heuristic_construction(s)
        elif args.csearch == 'greedy':
            s = greedy_construction(s)
        elif args.csearch == 'beam':
            s = beam_search(s, 10)
        elif args.csearch == 'grasp':
            s = grasp(s, args.cbudget, alpha=0.01)
        elif args.csearch == 'as':
            ants = [s] * 100
            s = ant_system(ants, args.cbudget, beta=5.0, rho=0.5, tau0=1 / 3000.0)
        elif args.csearch == 'mmas':
            ants = [s] * 100
            s = mmas(ants, args.cbudget, beta=5.0, rho=0.02, taumax=1 / 3000.0, globalratio=0.5)

    if s is not None:
        if args.lsearch == 'bi':
            s = best_improvement(s, args.lbudget)
        elif args.lsearch == 'fi':
            s = first_improvement(s, args.lbudget)
        elif args.lsearch == 'ils':
            s = ils(s, args.lbudget)
        elif args.lsearch == 'rls':
            s = rls(s, args.lbudget)
        elif args.lsearch == 'sa':
            s = sa(s, args.lbudget, 30)

    end = perf_counter()

    if s is not None:
        print(s.output(), file=args.output_file)
        if s.objective() is not None:
            logging.info(f"Objective: {s.objective():.3f}")
        else:
            logging.info(f"Objective: None")
    else:
        logging.info(f"Objective: no solution found")

    logging.info(f"Elapsed solving time: {end - start:.4f}")
