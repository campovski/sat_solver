if __name__ == '__main__':
    import sys
    import SATProblem, SATSolver

    problem = SATProblem.SATProblem()
    problem.read_from_dimacs(sys.argv[1])
    print problem

    SATSolver.SATSolver(problem).solve(pruning=True, verbose=True)
