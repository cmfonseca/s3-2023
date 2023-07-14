#!/usr/bin/env python3
#
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

from typing import TextIO, Optional, cast, NewType
from collections.abc import Sequence, Iterable, Hashable

from dataclasses import dataclass
from math import sqrt, isclose
from copy import copy
from itertools import chain
import logging
import sys

from api.utils import or_default, pairwise, sample2

@dataclass
class Component:
    k: int 

    @property
    def cid(self) -> Hashable:
        return self.k

@dataclass
class LocalMove:
    i: int
    j: int

if sys.version_info < (3, 9):
    Path = NewType('Path', list)
    Used = NewType('Used', set)
    Unused = NewType('Unused', set)
else:
    Path = NewType('Path', list[int])
    Used = NewType('Used', set[int])
    Unused = NewType('Unused', set[int])

class Solution():
    def __init__(self,
                 problem: Problem,
                 path: Path,
                 used: Used,
                 unused: Unused,
                 cost: int,
                 time_spent: int) -> None:
        self.problem = problem
        self.path = path
        self.used = used
        self.unused = unused
        self.cost = cost
        self.time_spent = time_spent

    def output(self) -> str:
        return "\n".join(map(str, self.path))

    def copy(self):
        return self.__class__(self.problem,
                              copy(self.path),
                              copy(self.used),
                              copy(self.unused),
                              self.cost,
                              self.time_spent)

    def is_feasible(self) -> bool:
        return len(self.path) == self.problem.n_items

    def objective(self) -> Optional[int]:
        if len(self.path) == self.problem.n_items:
            return self.cost
        else:
            return None

    def lower_bound(self, path=None) -> Optional[int]:
        # return self.cost
        # Cj - d_j
        total_cost = 0
        if path is None:
            path = self.path
        for i in path:
            total_cost += self.problem.production_times[i]
            # d = self.problem.due_dates[i]
            # if d > d_max:
            #     d_max = d

        if total_cost > 0:
            w = self.problem.penalty_weights[path[-1]]
            total_cost *= w

        return total_cost - self.problem.due_dates[path[-1]]

    def add_moves(self) -> Iterable[Component]:
        if len(self.path) < self.problem.n_items:
            for k in self.unused:
                yield Component(k)

    def local_moves(self) -> Iterable[LocalMove]:
        for i in range(0, len(self.path)-2):
            for j in range(i+1, len(self.path)-1):
                yield LocalMove(i, j)

    def random_local_move(self) -> Optional[LocalMove]:
        if len(self.path) >= 2:
            i = random.randrange(0, len(self.path)-2)
            j = random.randrange(i+1, len(self.path)-1)
            return LocalMove(i, j)
        else:
            return None

    def random_local_moves_wor(self) -> Iterable[LocalMove]:
        for i, j in sample2(len(self.path)-1, len(self.path)-1):
            if j > i:
                yield LocalMove(i, j)

    def heuristic_add_move(self) -> Optional[Component]:
        if len(self.path) < self.problem.n_items:
            max_heuristic_weight = - float('inf')
            idx = 0
            for k in self.used:
                heuristic_weight = self.problem.penalty_weights[k] / (self.problem.due_dates[k] + 1)
                if heuristic_weight > max_heuristic_weight:
                    max_heuristic_weight = heuristic_weight
                    idx = k
            return Component(idx)

    def add(self, component: Component) -> None:
        self.path.append(component.k)
        self.unused.remove(component.k)
        self.used.add(component.k)
        self.time_spent += self.problem.production_times[component.k]
        self.cost += self.problem.penalty_weights[component.k] * max(0, self.time_spent-self.problem.due_dates[component.k])

    def step(self, lmove: LocalMove) -> None:
        i, j = lmove.i, lmove.j
        self.path[i], self.path[j] = self.path[j], self.path[i]
        time_spent = 0
        cost = 0
        for k in self.path:
            time_spent += self.problem.production_times[k]
            cost += self.problem.penalty_weights[k] * max(0, time_spent - self.problem.due_dates[k])

    def objective_incr_local(self, lmove: LocalMove) -> Optional[float]:
        raise NotImplementedError
        # i, j = lmove.i, lmove.j
        # ndist = self.dist
        # ndist -= self.problem.dist[self.path[i-1]][self.path[i]]
        # ndist -= self.problem.dist[self.path[j-1]][self.path[j]]
        # ndist += self.problem.dist[self.path[i-1]][self.path[j-1]]
        # ndist += self.problem.dist[self.path[i]][self.path[j]]
        # return ndist - self.dist

    def lower_bound_incr_add(self, component: Component) -> Optional[float]:
        # raise NotImplementedError
        if len(self.path) <= cast(Problem, self.problem).n_items:
            # u, v = component.u, component.v
            # d = self.problem.dist[u][v]
            # new_lower_bound - old_lower_bound
            # Component : k -> index of next item
            new_path = copy(self.path).append(component.k)
            new_lower_bound = self.lower_bound(new_path)
            return new_lower_bound - self.lower_bound()
            
        else:
            return 0

    def perturb(self, ks: int) -> None:
        for _ in range(ks):
            move = self.random_local_move()
            if move is not None:
                self.step(move)

    def components(self) -> Iterable[Component]:
        for k in range(len(self.path)):
            yield Component(k)

    def objective(self) -> Optional[int]:
        return self.cost


