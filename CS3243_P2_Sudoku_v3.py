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
        self.variables = tuple()
        self.domains = dict()
        self.neighbors = dict()
        self.constraints = lambda A, a, B, b : a != b
        self.initialiseCSP(puzzle)
        self.csp = CSP(self.variables, self.domains, self.neighbors, self.constraints)

    def initialiseCSP(self, puzzle):
        # going through 2d list
        for i in range(9):
            for j in range(9):
                self.variables += (Variable((i, j), puzzle[i][j]),)
        
        # going through var set
        for var1 in self.variables:
            self.domains[var1] = [1, 2, 3, 4, 5, 6, 7, 8, 9] if not var1.value else [var1.value]
            self.neighbors[var1] = []
            for var2 in self.variables:
                if var1 != var2 and var1.isSameUnit(var2):
                    self.neighbors[var1].append(var2)

    def solve(self):

        # self.ans is a list of lists
        self.AC3(self.csp)
        assignment = self.backtracking_search(self.csp)
        for var in assignment:
            (i, j) = var.coordinate
            self.ans[i][j] = assignment[var]
        return self.ans

    # def dom_j_up(self, csp, queue):
    #     return SortedSet(queue, key=lambda t: -(len(csp.curr_domains[t[1]])))

    def AC3(self, csp, queue=None, removals=None):
        """[Figure 6.3]"""
        if queue is None:
            queue = {(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]}
        csp.support_pruning()
        # queue = self.dom_j_up(csp, queue)
        checks = 0
        while queue:
            (Xi, Xj) = queue.pop()
            revised, checks = self.revise(csp, Xi, Xj, removals, checks)
            if revised:
                if not csp.curr_domains[Xi]:
                    return False, checks  # CSP is inconsistent
                for Xk in csp.neighbors[Xi]:
                    if Xk != Xj:
                        queue.add((Xk, Xi))
        return True, checks  # CSP is satisfiable

    def revise(self, csp, Xi, Xj, removals, checks=0):
        """Return true if we remove a value."""
        revised = False
        for x in csp.curr_domains[Xi][:]:
            # If Xi=x conflicts with Xj=y for every possible y, eliminate Xi=x
            # if all(not csp.constraints(Xi, x, Xj, y) for y in csp.curr_domains[Xj]):
            conflict = True
            for y in csp.curr_domains[Xj]:
                if csp.constraints(Xi, x, Xj, y):
                    conflict = False
                checks += 1
                if not conflict:
                    break
            if conflict:
                csp.prune(Xi, x, removals)
                revised = True
        return revised, checks

    # def AC3b(self, csp, queue=None, removals=None):
    #     if queue is None:
    #         queue = {(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]}
    #     csp.support_pruning()
    #     queue = self.dom_j_up(csp, queue)
    #     checks = 0
    #     while queue:
    #         (Xi, Xj) = queue.pop()
    #         # Si_p values are all known to be supported by Xj
    #         # Sj_p values are all known to be supported by Xi
    #         # Dj - Sj_p = Sj_u values are unknown, as yet, to be supported by Xi
    #         Si_p, Sj_p, Sj_u, checks = self.partition(csp, Xi, Xj, checks)
    #         if not Si_p:
    #             return False, checks  # CSP is inconsistent
    #         revised = False
    #         for x in set(csp.curr_domains[Xi]) - Si_p:
    #             csp.prune(Xi, x, removals)
    #             revised = True
    #         if revised:
    #             for Xk in csp.neighbors[Xi]:
    #                 if Xk != Xj:
    #                     queue.add((Xk, Xi))
    #         if (Xj, Xi) in queue:
    #             if isinstance(queue, set):
    #                 # or queue -= {(Xj, Xi)} or queue.remove((Xj, Xi))
    #                 queue.difference_update({(Xj, Xi)})
    #             else:
    #                 queue.difference_update((Xj, Xi))
    #             # the elements in D_j which are supported by Xi are given by the union of Sj_p with the set of those
    #             # elements of Sj_u which further processing will show to be supported by some vi_p in Si_p
    #             for vj_p in Sj_u:
    #                 for vi_p in Si_p:
    #                     conflict = True
    #                     if csp.constraints(Xj, vj_p, Xi, vi_p):
    #                         conflict = False
    #                         Sj_p.add(vj_p)
    #                     checks += 1
    #                     if not conflict:
    #                         break
    #             revised = False
    #             for x in set(csp.curr_domains[Xj]) - Sj_p:
    #                 csp.prune(Xj, x, removals)
    #                 revised = True
    #             if revised:
    #                 for Xk in csp.neighbors[Xj]:
    #                     if Xk != Xi:
    #                         queue.add((Xk, Xj))
    #     return True, checks  # CSP is satisfiable


    # def partition(self, csp, Xi, Xj, checks=0):
    #     Si_p = set()
    #     Sj_p = set()
    #     Sj_u = set(csp.curr_domains[Xj])
    #     for vi_u in csp.curr_domains[Xi]:
    #         conflict = True
    #         # now, in order to establish support for a value vi_u in Di it seems better to try to find a support among
    #         # the values in Sj_u first, because for each vj_u in Sj_u the check (vi_u, vj_u) is a double-support check
    #         # and it is just as likely that any vj_u in Sj_u supports vi_u than it is that any vj_p in Sj_p does...
    #         for vj_u in Sj_u - Sj_p:
    #             # double-support check
    #             if csp.constraints(Xi, vi_u, Xj, vj_u):
    #                 conflict = False
    #                 Si_p.add(vi_u)
    #                 Sj_p.add(vj_u)
    #             checks += 1
    #             if not conflict:
    #                 break
    #         # ... and only if no support can be found among the elements in Sj_u, should the elements vj_p in Sj_p be used
    #         # for single-support checks (vi_u, vj_p)
    #         if conflict:
    #             for vj_p in Sj_p:
    #                 # single-support check
    #                 if csp.constraints(Xi, vi_u, Xj, vj_p):
    #                     conflict = False
    #                     Si_p.add(vi_u)
    #                 checks += 1
    #                 if not conflict:
    #                     break
    #     return Si_p, Sj_p, Sj_u - Sj_p, checks


    # Constraint Propagation with AC4

    # def AC4(self, csp, queue=None, removals=None):
    #     if queue is None:
    #         queue = {(Xi, Xk) for Xi in csp.variables for Xk in csp.neighbors[Xi]}
    #     csp.support_pruning()
    #     queue = self.dom_j_up(csp, queue)
    #     support_counter = Counter()
    #     variable_value_pairs_supported = defaultdict(set)
    #     unsupported_variable_value_pairs = []
    #     checks = 0
    #     # construction and initialization of support sets
    #     while queue:
    #         (Xi, Xj) = queue.pop()
    #         revised = False
    #         for x in csp.curr_domains[Xi][:]:
    #             for y in csp.curr_domains[Xj]:
    #                 if csp.constraints(Xi, x, Xj, y):
    #                     support_counter[(Xi, x, Xj)] += 1
    #                     variable_value_pairs_supported[(Xj, y)].add((Xi, x))
    #                 checks += 1
    #             if support_counter[(Xi, x, Xj)] == 0:
    #                 csp.prune(Xi, x, removals)
    #                 revised = True
    #                 unsupported_variable_value_pairs.append((Xi, x))
    #         if revised:
    #             if not csp.curr_domains[Xi]:
    #                 return False, checks  # CSP is inconsistent
    #     # propagation of removed values
    #     while unsupported_variable_value_pairs:
    #         Xj, y = unsupported_variable_value_pairs.pop()
    #         for Xi, x in variable_value_pairs_supported[(Xj, y)]:
    #             revised = False
    #             if x in csp.curr_domains[Xi][:]:
    #                 support_counter[(Xi, x, Xj)] -= 1
    #                 if support_counter[(Xi, x, Xj)] == 0:
    #                     csp.prune(Xi, x, removals)
    #                     revised = True
    #                     unsupported_variable_value_pairs.append((Xi, x))
    #             if revised:
    #                 if not csp.curr_domains[Xi]:
    #                     return False, checks  # CSP is inconsistent
    #     return True, checks  # CSP is satisfiable

    # CSP Backtracking Search

    # Variable ordering

    def first(self, iterable, default=None):
        """Return the first element of an iterable; or default."""
        return next(iter(iterable), default)
    
    def shuffled(self, iterable):
        """Randomly shuffle a copy of iterable."""
        items = list(iterable)
        shuffle(items)
        return items

    def argmin_random_tie(self, seq, key=lambda x : x):
        """Return a minimum element of seq; break ties at random."""
        return min(seq, key=key)

    # def degree(self, csp, var, seq):
    #     return count(filter(lambda n : n in csp.neighbors[var], seq))

    def first_unassigned_variable(self, assignment, csp):
        """The default variable order."""
        return self.first([var for var in csp.variables if var not in assignment])

    # def mrv_with_degree(self, assignment, csp):
    #     seq = [var for var in csp.variables if var not in assignment]
    #     curr_var = (None, 0, 0)
    #     for v in seq:
    #         lv = self.num_legal_values(csp, v, seq)
    #         degree = self.degree(csp, v, seq)
    #         if not curr_var[0]:
    #             curr_var = (v, lv, degree)
    #         else:
    #             if lv < curr_var[1]:
    #                 curr_var = (v, lv, degree)
    #                 continue
    #             elif lv == curr_var[1]:
    #                 if degree > curr_var[2]:
    #                     curr_var = (v, lv, degree)
    #     return curr_var[0]

    def mrv(self, assignment, csp):
        """Minimum-remaining-values heuristic."""
        return self.argmin_random_tie([v for v in csp.variables if v not in assignment],
                                key=lambda var: self.num_legal_values(csp, var, assignment))

    def num_legal_values(self, csp, var, assignment):
        if csp.curr_domains:
            return len(csp.curr_domains[var])
        else:
            return count(csp.nconflicts(var, val, assignment) == 0 for val in csp.domains[var])

    # Value ordering

    def unordered_domain_values(self, var, assignment, csp):
        """The default value order."""
        return csp.choices(var)

    def lcv(self, var, assignment, csp):
        """Least-constraining-values heuristic."""
        return sorted(csp.choices(var), key=lambda val: csp.nconflicts(var, val, assignment))

    # Inference

    def no_inference(self, csp, var, value, assignment, removals):
        return True

    def forward_checking(self, csp, var, value, assignment, removals):
        """Prune neighbor values inconsistent with var=value."""
        csp.support_pruning()
        for B in csp.neighbors[var]:
            if B not in assignment:
                for b in csp.curr_domains[B][:]:
                    if not csp.constraints(var, value, B, b):
                        csp.prune(B, b, removals)
                if not csp.curr_domains[B]:
                    return False
        return True

    def mac(self, csp, var, value, assignment, removals):
        """Maintain arc consistency."""
        return self.AC3(csp, {(X, var) for X in csp.neighbors[var]}, removals)

    # The search, proper

    def backtracking_search(self, csp):
        """[Figure 6.5]"""

        def backtrack(assignment):
            # self.printAssignment(assignment)
            # print(len(assignment), len(csp.variables))
            if len(assignment) == len(csp.variables):
                return assignment
            var = self.mrv(assignment, csp)
            for value in self.lcv(var, assignment, csp):
                if 0 == csp.nconflicts(var, value, assignment):
                    csp.assign(var, value, assignment)
                    removals = csp.suppose(var, value)
                    if self.forward_checking(csp, var, value, assignment, removals):
                        result = backtrack(assignment)
                        if result is not None:
                            return result
                    csp.restore(removals)
            csp.unassign(var, assignment)
            return None

        result = backtrack({})
        # assert result is None or csp.goal_test(result)
        return result

    def printAssignment(self, assignment):
        lst = [[0 for i in range(9)] for j in range(9)]
        for var in assignment:
            lst[var.coordinate[0]][var.coordinate[1]] = assignment[var]
        for line in lst:
            print(line)

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(map(bool, seq))

