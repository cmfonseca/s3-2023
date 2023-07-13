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
    def random_local_moves_wor(self) -> Iterable[LocalMove]: ...
    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]: ...
    def step(self, lmove: LocalMove) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

def first_improvement(solution: Solution, budget: float) -> Solution:
    "First-improvement local search"
    start = perf_counter()
    while perf_counter() - start < budget:
        for move in solution.random_local_moves_wor():
            incr = cast(ObjectiveBound, solution.objective_incr_local(move))
            if incr < 0 and not isclose(incr, 0):
                logging.debug(f"Improvement found: {incr}")
                solution.step(move)
                break
            if perf_counter() - start >= budget:
                return solution
        else:
            break
    return solution
