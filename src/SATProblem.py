class SATProblem:
    def __init__(self):
        self.nbvars = 0
        self.nbclauses = 0
        self.vars = []
        self.clauses = []
        self.solution = None


    def __str__(self):
        string = ''
        for clause in self.clauses:
            string += ' '.join([str(l) for l in clause]) + '\n'
        return string


    def _print_in_dimacs(self, f=None):
        if f:
            orig_stdout = sys.stdout
            fout = open(f, 'w')
            sys.stdout = fout

        print 'p cnf {0} {1}'.format(self.nbvars, self.nbclauses)
        for clause in self.clauses:
            print ' '.join(('-' if l & 1 else '') + str(l/2 + 1) for l in clause) + ' 0'

        if f:
            sys.stdout = orig_stdout
            fout.close()


    def __add_clause(self, string): # clause is a string like '3 1 -4 2 0'
        clause = []
        for literal in string.split()[:-1]:
            transcribed_literal = 2 * (abs(int(literal)) - 1) + (literal[0] == '-')
            clause.append(transcribed_literal)
            self.vars[transcribed_literal] = True
        self.clauses.append(clause)


    def read_from_dimacs(self, f):
        print '[OK] Starting read_from_dimacs...'

        with open(f, 'r') as f:
                for line in f:
                    if line[0] == 'c':
                        continue
                    if line[0] == 'p':
                        _, _, nbvars, nbclauses = line.strip().split()
                        self.nbvars = int(nbvars)
                        self.nbclauses = int(nbclauses)
                        self.vars = [False for _ in range(2*self.nbvars)]
                        continue
                    self.__add_clause(line.strip())

        assert self.nbvars > 0, '[ERROR] self.nbvars > 0: self.nbvars = {}'.format(self.nbvars)
        assert len(self.clauses) == self.nbclauses, '[ERROR] len(self.clauses) does not match self.nbclauses:\
            len(self.clauses) = {0}, self.nbclauses = {1}'.format(len(self.clauses), self.nbclauses)
        print '[OK] Success: read_from_dimacs'


    def solve(self, method='naive', f=None, verbose=False):
        assert method in ['naive', 'dpll'], '[ERROR] Unrecognized method for solving SAT.\n\
                Possible method values: (\'naive\'), \'dpll\'.'
        print '[OK] Started solving ...'
        if f:
            orig_stdout = sys.stdout
            fout = open(f, 'w')
            sys.stdout = fout

        if method == 'naive':
            self.__backtracking_naive(verbose=verbose)
            print self.solution
        elif method == 'dpll':
            self.__dpll(verbose=verbose)
            print self.solution

        if f:
            sys.stdout = orig_stdout
            fout.close()

        print '[DONE]'


    def evaluate_clause(self, index, assignment):
        for literal in self.clauses[index]:
            if ( literal & 0 and assignment[literal/2] ) or \
                ( literal & 1 and assignment[literal/2] == False ):
                return True
        return False


    def evaluate_problem(self, assignment, verbose):
        for i in range(self.nbclauses):
            if verbose:
                print 'Testing clause\t' + str(i)
            if not self.evaluate_clause(index=i, assignment=assignment):
                return False
        return True


    def __backtracking_naive(self, verbose=False):
        assignment = [None for _ in range(self.nbvars)]
        current_position = 0
        while True:
            if verbose:
                print '\n\ncurrent_position = ' + str(current_position)
            if current_position < 0:
                # we have backtracked the var on index 0, meaning no
                # satisfying assignment was found
                self.solution = [0]
                return

            if assignment[current_position] is None:
                assignment[current_position] = False
            elif assignment[current_position] == False:
                assignment[current_position] = True
            else: # need to backtrack
                assignment[current_position] = None
                current_position -= 1
                continue

            # if assignment satisfies all clauses, we have found a solution
            if self.evaluate_problem(assignment=assignment, verbose=verbose):
                self.solution = assignment
                return

            if current_position < self.nbvars - 1:
                current_position += 1


    def __dpll(self, verbose=False):
        pass
