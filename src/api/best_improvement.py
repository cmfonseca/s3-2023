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

from typing import cast, Union, TypeVar, Protocol, Optional, Union
from collections.abc import Iterable

from time import perf_counter
import logging

from .utils import isclose

ObjectiveBound = Union[float, int]

Objective = TypeVar('Objective', bound=ObjectiveBound, covariant=True)
LocalMove = TypeVar('LocalMove')

class SolutionProtocol(Protocol[Objective, LocalMove]):
    def local_moves(self) -> Iterable[LocalMove]: ...
    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]: ...
    def step(self, lmove: LocalMove) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

def best_improvement(solution: Solution, budget: float) -> Solution:
    start = perf_counter()
    while perf_counter() - start < budget:
        best_incr: ObjectiveBound = 0
        best_move = None
        for move in solution.local_moves():
            delta = cast(ObjectiveBound, solution.objective_incr_local(move))
            if delta < best_incr and not isclose(delta, best_incr):
                best_incr = delta
                best_move = move
            if perf_counter() - start >= budget:
                break
        if best_move is not None:
            logging.debug(f"Improvement found: {best_incr}")
            solution.step(best_move)
        else:
            break
    return solution

