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
