from linopy import Model

from common.MultiThreadSum import MultiThreadSum
from common.Utils import main
from day10.Utils import CounterParser


class LeastCounterButtonPressFinder:

    @staticmethod
    def run(input: list[tuple[list[list[int]], list[int]]]) -> int:
        tpe = MultiThreadSum()

        return tpe.exec(LeastCounterButtonPressFinder._find_presses_wrapper, input)

    @staticmethod
    def _find_presses_wrapper(input: tuple[list[list[int]], list[int]]) -> int:
        A, T = input
        solver = Solver(A, T)
        return solver.solve()


class Solver:

    def __init__(self, A, T):
        self.A = A
        self.T = T
        self.m = len(self.A)
        self.n = len(self.A[0]) if self.m > 0 else 0
        self.model = Model()

    def solve(self) -> int:
        x = self.model.add_variables(
            lower=[0 for _ in range(self.n)], name="x", integer=True
        )
        for i in range(self.m):

            self.model.add_constraints(
                sum(self.A[i][j] * x[j] for j in range(self.n)) == self.T[i]
            )

        self.model.add_objective(x.sum())
        self.model.solve(solver_name="highs", quiet=True)

        return int(
            self.model.objective.value,
        )


if __name__ == "__main__":
    main(CounterParser, LeastCounterButtonPressFinder, test=False)
