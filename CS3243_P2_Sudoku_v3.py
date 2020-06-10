# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from random import shuffle
from time import time
from sortedcontainers import SortedSet
# from collections import defaultdict, Counter
# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.csp = CSP(puzzle)

    def solve(self):
        # self.ans is a list of lists
        return self.ans

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

class CSP():
    def __init__(self, puzzle):
        self.variables = set()
        self.domains = dict()
        self.neighbors = dict()
        self.rows = dict()
        self.cols = dict()
        self.squares = dict()
        self.initialiseCSP(puzzle)
        self.currDomain = dict()
    
    def initialiseCSP(self, puzzle):
        # going through 2d list
        for i in range(9):
            for j in range(9):
                self.variables.add(Variable((i, j), puzzle[i][j]))
        # going through var set
        for var1 in self.variables:
            self.domains[var1] = "123456789" if not var1.value else str(value)
            self.rows[var1] = []
            self.cols[var1] = []
            self.squares[var1] = []
            self.neighbors[var1] = []
            for var2 in self.variables:
                if var1 != var2:
                    if var1.isSameRow(var2):
                        self.rows[var1].append(var2)
                    if var1.isSameCol(var2):
                        self.cols[var1].append(var2)
                    if var1.isSameSquare(var2):
                        self.squares[var1].append(var2)
                    if var1.isSameUnit(var2):
                        self.neighbors[var1].append(var2)

    def assign(self):
        return

    def constraintsPropagation(self):
        return

    def backtrackSearch(self, domains):
        if domains is False:
            return False
        if self.checkSolved(domains):
            return domains
        var = self.mrv(domains)
        # return self.anyPossibleSequence(self.backtrackSearch( \
        #     self.assign(domains.copy(),var, d)) for d in domains[var])
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
        # Minmum remaining values heuristic domains = {a: 1, b 123, c 12345} b
        #return min((var) for var in self.variables if len(domains[var])>1, key = len(domains[var]))
        return min(self.variables,key=lambda var: len(domains[var]) if (len(domains[var]) > 1) else 99)
    def anyPossibleSequence(self, sequence):
        # Returns the element if it is not false
        for elem in sequence:
            if elem:
                return elem
        return False

class Variable(object):
    def __init__(self, coordinate, value):
        self.coordinate = coordinate    # (x, y)
        self.value = value

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
    # outfile = open("temp.txt", "w")
    sudoku = Sudoku(puzzle)
    start = time()
    ans = sudoku.solve()
    end = time()
    # outfile.close()
    # print(ans)
    with open(sys.argv[2], 'a') as f:
        for i in range(9):
            for j in range(9):
                f.write(str(ans[i][j]) + " ")
            f.write("\n")
        f.write("time taken: " + str(end-start) + "\n")
        f.write("-------------------------------\n")
