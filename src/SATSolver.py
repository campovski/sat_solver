class SATSolver:
    def __init__(self, problem=None):
        self.problem = problem

    def solve(self, unit=False, pruning=False, simplify=False, f=None, verbose=False):
        assert self.problem.__class__.__name__ == 'SATProblem', \
            'Problem must be of type SATProblem. type(problem) = {}'.format(self.problem.__class__.__name__)

        print '[OK] Started solving ...'

        unknown = False

        if f:
            orig_stdout = sys.stdout
            fout = open(f, 'w')
            sys.stdout = fout

        if unit and pruning and simplify:
            self.__dpll(verbose=verbose)
            print self.problem.solution
        elif not unit and pruning and not simplify:
            self.__backtracking(verbose=verbose)
            print self.problem.solution
        elif not unit and not pruning and not simplify:
            self.__backtracking_naive(verbose=verbose)
            print self.problem.solution
        else:
            unknown = True

        if f:
            sys.stdout = orig_stdout
            fout.close()

        if unknown:
            print 'Unsupported combination (unit, pruning, simplify)!'
            return
        print '[DONE]'


    def __backtracking_naive(self, verbose=False):

        def evaluate_clause(clause, assignment):
            for literal in clause:
                if ( literal & 1 == 0 and assignment[literal/2] ) or \
                    ( literal & 1 and assignment[literal/2] == False ):
                    return True
            return False

        def evaluate_problem(problem, assignment, verbose):
            for i in range(problem.nbclauses):
                clause_evaluation = evaluate_clause(clause=problem.clauses[i], assignment=assignment)
                if verbose:
                    print 'Clause {0} eval to {1}'.format(problem.clauses[i], clause_evaluation)
                if not clause_evaluation:
                    return False
            return True

        assignment = [None for _ in range(self.problem.nbvars)]
        current_position = 0
        while True:
            if verbose:
                print '\ncurrent_position = ' + str(current_position)
            if current_position < 0:
                # we have backtracked the var on index 0, meaning no
                # satisfying assignment was found
                self.problem.solution = [0]
                return

            if assignment[current_position] is None:
                assignment[current_position] = False
            elif assignment[current_position] == False:
                assignment[current_position] = True
            else: # need to backtrack
                if verbose:
                    print 'Backtracking...'
                assignment[current_position] = None
                current_position -= 1
                continue

            problem_evaluation = evaluate_problem(self.problem, assignment=assignment, verbose=verbose)

            if verbose:
                print '{0} => {1}'.format(assignment, problem_evaluation)

            # if assignment satisfies all clauses, we have found a solution
            if problem_evaluation:
                self.problem.solution = assignment
                return

            if current_position < self.problem.nbvars - 1:
                current_position += 1


    def __backtracking(self, verbose=False):

        def evaluate_clause(clause, assignment):
            falsified = 0
            for literal in clause:
                if ( literal & 1 == 0 and assignment[literal/2] ) or \
                    ( literal & 1 and assignment[literal/2] == False ):
                    return True
                if ( literal & 1 and assignment[literal/2] ) or \
                    ( literal & 1 == 0 and assignment[literal/2] == False ):
                    falsified += 1
            if falsified == len(clause):
                return False
            return None

        def evaluate_problem(problem, assignment, verbose):
            correct = 0
            for i in range(problem.nbclauses):
                clause_evaluation = evaluate_clause(clause=problem.clauses[i], assignment=assignment)
                if verbose:
                    print 'Clause {0} eval to {1}'.format(problem.clauses[i], clause_evaluation)
                if clause_evaluation:
                    correct += 1
                elif clause_evaluation == False:
                    return False
            if correct == problem.nbclauses:
                return True
            return None

        assignment = [None for _ in range(self.problem.nbvars)]
        current_position = 0
        while True:
            if verbose:
                print '\ncurrent_position = ' + str(current_position)
            if current_position < 0:
                # we have backtracked the var on index 0, meaning no
                # satisfying assignment was found
                self.problem.solution = [0]
                return

            if assignment[current_position] is None:
                assignment[current_position] = False
            elif assignment[current_position] == False:
                assignment[current_position] = True
            else: # need to backtrack
                if verbose:
                    print 'Backtracking...'
                assignment[current_position] = None
                current_position -= 1
                continue

            problem_evaluation = evaluate_problem(self.problem, assignment=assignment, verbose=verbose)

            if verbose:
                print '{0} => {1}'.format(assignment, problem_evaluation)

            if problem_evaluation: # if assignment satisfies all clauses, we have found a solution
                self.problem.solution = assignment
                return
            elif problem_evaluation == False: # if assignment falsifies a clause, we can prune
                if verbose:
                    print 'Pruning'
                continue

            if current_position < self.problem.nbvars - 1:
                current_position += 1
