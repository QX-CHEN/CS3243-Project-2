# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.csp = CSP(puzzle)

    def solve(self):
        assignment = self.csp.backtrackSearch(self.csp.domains.copy())
        for var in assignment:
            (i, j) = var.coordinate
            self.ans[i][j] = assignment[var]
        # self.ans is a list of lists
        return self.ans

class CSP(object):
    def __init__(self, puzzle):
        self.variables = list()
        self.units = dict()
        self.neighbors = dict()
        self.domains = dict()
        self.initialiseCSP(puzzle)
        self.calculateDomain()
        
    def initialiseCSP(self,puzzle):
        for i in range(9):
            for j in range(9):
                self.variables.append(Variable((i, j), puzzle[i][j]))

        for var1 in self.variables:
            self.units[var1] = [[],[],[]] # col, row, square
            self.neighbors[var1] = set() # add in variables which belongs to the same unit
            self.domains[var1] = "123456789" # initialising domain
            for var2 in self.variables:
                if var1.isSameCol(var2):
                    self.units[var1][0].append(var2)
                    if var1 != var2:
                        self.neighbors[var1].add(var2)

                if var1.isSameRow(var2):
                    self.units[var1][1].append(var2)
                    if var1 != var2:
                        self.neighbors[var1].add(var2)

                if var1.isSameSquare(var2):
                    self.units[var1][2].append(var2)
                    if var1 != var2:
                        self.neighbors[var1].add(var2)

    def calculateDomain(self):
        # Sets each variables' domain
        for var in self.variables:
            if var.value != '0':
                self.assign(self.domains, var, var.value)
        return self.domains

    def assign(self, domains, var, val):
        temp = domains[var].replace(val, "")
        for delVal in temp:
            if not self.constraintsPropagation(domains, var, delVal):
                return False
        return domains

    def constraintsPropagation(self, domains, var, delVal):
        # check exists
        if delVal not in domains[var]:
            return domains
            
        # delete delVal from domains
        domains[var] = domains[var].replace(delVal, "")

        # when var can only take on a val, assign it
        if not len(domains[var]):
            return False
        elif len(domains[var]) == 1:
            delVal2 = domains[var] # edited by Hussain
            for neighbor in self.neighbors[var]:
                if not self.constraintsPropagation(domains, neighbor, delVal2):
                    return False
        
        # when only one var left in a unit for a val, assign it
        for u in self.units[var]:
            remainings = []
            for v in u:
                if delVal in domains[v]:
                    remainings.append(v)
            if not len(remainings):
                return False
            elif len(remainings) == 1:
                if not self.assign(domains, remainings[0], delVal):
                    return False
        return domains

    def backtrackSearch(self, domains):
        if domains is False:
            return False
        if self.checkSolved(domains):
            return domains
        var = self.mrv(domains)
        for d in domains[var]:
            result = self.backtrackSearch(self.assign(domains.copy(),var, d))
            if result:
                return result
        return False

    def checkSolved(self,domains):
        for var in self.variables:
            if len(domains[var]) != 1:
                return False
        return True
        
    def mrv(self, domains):
        # Minmum remaining values heuristic domains = {a: 1, b 123, c 12345} return b
        return min(self.variables,key=lambda var: len(domains[var])\
               if (len(domains[var]) > 1) else 10) 
               #if len(domain) == 1 then return 10 to ensure it is not minimum

class Variable(object):
    def __init__(self, coordinate, value):
        self.coordinate = coordinate    # (x, y)
        self.value = str(value)

    def __hash__(self):
        return hash(self.coordinate)

    def isSameRow(self, var):
        return self.coordinate[0] == var.coordinate[0]

    def isSameCol(self, var):
        return self.coordinate[1] == var.coordinate[1]

    def isSameSquare(self, var):
        ''' square refers to 3*3 square '''
        return (self.coordinate[0]//3, self.coordinate[1]//3) == (var.coordinate[0]//3, var.coordinate[1]//3)



if __name__ == "__main__":
    # STRICTLY do NOT modify the code in the main function here
    if len(sys.argv) != 3:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise ValueError("Wrong number of arguments!")

    try:
        f = open(sys.argv[1], 'r')
    except IOError:
        print ("\nUsage: python CS3243_P2_Sudoku_XX.py input.txt output.txt\n")
        raise IOError("Input file not found!")

    puzzle = [[0 for i in range(9)] for j in range(9)]
    lines = f.readlines()

    i, j = 0, 0
    for line in lines:
        for number in line:
            if '0' <= number <= '9':
                puzzle[i][j] = int(number)
                j += 1
                if j == 9:
                    i += 1
                    j = 0

    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()

    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
