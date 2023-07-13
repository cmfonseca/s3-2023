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

from typing import cast, Protocol, TypeVar, Optional
from collections.abc import Iterable

from operator import itemgetter
import logging

class ObjectiveProtocol(Protocol):
    def __lt__(self, other) -> bool: ...

Objective = TypeVar('Objective', bound=ObjectiveProtocol, covariant=True)
Component = TypeVar('Component')

class SolutionProtocol(Protocol[Objective, Component]):
    def add_moves(self) -> Iterable[Component]: ...
    def add(self, component: Component) -> None: ...
    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

def greedy_construction(solution: Solution) -> Solution:
    while True:
        best = min(filter(lambda v: v[0] is not None,
                          map(lambda c: (solution.lower_bound_incr_add(c), c),
                              solution.add_moves())),
                   default = None,
                   key = itemgetter(0))
        if best is None:
            break
        solution.add(best[1])
        logging.info(f"Component added, lb increment: {best[0]}")
    return solution
