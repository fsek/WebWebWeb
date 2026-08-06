from collections import deque
from datetime import datetime, timezone
from ortools.sat.python import cp_model
from fastapi import HTTPException
from api_schemas.enclose_moose_level_schema import EncloseMooseLevelCreate, EncloseMooseLevelUpdate
from db_models.enclose_moose_level_model import EncloseMooseLevel_DB
from db_models.enclose_moose_submission_model import EncloseMooseSubmission_DB


class EncloseGrid:
    def __init__(self, encoded_grid: str, wall_budget: int):
        self.wall_budget = wall_budget

        if wall_budget < 0:
            raise HTTPException(400, detail="Wall budget must not be negative")

        self.grid_string = encoded_grid.replace("\n", "")
        self.N = len(self.grid_string)

        if self.N <= 1:
            raise HTTPException(400, detail="Level must be bigger than one square")

        for tile in encoded_grid:
            if tile not in ("\n", ".", "~", "H", "C", "G", "S") and not tile.isnumeric():
                raise HTTPException(400, detail=f'Level contained unknown encoding: "{tile}"')

        if "H" not in encoded_grid:
            raise HTTPException(400, detail='Level must contain a moose ("H")')

        if "\n" not in encoded_grid:
            raise HTTPException(400, detail="Level must be rectangular")

        self.grid_width = encoded_grid.index("\n")
        self.grid_height = self.N // self.grid_width

        if len(set(map(len, encoded_grid.split("\n")))) != 1:
            raise HTTPException(400, detail="Level must be rectangular")

        self.moose_index = self.grid_string.index("H")

        self.portals: dict[str, set[int]] = {}
        for flat_index, tile in enumerate(self.grid_string):
            if tile.isnumeric():
                self.portals.setdefault(tile, set()).add(flat_index)

    def get_neighbors(self, flat_index: int):
        row_index, column_index = divmod(flat_index, self.grid_width)
        neighbors: set[int] = set()
        if column_index != 0:
            neighbors.add(flat_index - 1)
        if column_index != self.grid_width - 1:
            neighbors.add(flat_index + 1)
        if row_index != 0:
            neighbors.add(flat_index - self.grid_width)
        if row_index != self.grid_height - 1:
            neighbors.add(flat_index + self.grid_width)

        tile = self.grid_string[flat_index]
        if tile in self.portals:
            for flat_index_portal in self.portals[tile]:
                if flat_index_portal != flat_index:
                    neighbors.add(flat_index_portal)

        return neighbors

    def is_boundary(self, flat_index: int):
        row, col = divmod(flat_index, self.grid_width)

        return row == 0 or col == 0 or row == self.grid_height - 1 or col == self.grid_width - 1

    def score_tile(self, tile: str):
        bonus_score_dict = {"C": 3, "G": 10, "S": -5}
        bonus_score = 1 + bonus_score_dict.get(tile, 0)

        return bonus_score

    def find_optimal_solution(self):
        # Algorithm inspired by https://dynomight.substack.com/p/horse, https://blog.macuyiko.com/post/2026/solving-enclosehorse-with-cp-sat.html and Gemini

        model = cp_model.CpModel()

        w = [model.new_bool_var(f"w_{i}") for i in range(self.N)]  # Whether wall is present
        e = [model.new_bool_var(f"r_{i}") for i in range(self.N)]  # Whether the tile is enclosed

        never_enclosed_indices: set[int] = set()
        for flat_index, tile in enumerate(self.grid_string):
            if tile == "~" or self.is_boundary(flat_index):
                model.add(e[flat_index] == 0)  # Water or boundary tiles cannot be enclosed
                never_enclosed_indices.add(flat_index)

            if tile != ".":
                model.add(w[flat_index] == 0)  # Non-grass tiles cannot have walls

            model.add(e[flat_index] + w[flat_index] <= 1)  # A tile cannot be both enclosed and have a wall

        model.add(e[self.moose_index] == 1)  # Moose must be enclosed

        model.add(sum(w) <= self.wall_budget)  # Enforce wall budget

        d = [model.new_int_var(0, self.N, f"d_{i}") for i in range(self.N)]  # Distance from moose
        model.add(d[self.moose_index] == 0)  # Moose is at distance 0 from moose.

        for flat_index, tile in enumerate(self.grid_string):
            if flat_index in never_enclosed_indices:
                continue

            parents: list[cp_model.IntVar] = []
            for neighbor_index in self.get_neighbors(flat_index):
                if self.grid_string[neighbor_index] == "~":
                    continue

                model.add(
                    e[flat_index] <= e[neighbor_index] + w[neighbor_index]
                )  # If a tile is enclosed, its neighbor must either also be enclosed or have a wall

                if flat_index != self.moose_index:
                    p_var = model.new_bool_var(
                        f"p_{neighbor_index}_{flat_index}"
                    )  # Whether neighbor_index is parent of flat_index
                    parents.append(p_var)

                    model.add_implication(p_var, e[neighbor_index])  # A parent must be an enclosed tile
                    model.add(d[flat_index] == d[neighbor_index] + 1).only_enforce_if(  # pyright: ignore
                        p_var
                    )  # Distance increases to prevent cycles (isolated enclosed areas)

            if flat_index != self.moose_index:
                if parents:
                    model.add(sum(parents) == e[flat_index])  # If a tile is enclosed, it has exactly one parent
                else:
                    model.add(e[flat_index] == 0)  # If completely surrounded by water, it cannot be enclosed

        enclosed_score = [self.score_tile(tile) * e[flat_index] for flat_index, tile in enumerate(self.grid_string)]
        model.maximize(sum(enclosed_score))

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 15
        solver.parameters.num_search_workers = 8

        status = solver.solve(model)
        # print(f"Solving took {solver.wall_time} seconds")

        if status not in (cp_model.INFEASIBLE, cp_model.OPTIMAL):
            raise HTTPException(
                400,
                detail=f"Level could not be solved, likely because it exceeded the time limit (solver status: {solver.status_name(status)})",
            )

        if status == cp_model.INFEASIBLE:
            raise HTTPException(400, detail="Level is unsolvable")

        score = int(solver.objective_value)
        wall_indices = set(i for i in range(self.N) if solver.value(w[i]) == 1)

        model.add_bool_or(
            [w[i].Not() for i in wall_indices] + [w_i for i, w_i in enumerate(w) if i not in wall_indices]
        )
        status2 = solver.solve(model)
        if status2 == cp_model.OPTIMAL:
            solution_is_unique = int(solver.objective_value) != score
        elif status2 == cp_model.INFEASIBLE:
            solution_is_unique = True
        else:
            solution_is_unique = None

        """  # Some debug visualisations
        import numpy as np

        e_sol = np.array([solver.value(e[i]) for i in range(self.N)])

        np.set_printoptions(linewidth=1000)
        print("MAP")
        grid: list[list[str]] = []
        for flat_index, tile in enumerate(self.grid_string):
            if flat_index % self.grid_width == 0:
                grid.append([])

            if flat_index in wall_indices:
                grid[-1].append("W")
            else:
                grid[-1].append(tile)
        print(np.array(grid).reshape((self.grid_height, self.grid_width)))

        print("REGION")
        print(e_sol.reshape((self.grid_height, self.grid_width)))
        print("SCORES")
        print(
            (e_sol * np.array(list(map(self.score_tile, self.grid_string))))
            .astype(int)
            .reshape((self.grid_height, self.grid_width))
        )
        """

        return score, wall_indices, solution_is_unique

    def score_solution(self, solution: set[int]):
        if len(solution) > self.wall_budget:
            raise HTTPException(400, "The solution contained too many walls")

        for wall_index in solution:
            if wall_index < 0 or wall_index > self.N - 1:
                raise HTTPException(400, f"The solution contained a wall that was of out bounds ({wall_index})")

            if self.grid_string[wall_index] != ".":
                raise HTTPException(400, f"The solution contained a wall placed on non-grass ({wall_index})")

        queue: deque[int] = deque()
        visited: set[int] = set()
        score = 0

        queue.append(self.moose_index)
        visited.add(self.moose_index)

        while queue:
            current_index = queue.popleft()
            score += self.score_tile(self.grid_string[current_index])

            for neighbor_index in self.get_neighbors(current_index):
                is_visited = neighbor_index in visited
                if is_visited:
                    continue

                visited.add(neighbor_index)

                is_blocked = self.grid_string[neighbor_index] == "~" or neighbor_index in solution
                if is_blocked:
                    continue

                is_escaped = self.is_boundary(neighbor_index)
                if is_escaped:
                    raise HTTPException(400, detail="The solution does not enclose the moose")

                queue.append(neighbor_index)

        return score  # len(visited) + bonus score


