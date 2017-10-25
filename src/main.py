if __name__ == '__main__':
    import sys
    import SATProblem, SATSolver

    VERBOSE = False

    problem = SATProblem.SATProblem()
    problem.read_from_dimacs(f=sys.argv[1], verbose=VERBOSE)

    if len(sys.argv) == 3:
        f = sys.argv[2]
    else: f = None

    SATSolver.SATSolver(problem).solve(pruning=True, verbose=VERBOSE, f=f)