class CSP():
    """This class describes finite-domain Constraint Satisfaction Problems.
    A CSP is specified by the following inputs:
        variables   A list of variables; each is atomic (e.g. int or string).
        domains     A dict of {var:[possible_value, ...]} entries.
        neighbors   A dict of {var:[var,...]} that for each variable lists
                    the other variables that participate in constraints.
        constraints A function f(A, a, B, b) that returns true if neighbors
                    A, B satisfy the constraint when they have values A=a, B=b

    In the textbook and in most mathematical definitions, the
    constraints are specified as explicit pairs of allowable values,
    but the formulation here is easier to express and more compact for
    most cases (for example, the n-Queens problem can be represented
    in O(n) space using this notation, instead of O(n^4) for the
    explicit representation). In terms of describing the CSP as a
    problem, that's all there is.

    However, the class also supports data structures and methods that help you
    solve CSPs by calling a search function on the CSP. Methods and slots are
    as follows, where the argument 'a' represents an assignment, which is a
    dict of {var:val} entries:
        assign(var, val, a)     Assign a[var] = val; do other bookkeeping
        unassign(var, a)        Do del a[var], plus other bookkeeping
        nconflicts(var, val, a) Return the number of other variables that
                                conflict with var=val
        curr_domains[var]       Slot: remaining consistent values for var
                                Used by constraint propagation routines.
    The following methods are used only by graph_search and tree_search:
        actions(state)          Return a list of actions
        result(state, action)   Return a successor of state
        goal_test(state)        Return true if all constraints satisfied
    The following are just for debugging purposes:
        nassigns                Slot: tracks the number of assignments made
        display(a)              Print a human-readable representation
    """

    def __init__(self, variables, domains, neighbors, constraints):
        """Construct a CSP problem. If variables is empty, it becomes domains.keys()."""
        variables = variables or list(domains.keys())
        self.variables = variables
        self.domains = domains
        self.neighbors = neighbors
        self.constraints = constraints
        self.curr_domains = None
        self.nassigns = 0

    def assign(self, var, val, assignment):
        """Add {var: val} to assignment; Discard the old value if any."""
        assignment[var] = val
        self.nassigns += 1

    def unassign(self, var, assignment):
        """Remove {var: val} from assignment.
        DO NOT call this if you are changing a variable to a new value;
        just call assign for that."""
        if var in assignment:
            del assignment[var]

    def nconflicts(self, var, val, assignment):
        """Return the number of conflicts var=val has with other variables."""

        # Subclasses may implement this more efficiently
        def conflict(var2):
            return var2 in assignment and not self.constraints(var, val, var2, assignment[var2])

        return count(conflict(v) for v in self.neighbors[var])

    def display(self, assignment):
        """Show a human-readable representation of the CSP."""
        # Subclasses can print in a prettier way, or display with a GUI
        print(assignment)

    # These are for constraint propagation

    def support_pruning(self):
        """Make sure we can prune values from domains. (We want to pay
        for this only if we use it.)"""
        if self.curr_domains is None:
            self.curr_domains = {v: list(self.domains[v]) for v in self.variables}

    def suppose(self, var, value):
        """Start accumulating inferences from assuming var=value."""
        self.support_pruning()
        removals = [(var, a) for a in self.curr_domains[var] if a != value]
        self.curr_domains[var] = [value]
        return removals

    def prune(self, var, value, removals):
        """Rule out var=value."""
        self.curr_domains[var].remove(value)
        if removals is not None:
            removals.append((var, value))

    def choices(self, var):
        """Return all values for var that aren't currently ruled out."""
        return (self.curr_domains or self.domains)[var]

    def infer_assignment(self):
        """Return the partial assignment implied by the current inferences."""
        self.support_pruning()
        return {v: self.curr_domains[v][0]
                for v in self.variables if 1 == len(self.curr_domains[v])}

    def restore(self, removals):
        """Undo a supposition and all inferences from it."""
        for B, b in removals:
            self.curr_domains[B].append(b)

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
