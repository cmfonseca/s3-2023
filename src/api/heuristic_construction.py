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

from typing import TypeVar, Protocol, Optional

Component = TypeVar('Component')

class SolutionProtocol(Protocol[Component]):
    def heuristic_add_move(self) -> Optional[Component]: ...
    def add(self, component: Component) -> None: ...

Solution = TypeVar('Solution', bound=SolutionProtocol)

def heuristic_construction(solution: Solution) -> Solution:
    c = solution.heuristic_add_move()
    while c is not None:
        solution.add(c)
        c = solution.heuristic_add_move()
    return solution
