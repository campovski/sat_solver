if __name__ == '__main__':
    import sys
    import SATProblem

    problem = SATProblem.SATProblem()
    problem.read_from_dimacs(sys.argv[1])

    problem.solve(verbose=True)