def level_create(data: EncloseMooseLevelCreate):
    grid = EncloseGrid(data.encoded_grid, data.wall_budget)
    optimal_score, optimal_solution, optimal_is_unique = grid.find_optimal_solution()

    level = EncloseMooseLevel_DB(
        release_date=data.release_date,
        day_index=data.day_index,
        name=data.name,
        encoded_grid=data.encoded_grid,
        wall_budget=data.wall_budget,
        optimal_score=optimal_score,
        optimal_solution=list(optimal_solution),
        optimal_is_unique=optimal_is_unique,
    )

    return level


def level_update(level: EncloseMooseLevel_DB, data: EncloseMooseLevelUpdate):
    updates = data.model_dump(exclude_unset=True)

    used_encoded_grid = updates.get("encoded_grid", level.encoded_grid)
    used_wall_budget = updates.get("wall_budget", level.wall_budget)
    if used_encoded_grid != level.encoded_grid or used_wall_budget != level.wall_budget:
        level.submissions.clear()

        grid = EncloseGrid(used_encoded_grid, used_wall_budget)
        optimal_score, optimal_solution, optimal_is_unique = grid.find_optimal_solution()

        updates["optimal_score"] = optimal_score
        updates["optimal_solution"] = list(optimal_solution)
        updates["optimal_is_unique"] = optimal_is_unique

    for var, value in updates.items():
        setattr(level, var, value)

    return level


def solution_submit(level: EncloseMooseLevel_DB, solution: set[int], player_id: int):
    grid = EncloseGrid(level.encoded_grid, level.wall_budget)
    player_score = grid.score_solution(solution)

    db_submission = EncloseMooseSubmission_DB(
        level_id=level.level_id,
        submission_time=datetime.now(timezone.utc),
        player_id=player_id,
        player_score=player_score,
        player_solution=list(solution),
    )

    return db_submission
