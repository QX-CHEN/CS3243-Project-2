# CS3243 Introduction to Artificial Intelligence
# Project 2, Part 1: Sudoku

import sys
import copy
from collections import deque
from time import time

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = copy.deepcopy(puzzle) # self.ans is a list of lists
        self.csp = CSP(puzzle)

    def solve(self):
        self.AC3(self.csp)
        assignment = self.backtrackingSearch(self.csp)
        for var in assignment:
            (i, j) = var.coordinate
            self.ans[i][j] = assignment[var]
        # self.ans is a list of lists
        return self.ans



    def backtrackingSearch(self, csp):
        assignment = csp.inferAssignment()
        return self.backtrack(csp, assignment)
    
    def backtrack(self, csp, assignment = dict()):
        if self.complete(assignment,csp):
            return assignment
        
        var = self.mrv(csp, assignment)
        for value in self.lcv(var, assignment, csp):
            if self.isConsistent(var, value, assignment, csp):
                assignment[var] = value
                #print(var)
                csp.unassignedVars.remove(var)
                removals = self.assume(var, value, csp)

                # self.printAssignment(assignment)
                # inferences = self.inference(csp, var, value)
                if self.forwardChecking(var, value, assignment, removals,csp):
                    result = self.backtrack(csp, assignment)
                    if result:
                        return result
                csp.unassignedVars.add(var)
                self.addBack(removals,csp)
        if var in assignment:
            #print("@@@@@@@@@@@@@@@@@@@@@@")
            #print(var)
            
            del assignment[var]
        # del inferences from assignment
        return False

    def forwardChecking(self, var, val, assignment, removals, csp):
        csp.copyCurrDomain()
        for N in csp.neighbour[var]:
            if N not in assignment:
                for value in csp.currDomains[N].copy():
                    if csp.constraints[(var,N)](val,value):
                        csp.currDomains[N].remove(value)
                        removals.append((N,value))
                if not csp.currDomains[N]:
                    return False    
        return True

    def assume(self, var, value, csp):
        csp.copyCurrDomain()
        removals = list()
        for val in csp.currDomains[var]:
            if val != value:
                removals.append((var,val))
        csp.currDomains[var] = {value}
        return removals

    def addBack(self, removals, csp):
        for (var,val) in removals:
            csp.currDomains[var].add(val)

    def complete(self, assignment,csp):
        return len(assignment) == len(csp.variables)
    
    def isConsistent(self,var, val, assignment, csp):
        for key in assignment:
            try:
                if csp.constraints[(var,key)](val,assignment[var]):
                    return False
            except:
                continue
        return True
    
    def mrv(self,csp,assignment): # minimum remaining values
        seq = csp.unassignedVars.copy() #filter(lambda var: var not in assignment,csp.variables)
        return min(seq,key=lambda var: len(csp.currDomains[var]))
    
    ###check one more time ###
    def lcv(self, var, assignment,csp): # least constraining values
        def numConflicts(val): #number of conflicts
            conflict = 0
            for key in assignment:
                try:    
                    if csp.constraints[(var,key)](val,assignment[var]):
                        conflict +=1
                except:
                    continue
            return conflict
        ls = list(csp.currDomains[var])
        ls.sort(key = numConflicts)
        return ls
    # def numConflicts(self, csp, var, assignment,val): #number of conflicts
    #     conflict = 0
    #     for key in assignment:
    #         if csp.constraints[(var,key)](val,assignment[var]):
    #             conflict +=1
    #     return conflict





    def AC3(self,csp):
        arc_q = deque()
        for cons in csp.constraints:
            arc_q.append(cons)
        csp.copyCurrDomain()
        while arc_q:
            (xi, xj) = arc_q.popleft()
            if self.revise(csp, xi, xj):
                if not csp.currDomains[xi]:
                    return False
                for xk in csp.neighbour[xi]:
                    if xk != xj:
                        arc_q.append((xk, xi))
        return True
    def revise(self, csp, xi, xj):
        revised = False
        for x in csp.currDomains[xi].copy():
            conflict = True
            #if any(map(lambda y : csp.constraints[(xi, xj)](x, y),csp.currDomains[xj])):
                #xi.domain.remove(x)
            for y in csp.currDomains[xj]:
                if not csp.constraints[(xi,xj)](x,y):
                    conflict = False
                if not conflict:
                    break
            if conflict:
                csp.currDomains[xi].remove(x)
                revised = True
        return revised

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.
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

class CSP(object):
    def __init__(self, puzzle): #removed constraints

        self.variables = set()  # set of var
        self.domains = dict()   # key = var, value = var_domain (set)
        self.neighbour = dict() # key = var, value = var_neighbour (set)

        # set of binary constraints (constraint function involving two var) represented by pair(scope, relation)
        # scope = (x, y), relation = f(x, y), where x, y are vars
        self.constraints = dict()
        self.initialiseCSP(puzzle)
        self.unassignedVars = self.variables.copy()
        self.currDomains = None

    def initialiseCSP(self,puzzle): #initialise csp
        # going through 2d list
        for i in range(9):
            for j in range(9):
                self.variables.add(Variable((i, j), puzzle[i][j]))
        # going through var set
        for var1 in self.variables:
            self.domains[var1] = set([1, 2, 3, 4, 5, 6, 7, 8, 9]) if not var1.value else set([var1.value])
            self.neighbour[var1] = set()
            for var2 in self.variables:
                if var1 != var2 and var1.isSameUnit(var2):
                    self.constraints[(var1, var2)] = lambda x,y: x==y #to check if in conflict
                    self.neighbour[var1].add(var2)
        
    def copyCurrDomain(self):
        ''' Create a copy of domains as currDomains '''
        if self.currDomains is None:
            self.currDomains = dict()
            for var in self.variables:
                self.currDomains[var] = {i for i in self.domains[var]}
        return
    def inferAssignment(self):
        assignment = {}
        print("infer assignment")
        for var in self.currDomains:
            if len(self.currDomains[var])==1:
                assignment[var] = list(self.currDomains[var])[0]
                self.unassignedVars.remove(var)
        return assignment

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
