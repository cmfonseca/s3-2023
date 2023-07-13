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

from typing import cast, TypeVar, Protocol, Optional, Union
from collections.abc import Callable, Iterable

from time import perf_counter
from operator import itemgetter
import random
import logging

ObjectiveBound = Union[int, float]
Objective = TypeVar('Objective', bound=ObjectiveBound, covariant=True)
Component = TypeVar('Component')

class SolutionProtocol(Protocol[Objective, Component]):
    def lower_bound(self) -> Optional[Objective]: ...
    def objective(self) -> Optional[Objective]: ...
    def copy(self: Solution) -> Solution: ...
    def is_feasible(self) -> bool: ...
    def add_moves(self) -> Iterable[Component]: ...
    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]: ...
    def add(self, component: Component) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)
    
class LocalSearch(Protocol[Solution]):
    def __call__(self, s: Solution) -> Optional[Solution]: ...

def grasp(solution: Solution,
          budget: float,
          alpha: float = 0.1,
          seed: Optional[int] = None,
          local_search: Optional[LocalSearch[Solution]] = None,
          ) -> Optional[Solution]:
    if seed is not None:
        random.seed(seed)
    start = perf_counter()
    best, bestobj = None, None
    while perf_counter() - start < budget:
        s = solution.copy()
        b, bobj = (s.copy(), s.objective()) if s.is_feasible() else (None, None)
        C = [(cast(ObjectiveBound, s.lower_bound_incr_add(c)), c) for c in s.add_moves()]
        while len(C) != 0:
            cmin = min(C, key=itemgetter(0))[0]
            cmax = max(C, key=itemgetter(0))[0]
            thresh = cmin + alpha * (cmax - cmin)
            RCL = [c for decr, c in C if decr <= thresh]
            c = random.choice(RCL)
            s.add(c)
            if s.is_feasible():
                obj = cast(ObjectiveBound, s.objective())
                if bobj is None or obj < bobj:
                    b, bobj = s.copy(), obj
            C = [(cast(ObjectiveBound, s.lower_bound_incr_add(c)), c) for c in s.add_moves()]
        if b is not None:
            if local_search is not None:
                b = local_search(b)
                if b is not None and b.is_feasible():
                    bobj = cast(ObjectiveBound, b.objective())
            if bestobj is None or bobj < bestobj:
                best, bestobj = b, bobj
                logging.info(f"New best solution found: {bestobj}")
    return best
