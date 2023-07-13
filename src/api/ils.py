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

from typing import cast, Union, TypeVar, Optional, Protocol
from collections.abc import Iterable

from time import perf_counter
import logging

from .utils import isclose

ObjectiveBound = Union[float, int]

Objective = TypeVar('Objective', bound=ObjectiveBound, covariant=True)
LocalMove = TypeVar('LocalMove')

class SolutionProtocol(Protocol[Objective, LocalMove]):
    def objective(self) -> Objective: ...
    def copy(self: Solution) -> Solution: ...
    def random_local_moves_wor(self) -> Iterable[LocalMove]: ...
    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]: ...
    def step(self, lmove: LocalMove) -> None: ...
    def perturb(self, ks: int) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

def ils(solution: Solution, budget: float, ks: int = 3) -> Solution:
    start = perf_counter()
    best = solution.copy()
    best_obj = cast(ObjectiveBound, best.objective())
    while perf_counter() - start < budget:
        # for move in solution.enumLocalMove():
        for move in solution.random_local_moves_wor():
            incr = cast(ObjectiveBound, solution.objective_incr_local(move))
            if incr < 0 and not isclose(incr, 0):
                solution.step(move)
                break
            if perf_counter() - start >= budget:
                obj = cast(ObjectiveBound, solution.objective())
                if obj < best_obj:
                    return solution
                else:
                    return best
        else:
            # Local optimum found
            obj = cast(ObjectiveBound, solution.objective())
            if obj < best_obj or isclose(obj, best_obj):
                best = solution.copy()
                best_obj = obj
                logging.info(f"New best solution found: {best_obj}")
            else:
                solution = best.copy()
            solution.perturb(ks)
    obj = cast(ObjectiveBound, solution.objective())
    if obj < best_obj:
        return solution
    else:
        return best
