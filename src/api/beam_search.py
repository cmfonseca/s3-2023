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

from typing import cast, TypeVar, Union, Any, List, Tuple, Protocol, Optional
from collections.abc import Iterable

from operator import itemgetter
import logging

T = TypeVar('T')

class ObjectiveProtocol(Protocol):
    def __lt__(self: T, other: T) -> bool: ...
    def __add__(self: T, other: T) -> T: ...

Objective = TypeVar('Objective', bound=ObjectiveProtocol, covariant=True)
Component = TypeVar('Component')

class SolutionProtocol(Protocol[Objective, Component]):
    def objective(self) -> Optional[Objective]: ...
    def lower_bound(self) -> Optional[Objective]: ...
    def copy(self: Solution) -> Solution: ...
    def is_feasible(self) -> bool: ...
    def add_moves(self) -> Iterable[Component]: ...
    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]: ...
    def add(self, component: Component) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

BSList = List[Tuple[Objective, Solution]]
BSCandidates = List[Tuple[Objective, Solution, Component]]

def candidates(prev: BSList) -> BSCandidates:
    result: BSCandidates = []
    for lb, s in prev:
        result.extend(map(lambda c: (lb + cast(ObjectiveProtocol, s.lower_bound_incr_add(c)),
                                     s, c),
                          s.add_moves()))
    return result

def evolve(candidates: BSCandidates, bw: int) -> BSList:
    result: BSList = []
    candidates.sort(key=itemgetter(0))
    for lb, s, c in candidates[:bw]:
        ns = s.copy()
        ns.add(c)
        result.append((lb, ns))
    return result

def beam_search(solution: Solution, bw: int = 10) -> Solution:
    best = solution
    bestobj = best.objective()
    v = [(cast(ObjectiveProtocol, solution.lower_bound()), solution)]
    while True:
        c = candidates(v)
        if len(c) == 0:
            break
        v = evolve(c, bw)
        for _, s in v:
            if s.is_feasible():
                obj = cast(ObjectiveProtocol, s.objective())
                if bestobj is None or obj < bestobj:
                    best, bestobj = s, obj
                    logging.info(f"New best solution found: {bestobj}")
    return best
