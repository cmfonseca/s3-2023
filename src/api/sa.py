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

from typing import cast, Optional, Union, TypeVar, Protocol
from collections.abc import Callable, Iterable

from time import perf_counter
from math import exp
import random
import logging

ObjectiveBound = Union[float, int]

Objective = TypeVar('Objective', bound=ObjectiveBound, covariant=True)
LocalMove = TypeVar('LocalMove')

class SolutionProtocol(Protocol[Objective, LocalMove]):
    def objective(self) -> Objective: ...
    def copy(self: Solution) -> Solution: ...
    def random_local_moves_wor(self) -> Iterable[LocalMove]: ...
    def objective_incr_local(self, lmove: LocalMove) -> Optional[Objective]: ...
    def step(self, lmove: LocalMove) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

class LinearDecay:
    def __init__(self, init_temp: float) -> None:
        self.init_temp = init_temp

    def __call__(self, t: float) -> float:
        return t * self.init_temp

class ExponentialAcceptance:
    def __init__(self) -> None:
        ...

    def __call__(self, incr: float, t: float) -> float:
        if incr <= 0:
            return 1.0
        else:
            return exp(-incr / t)

def sa(solution: Solution,
       budget: float,
       init_temp: float,
       seed: Optional[int] = None,
       temperature: Optional[Callable[[float], float]] = None,
       acceptance: Optional[Callable[[float, float], float]] = None,
       ) -> Solution:
    if seed is not None:
        random.seed(seed)
        
    if temperature is None:
        temperature = LinearDecay(init_temp)

    if acceptance is None:
        acceptance = ExponentialAcceptance()
       
    start = perf_counter()
    best = solution.copy()
    bestobj = best.objective()
    while perf_counter() - start < budget:
        for move in solution.random_local_moves_wor():
            t = temperature(1 - (perf_counter()-start) / budget)
            if t <= 0:
                break
            incr = cast(ObjectiveBound, solution.objective_incr_local(move))
            if acceptance(incr, t) >= random.random():
                solution.step(move)
                obj = cast(Union[float, int], solution.objective())
                if bestobj is None or obj < bestobj:
                    best = solution.copy()
                    bestobj = obj
                    logging.info(f"New best solution: {bestobj}")
                break
    return best
