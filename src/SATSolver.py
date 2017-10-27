import sys

class SATSolver:
    def __init__(self, problem=None):
        self.problem = problem

    def solve(self, unit=False, pruning=False, simplify=False, f=None, verbose=False):
        assert self.problem.__class__.__name__ == 'SATProblem', \
                'Problem must be of type SATProblem. type(problem) = {}'.format(self.problem.__class__.__name__)

        if verbose:
            print '[OK] Started solving ...'

        if unit and pruning and simplify:
            self.__dpll(verbose=verbose)
        elif simplify:
            self.__backtracking_simplify(verbose=verbose)
        elif not unit and pruning and not simplify:
            self.__backtracking(verbose=verbose)
        elif not unit and not pruning and not simplify:
            self.__backtracking_naive(verbose=verbose)

        if f:
            orig_stdout = sys.stdout
            fout = open(f, 'w')
            sys.stdout = fout

        if self.problem.solution == [0]:
            print 0
        else:
            output = ''
            for i in range(self.problem.nbvars):
                if self.problem.solution[i]:
                    output += str(i+1)
                elif self.problem.solution[i] == False:
                    output += '-' + str(i+1)
                if i < self.problem.nbvars - 1:
                    output += ' '
            print output
            #print ' '.join([str(i+1) if self.problem.solution[i] elif '-{}'.format(i+1) \
            #    for i in range(len(self.problem.solution))])

        if f:
            sys.stdout = orig_stdout
            fout.close()

        if verbose:
            print '[DONE]'


    def __backtracking_naive(self, verbose):

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
        current_depth = 0
        while True:
            if verbose:
                print '\ncurrent_depth = ' + str(current_depth)
            if current_depth < 0:
                # we have backtracked the var on index 0, meaning no
                # satisfying assignment was found
                self.problem.solution = [0]
                return

            if assignment[current_depth] is None:
                assignment[current_depth] = False
            elif assignment[current_depth] == False:
                assignment[current_depth] = True
            else: # need to backtrack
                if verbose:
                    print 'Backtracking...'
                assignment[current_depth] = None
                current_depth -= 1
                continue

            problem_evaluation = evaluate_problem(self.problem, assignment=assignment, verbose=verbose)

            if verbose:
                print '{0} => {1}'.format(assignment, problem_evaluation)

            # if assignment satisfies all clauses, we have found a solution
            if problem_evaluation:
                self.problem.solution = assignment
                return

            if current_depth < self.problem.nbvars - 1:
                current_depth += 1


    def __backtracking(self, verbose):

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
        current_depth = 0
        while True:
            if verbose:
                print '\ncurrent_depth = ' + str(current_depth)
            if current_depth < 0:
                # we have backtracked the var on index 0, meaning no
                # satisfying assignment was found
                self.problem.solution = [0]
                return

            if assignment[current_depth] is None:
                assignment[current_depth] = False
            elif assignment[current_depth] == False:
                assignment[current_depth] = True
            else: # need to backtrack
                if verbose:
                    print 'Backtracking...'
                assignment[current_depth] = None
                current_depth -= 1
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

            if current_depth < self.problem.nbvars - 1:
                current_depth += 1


    def __backtracking_simplify(self, verbose):

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

        def evaluate_problem(problem, assignment, depth, verbose):
            correct = 0
            for i in range(problem.nbclauses):
                if depth < self.depth_of_disablement[i]:
                    clause_evaluation = evaluate_clause(clause=problem.clauses[i], assignment=assignment)
                    if verbose:
                        print 'Clause {0} eval to {1}'.format(problem.clauses[i], clause_evaluation)
                    if clause_evaluation:
                        correct += 1
                        self.depth_of_disablement[i] = depth
                    elif clause_evaluation == False:
                        return False
                else:
                    correct += 1
            if correct == problem.nbclauses:
                return True
            return None

        assignment = [None for _ in range(self.problem.nbvars)]
        # if current_depth > depth_of_disablement[i], than that means that
        # i-th clause is disabled, meaning we don't need to check it because
        # it has already been satisfied
        self.depth_of_disablement = [self.problem.nbvars for _ in range(self.problem.nbclauses)]
        current_depth = 0
        while True:
            if verbose:
                print '\ncurrent_depth = ' + str(current_depth)
                print self.depth_of_disablement

            if current_depth < 0:
                # we have backtracked the var on index 0, meaning no
                # satisfying assignment was found
                self.problem.solution = [0]
                return

            if assignment[current_depth] is None:
                assignment[current_depth] = False
            elif assignment[current_depth] == False:
                assignment[current_depth] = True
            else: # need to backtrack
                if verbose:
                    print 'Backtracking...'
                assignment[current_depth] = None
                current_depth -= 1
                self.depth_of_disablement[:] = [d if d < current_depth else self.problem.nbvars for d in range(self.problem.nbclauses)]
                continue

            problem_evaluation = evaluate_problem(self.problem, assignment=assignment, depth=current_depth, verbose=verbose)

            if verbose:
                print '{0} => {1}'.format(assignment, problem_evaluation)

            if problem_evaluation: # if assignment satisfies all clauses, we have found a solution
                self.problem.solution = assignment
                return
            elif problem_evaluation == False: # if assignment falsifies a clause, we can prune
                if verbose:
                    print 'Pruning'
                self.depth_of_disablement[:] = [d if d < current_depth else self.problem.nbvars for d in range(self.problem.nbclauses)]
                continue

            if current_depth < self.problem.nbvars - 1:
                current_depth += 1


    def __dpll(self, verbose):
        pass
