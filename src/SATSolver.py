import sys
import SATProblem

"""
    SATSolver: Provides methods for solving SAT problems. Possible algorithms are
    naive backtracking, backtracking with pruning falsified trees, backtracking
    with pruning falsified trees and removing clauses that are true on certain
    depths, and DPLL.
    @param problem : A problem to be solved.
    @method solver : Solves the problem.
"""
class SATSolver:
    def __init__(self, problem=None):
        self.problem = problem


    """
        solve: Solves the problem of current object.
        @param unit : Unit propagation (DPLL)
        @param simplify : Backtracking with simplification
        @param pruning : Backtracking with pruning
        @param f : Print to file f
        @param verbose : Print progress to console
    """
    def solve(self, unit=False, pruning=False, simplify=False, f=None, verbose=False):
        assert self.problem.__class__.__name__ == 'SATProblem', \
                'Problem must be of type SATProblem. type(problem) = {}'.format(self.problem.__class__.__name__)

        if verbose:
            print '[OK] Started solving ...'

        if unit:
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
            for i in range(len(self.problem.solution)):
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

    """
        Naive backtracking algorithm.
    """
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


    """
        Backtracking with pruning.
    """
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


    """
        Backtracking with pruning and omiting checking the truthful clauses on
        current_depth and assignment.
    """
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


    """
        DPLL algorithm. Uses pruning with simplification and unit propagation.
    """
    def __dpll(self, verbose):

        def is_consistent(clauses, assignment):
            for clause in clauses:
                if len([l for l in clause if l in assignment]) == 0:
                    return False
            return True

        def complement(assignment):
            out = []
            for literal in assignment:
                if literal & 1 == 0:
                    out.append(literal+1)
                else:
                    out.append(literal-1)
            return out

        def falsified(clauses, assignment):
            complements = complement(assignment)
            for clause in clauses:
                if len([l for l in clause if l not in complements]) == 0:
                    return True
            return False

        def pure_literal_assignment(clauses, assignment):
            complements = complement(assignment)
            candidates = []
            for clause in clauses:
                if len([l for l in clause if l in assignment]) == 0:
                    candidates += [l for l in clause]
            candidatesComplements = complement(candidates)
            pures = [l for l in candidates if l not in candidatesComplements]
            for literal in pures:
                if literal not in assignment and literal not in complements:
                    return literal
            return -1

        def unit_propagation(clauses, assignment):
            complements = complement(assignment)
            for clause in clauses:
                remaining = [l for l in clauses if l not in complements]
                if len(remaining) == 1:
                    if remaining[0] not in assignment:
                        return remaining[0]
            return -1

        def get_new_atom(clauses, assignment):
            assPlusComp = assignment + complement(assignment)
            for clause in clauses:
                for literal in clause:
                    if literal not in assPlusComp:
                        return literal
            return -1

        def dpll_rec(clauses, assignment):
            if is_consistent(clauses, assignment):
                return assignment
            if falsified(clauses, assignment):
                return False
            pure = pure_literal_assignment(clauses, assignment)
            if pure != -1:
                return dpll_rec(clauses, assignment + [pure])
            unit = unit_propagation(clauses, assignment)
            if unit != -1:
                return dpll_rec(clauses, assignment + [unit])
            new_atom = get_new_atom(clauses, assignment)
            if new_atom != -1:
                new_atom = (new_atom / 2) * 2
                out = dpll_rec(clauses, assignment + [new_atom])
                if out:
                    return out
                else:
                    out = dpll_rec(clauses, assignment + [new_atom+1])
                    if out:
                        return out
                    else:
                        return False

        out = dpll_rec(self.problem.clauses, [])
        if out:
            for literal in out:
                self.problem.solution[literal/2] = literal & 1 == 0
        else:
            self.problem.solution = [0]
