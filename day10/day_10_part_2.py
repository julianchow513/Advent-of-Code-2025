import numpy as np

from common.MultiThreadSum import MultiThreadSum
from common.Utils import main
from day10.Utils import CounterParser


class LeastCounterButtonPressFinder:

    @staticmethod
    def run(input: tuple[list[list[int]], list[int]]) -> int:
        tpe = MultiThreadSum()

        return tpe.exec(LeastCounterButtonPressFinder._find_presses_wrapper, input)

    @staticmethod
    def _find_presses_wrapper(input: tuple[np.ndarray, np.ndarray]) -> int:
        A, T = input
        solver = Solver(A, T)
        return solver.solve()


class Solver:

    def __init__(self, A, T):
        # A and T are already Python lists of ints
        self.A = A
        self.T = T
        self.m = len(self.A)
        self.n = len(self.A[0]) if self.m > 0 else 0

    def solve(self) -> int:
        from z3 import Optimize, Int
        import numpy as np
        from scipy.optimize import linprog

        c = [1] * self.n
        bounds = [(0, None)] * self.n
        res = linprog(
            c,
            A_eq=np.array(self.A, dtype=float),
            b_eq=np.array(self.T, dtype=float),
            bounds=bounds,
            method="highs",
        )

        if not res.success:
            raise RuntimeError("LP relaxation failed")

        lp_lower_bound = int(np.ceil(res.fun))

        opt = Optimize()
        x_vars = [Int(f"x{i}") for i in range(self.n)]

        for xi in x_vars:
            opt.add(xi >= 0)

        for row_idx in range(self.m):
            expr = sum(self.A[row_idx][j] * x_vars[j] for j in range(self.n))
            opt.add(expr == self.T[row_idx])

        total_sum = sum(x_vars)
        opt.minimize(total_sum)
        opt.add(total_sum >= lp_lower_bound)

        if opt.check() != "sat":
            raise RuntimeError("No integer solution found")

        model = opt.model()
        return sum(model[xi].as_long() for xi in x_vars)


if __name__ == "__main__":
    main(CounterParser, LeastCounterButtonPressFinder, test=True)