class Problem():
    def __init__(
        self,
        production_times: list[int],
        penalty_weights: list[int],
        due_dates: list[int]
    ) -> None:
        assert len(production_times) == len(penalty_weights) == len(due_dates)
        self.n_items = len(production_times)
        
    @classmethod
    def from_textio(cls, inputfile) -> Problem:
        nums = list(map(int, inputfile.read().strip().split()))
        if len(nums) % 3 != 0:
            logging.error(f"Input length of numbers not divisible by 3")
            return None
        n = len(nums) // 3
        return cls(nums[:n], nums[n:2*n], nums[2*n:])

    def empty_solution(self) -> Solution:
        return Solution(self, [], [], set(range(self.n_items)), 0, 0)

    def empty_solution_with_start(self, start: int) -> Solution:
        return Solution(self, start, [start], {start}, set(range(self.n_items))-{start}, 0)


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
        if args.csearch == 'beam':
            s = beam_search(s, 10)
        elif args.csearch == 'grasp':
            # s = grasp(s, args.cbudget, alpha = 0.01)
            s = grasp(s, args.cbudget, alpha = 0.01, local_search = lambda s: first_improvement(s, 0.1))
        elif args.csearch == 'greedy':
            s = greedy_construction(s)
        elif args.csearch == 'heuristic':
            s = heuristic_construction(s)
        elif args.csearch == 'as':
            ants = [p.empty_solution_with_start(i) for i in range(p.n_items)]
            # s = aco(ants, 30.0, beta = 5.0, rho = 0.5, tau0 = 1 / 3000.0)
            lbudget = 1.0 / len(ants)
            s = ant_system(ants, args.cbudget, beta = 5.0, rho = 0.5, tau0 = 1 / 3000.0,
                           local_search = lambda s: first_improvement(s, lbudget))
        elif args.csearch == 'mmas':
            ants = [p.empty_solution_with_start(i) for i in range(p.n_items)]
            # s = mmas(ants, 30.0, beta = 5.0, rho = 0.02, taumax = 1 / 3000.0, ants = 0.1)
            lbudget = 1.0 / len(ants)
            s = mmas(ants, args.cbudget, beta = 5.0, rho = 0.05, taumax = 1 / 3000.0, globalratio = 0.1,
                     local_search = lambda s: first_improvement(s, lbudget))

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
            s = sa(s, args.lbudget, 10)

    end = perf_counter()

    if s is not None:
        print(s.output(), file=args.output_file)
        if s.objective() is not None:
            logging.info(f"Objective: {s.objective():.3f}")
        else:
            logging.info(f"Objective: None")
    else:
        logging.info(f"Objective: no solution found")

    logging.info(f"Elapsed solving time: {end-start:.4f}")
