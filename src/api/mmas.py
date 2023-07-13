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

from typing import cast, TypeVar, Protocol, Optional, Union, Any
from collections.abc import Callable, Iterable, Hashable
from collections import defaultdict
from time import perf_counter
from operator import itemgetter
import random
import logging
import math

from .utils import argmin, isclose

ObjectiveBound = Union[float, int]
ComponentId = Hashable

Objective = TypeVar('Objective', bound=ObjectiveBound, covariant=True)

class ComponentProtocol(Protocol):
    @property
    def cid(self) -> ComponentId: ...

Component = TypeVar('Component', bound=ComponentProtocol)

class SolutionProtocol(Protocol[Objective, Component]):
    def lower_bound(self) -> Optional[Objective]: ...
    def objective(self) -> Optional[Objective]: ...
    def copy(self: Solution) -> Solution: ...
    def is_feasible(self) -> bool: ...
    def add_moves(self) -> Iterable[Component]: ...
    def lower_bound_incr_add(self, component: Component) -> Optional[Objective]: ...
    def add(self, component: Component) -> None: ...
    def components(self) -> Iterable[Component]: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)
    
class LocalSearch(Protocol[Solution]):
    def __call__(self, s: Solution) -> Solution: ...

def construct_ant(solution: Solution,
                  alpha: float,
                  beta: float,
                  tau: dict[ComponentId, float]) -> Solution:
    while True:
        cs = []
        cszero = []
        p = []
        best = None
        for c in solution.add_moves():
            k = c.cid
            lbincr = solution.lower_bound_incr_add(c)
            if lbincr is None:
                raise ValueError("lbincr cannot be None")
            if isclose(lbincr, 0.0):
                cszero.append(c)
            else:
                cs.append(c)
                p.append((tau[k]**alpha) * ((1.0 / lbincr) ** beta))
        if best is None:
            if len(cszero) > 0:
                best = random.choice(cszero)
            elif len(cs) > 0:
                if sum(p) > 0:
                    best = random.choices(cs, p, k = 1)[0]
                else:
                    best = random.choice(cs)
            else:
                break
        solution.add(best)
    return solution

def mmas(solutions: list[Solution],
         budget: float,
         taumax: float,
         a: float = 5.0,
         alpha: float = 1.0,
         beta: float = 3.0,
         rho: float = 0.5,
         globalratio: float = 0.5,
         nrestart: int = 500,
         seed: Optional[int] = None,
         local_search: Optional[LocalSearch[Solution]] = None,
         ) -> Optional[Solution]:
    start = perf_counter()

    if seed is not None:
        random.seed(seed)

    taumin = taumax / a
    tau0 = taumax
    tau: dict[ComponentId, float] = defaultdict(lambda: tau0)
    nants = len(solutions)

    best, bestobj = None, None
    nc = 0
    ni = 0
    while perf_counter() - start < budget:
        nc += 1
        ni += 1
        # Build ants
        logging.debug(f"Building ants (iteration {nc})")
        ants = []
        for s in solutions:
            if perf_counter() - start >= budget:
                break
            ant = construct_ant(s.copy(), alpha, beta, tau)

            if ant.is_feasible() and (bestobj is None or ant.objective() < bestobj):
                best = ant.copy()
                bestobj = cast(ObjectiveBound, ant.objective())
                ni = 0
                logging.info(f"New best solution found (iteration {nc}): {bestobj}")

            if local_search is not None:
                ant = local_search(ant)
                if ant.is_feasible() and (bestobj is None or cast(ObjectiveBound, ant.objective()) < bestobj):
                    best = ant.copy()
                    bestobj = cast(ObjectiveBound, ant.objective())
                    ni = 0
                    logging.info(f"New best solution found (iteration {nc}): {bestobj}")

            if ant.is_feasible():
                ants.append(ant)

        if len(ants) > 0:
            mi = math.inf
            ma = -math.inf
            su = 0.0
            c = 0
            for ant in ants:
                obj = cast(ObjectiveBound, ant.objective())
                mi = min(mi, obj)
                ma = max(ma, obj)
                su += obj
                c += 1
            avg = su / c if c > 0 else None
            logging.debug(f"Minimum (iteration {nc}): {mi}")
            logging.debug(f"Average (iteration {nc}): {avg}")
            logging.debug(f"Maximum (iteration {nc}): {ma}")

        # Update pheromones
        logging.debug(f"Updating pheromones (iteraton {nc})")
        if ni < nrestart:
            taumax = 1.0 / cast(ObjectiveBound, bestobj)
            taumin = taumax / a
            tau0 = (1.0 - rho) * tau0
            tau0 = max(taumin, min(taumax, tau0))
            for k in tau:
                tau[k] = max(taumin, min(taumax, (1.0 - rho) * tau[k]))
            if (best is None and len(ants) > 0) or (len(ants) > 0 and random.random() > globalratio):
                # Using iteration-best ant
                bi = argmin(map(lambda ant: cast(ObjectiveBound, ant.objective()), ants))
                b = ants[bi]
                obj = cast(ObjectiveBound, b.objective())
                logging.debug(f"Update pheromones using iteration-best ({obj})")
                for comp in b.components():
                    cid = comp.cid
                    if cid not in tau:
                        tau[cid] = min(taumax, tau0 + 1.0 / obj)
                    else:
                        tau[cid] = min(taumax, tau[cid] + 1.0 / obj)
            elif best is not None:
                # Using global-best ant
                logging.debug(f"Update pheromones using global best ({bestobj})")
                for comp in best.components():
                    cid = comp.cid
                    if cid not in tau:
                        tau[cid] = min(taumax, tau0 + 1.0 / cast(ObjectiveBound, bestobj))
                    else:
                        tau[cid] = min(taumax, tau[cid] + 1.0 / cast(ObjectiveBound, bestobj))
            else:
                logging.warning("No valid ant to update pheromones")
        else:
            # Reinitialization
            logging.debug(f"Reinitialize pheromones")
            taumax = 1.0 / cast(ObjectiveBound, bestobj)
            taumin = taumax / a
            tau0 = taumax
            for k in tau:
                tau[k] = tau0
        logging.debug(f"Best solution so far (iteration {nc}): {bestobj}")
    logging.info(f"Number of iterations: {nc}")
    return best
