# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from collections import deque

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.csp = CSP(puzzle)

    def solve(self):
        # print("BEFORE")
        # self.printKeyVal(self.csp.domains)
        self.AC3(self.csp)
        # print("AFTER")
        # self.printKeyVal(self.csp.currDomains)
        assignment = self.backtrackingSearch(self.csp)
        if not assignment:
            return False
        for (i, j) in assignment:
            self.ans[i][j] = assignment[(i, j)]
        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.


    def AC3(self, csp):
        arc_q = deque()
        for cons in csp.constraints:
            arc_q.append(cons)
        csp.regenerateCurrDomains()
        while arc_q:
            (xi, xj) = arc_q.popleft()
            if self.revise(csp, xi, xj):
                if not csp.currDomains[xi]:
                    return False
                for xk in csp.neighbours[xi]:
                    if xk != xj:
                        arc_q.append((xk, xi))
        return True

    def revise(self, csp, xi, xj):
        revised = False
        # print(xi, xj)
        for x in csp.currDomains[xi].copy():
            if all(map(lambda y : csp.constraints[(xi, xj)](x, y), csp.currDomains[xj])):
                csp.currDomains[xi].remove(x)
        return revised

    def backtrackingSearch(self, csp):
        return self.backtrack(csp)
    
    def backtrack(self, csp, assignment = dict()):
        # self.printAssignment(assignment)
        # print("\n")
        # self.writeAssignment(assignment)
        if self.complete(assignment):
            return assignment
        var = self.selectUnassignedVariable(csp, assignment)
        for value in self.orderDomainValue(var, assignment, csp):
            if self.isConsistent(var, value, assignment):
                assignment[var] = value
                var.value = value
                removals = csp.updateCurrDomains(var, value)
                # inferences = self.inference(csp, var, value)
                # if not inferences:
                    # add inferences to assignment
                result = self.backtrack(csp, assignment)
                if result:
                    return result
                csp.restoreCurrDomain(var, removals)
        # print(var)
        # print(csp.currDomains[var])

        # self.writeLine(var.coordinate)
        # self.writeLine(csp.currDomains[var])

        # self.printAssignment(assignment)
        # print("\n")
        if var in assignment:
            del assignment[var]
            var.value = 0
        # del inferences from assignment
        return False

    def isConsistent(self, var1, value, assignment):
        return not any(map(lambda var2 : var1.isSameUnit(var2) and assignment[var2] == value, assignment))

    def complete(self, assignment):
        return len(assignment) == 81
    
    def selectUnassignedVariable(self, csp, assignment):
        ''' using minimum remaining values '''
        # Maintain a PQ in csp might be more efficient
        lst = sorted(list(filter(lambda var: var not in assignment, csp.variables)), key = lambda var : len(csp.currDomains[var]))
        return lst[0]
    
    def orderDomainValue(self, var, assignment, csp):
        ''' using least constraining values '''
        # lst = sorted(list(var.domain), key = csp.variables.numConstrainingValues)
        lst = list(csp.currDomains[var])
        return lst

    def inference(self, csp, var, value):
        return 0

    def numConflict(self, var, value, assignment):
        return 

    def printKeyVal(self, cspAttr):
        for key, value in cspAttr.items():
            print(key, value)

    def printAssignment(self, assignment):
        lst = [[0 for i in range(9)] for j in range(9)]
        for var in assignment:
            lst[var.coordinate[0]][var.coordinate[1]] = assignment[var]
        for line in lst:
            print(line)
    
    def writeAssignment(self, assignment):
        lst = [[0 for i in range(9)] for j in range(9)]
        for var in assignment:
            lst[var.coordinate[1]][var.coordinate[0]] = assignment[var]
        outfile.write("---------------------------\n")
        for line in lst:
            outfile.write(str(line))
            outfile.write("\n")
    
    def writeLine(self, item):
        outfile.write(str(item))
        outfile.write("\n")

class CSP(object):
    def __init__(self, puzzle):
        self.variables = list()  # set of var (tuple representing indexes)
        
        self.domains = dict()   # key = var, value = var_domain (set)
        self.neighbour = dict() # key = var, value = var_neighbour (set)
        # TODO change AC3 and backtrack

        # set of binary constraints (constraint function involving two var) represented by pair(scope, relation)
        # scope = (x, y), relation = f(x, y), where x, y are vars
        self.constraints = dict()
        self.initialiseCSP(puzzle)
        # for var in self.variables:
        #     print(var.coordinate, var.value)
        self.currDomains = dict()
        return

    def initialiseCSP(self, puzzle):
        # going through 2d list
        for i in range(9):
            for j in range(9):
                self.variables.append(Variable((j,i), puzzle[i][j]))
        
        # going through var set
        for var1 in self.variables:
            self.domains[var1] = {1, 2, 3, 4, 5, 6, 7, 8, 9} if not var1.value else {var1.value}
            self.neighbour[var1] = set()
            for var2 in self.variables:
                if var1 != var2 and var1.isSameUnit(var2):
                    # print(var1, var2)
                    self.constraints[(var1, var2)] = self.conflict
                    self.neighbour[var1].add(var2)
                    var1.neighbour.add(var2)
        # print("Constraint\n")
        # for (var1, var2) in self.constraints:
        #     print(var1, var2)
        return

    def conflict(self, var1, var2):
        ''' var1 and var2 are in conflict when they having same value,
        only comparing vars in same unit (represent by arc) '''
        return var1 == var2

    def regenerateCurrDomains(self):
        ''' Create a copy of domains as currDomains '''
        # self.currDomains = dict()
        if not self.currDomains:
            for var in self.domains:
                self.currDomains[var] = {i for i in self.domains[var]}
        return

    def updateCurrDomains(self, var, value):
        self.regenerateCurrDomains()
        removals = list(filter(lambda val : val != value, self.currDomains[var]))
        self.currDomains[var] = set([value])
        return removals

    def restoreCurrDomain(self, var, removals):
        for r in removals:
            self.currDomains[var].add(r)
        return

class Variable(object):
    def __init__(self, coordinate, value):
        self.coordinate = coordinate    # (x, y)
        self.value = value
        # self.domain = {1, 2, 3, 4, 5, 6, 7, 8, 9} if not value else {value}
        self.neighbour = set()
        self.degree = len(self.neighbour)
        return

    def __hash__(self):
        return hash(self.coordinate)

    def __eq__(self, var):
        return self.coordinate == var.coordinate

    def __str__(self):
        return str(self.coordinate)

    def isSameUnit(self, var):
        return self.isSameRow(var) or self.isSameCol(var) or self.isSameSquare(var) 

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
    outfile = open("temp.txt", "w")
    sudoku = Sudoku(puzzle)
    ans = sudoku.solve()
    outfile.close()
    print(ans)
    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
