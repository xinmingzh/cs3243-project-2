import sys
import time
from copy import deepcopy

# Running script: given code can be run with the command:
# python file.py, ./path/to/init_state.txt ./output/output.txt

class Sudoku(object):
    def __init__(self, puzzle):
        # you may add more attributes if you need
        self.puzzle = puzzle # self.puzzle is a list of lists
        self.ans = deepcopy(puzzle) # self.ans is a list of lists
        self.domains = self.init_domain()
        self.neighbours = self.init_neighbours()
        self.pruned = self.init_pruned()
        self.constaints = self.init_constraints()
        self.nodes = 0
        self.time = time.time()


    def solve(self):
        # Main method called to run the alogorithm.

        self.precheck()
        print("time taken: " + str(time.time() - self.time))
        if not self.ac3(self.puzzle):
            return self.puzzle
        
        print("time taken: " + str(time.time() - self.time))

        self.ans = self.backtrack(self.puzzle, True)

        print("nodes: " + str(self.nodes))
        print("time taken: " + str(time.time() - self.time))

        # self.ans is a list of lists
        return self.ans


    def backtrack(self, puzzle, flag):

        self.nodes += 1
        # self.print_puzzle()
        # self.print_domains()
        # if (self.nodes) > 3:
        #     return puzzle

        if (self.isComplete(puzzle)):
            return puzzle

        pos = self.select_unassigned_var(puzzle)

        if not self.domains[pos]:
            return False

        for val in self.ordered_domain_values(puzzle, pos):

            if self.is_having_conflits(puzzle, pos, val):
                continue
            
            if self.assign(puzzle, pos, val, flag):

                result = self.backtrack(puzzle, flag)

                if result:
                    return result
            
            self.unassign(puzzle, pos, val)

        return False
    

    def precheck(self):
        # remove assigned value from neighbour cells of all assigned cells
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    for nb in self.neighbours[(i, j)]:
                        if puzzle[i][j] in self.domains[nb]:
                            self.domains[nb].remove(puzzle[i][j])


    def isComplete(self, puzzle):
        # return true if sudoku puzzle is complete
        return not any(0 in row for row in puzzle)


    def select_unassigned_var(self, puzzle):
        # select unassigned variable with Minimum Remaining Values (MRV) heuristic
        min_len = 10
        pos = False
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    if len(self.domains[(i, j)]) == 1:
                        return (i, j)

                    if len(self.domains[(i, j)]) < min_len:
                        pos = (i, j)
                        min_len = len(self.domains[(i, j)])
        # print(str(pos) + ": " + str(self.domains[pos]))
        return pos


    def ordered_domain_values(self, puzzle, pos):
        # return the domain of a cell sorted by Least Constraining Value (LCV) heuristic
        if len(self.domains[pos]) == 1:
            return self.domains[pos]

        return sorted(self.domains[pos], key = lambda val: self.conflicts(puzzle, pos, val))


    def conflicts(self, puzzle, pos, val):
        # a conflict occurs if the value of a cell appears in the domain of neighbouring cells
        # return the total number of conflicts of a value of a cell
        count = 0
        for neighbour in self.neighbours[pos]:
            if val in self.domains[neighbour]:
                count += 1
        return count
        

    def is_having_conflits(self, puzzle, pos, val):
        return val in map(lambda x: puzzle[x[0]][x[1]], self.neighbours[pos])


    def assign(self, puzzle, pos, val, flag = False):
        # print("assigning: " + str(pos) + ": " + str(val))
        puzzle[pos[0]][pos[1]] = val

        for v in self.domains[pos]:
            if v != val:
                self.domains[pos].remove(v)
                self.pruned[pos].append((pos, v))

        return self.forward_check(puzzle, pos, val, flag)


    def forward_check(self, puzzle, pos, val, flag = False):
        # forward checks for domain reductions
        if flag:
            # perform ac3 algo
            count = 20      # limits the number of iterations of ac3 checks to reduce time spent
        
            queue = [(xk, pos) for xk in self.neighbours[pos]]
            while count and queue:
                xi, xj = queue.pop(0)
                if self.revise(puzzle, xi, xj, pos):
                    if not self.domains[xi]:
                        return False
                    for xk in self.neighbours[xi]:
                        queue.append((xk, xi))
                count -= 1
        else:
            # perform forward checking algo
            for neighbour in self.neighbours[pos]:
                if puzzle[neighbour[0]][neighbour[1]] == 0:
                    if val in self.domains[neighbour]:
                        self.domains[neighbour].remove(val)
                        self.pruned[pos].append((neighbour, val))
        return True


    def unassign(self, puzzle, pos, val):
        # unassign value from cell and return pruned values back to domains
        # print("unassigning")
        if puzzle[pos[0]][pos[1]] != 0:
            for neighbour, val in self.pruned[pos]:
                self.domains[neighbour].append(val)

            self.pruned[pos] = []

            puzzle[pos[0]][pos[1]] = 0


    def get_peers(self, puzzle, pos):
        # helper function
        # get a list of peers (neighbours in the same 3*3 square)
        result = []
        for i in range(pos[0] - pos[0]%3, pos[0] - pos[0]%3 + 3):
            for j in range(pos[1] - pos[1]%3, pos[1] - pos[1]%3 + 3):
                result += [(i, j),]
        return result


    def ac3(self, puzzle):
        # ac3 algo used before backtracking
        queue = [x for x in self.constaints]
        count = 100     # limits the number of iterations of ac3 checks to reduce time spent
        while count and queue:
            xi, xj = queue.pop(0)
            if self.revise(puzzle, xi, xj):
                if not self.domains[xi]:
                    return False
                for xk in self.neighbours[xi]:
                    queue.append([xk, xi])
            count -= 1
        return True
    

    def revise(self, puzzle, xi, xj, pos = None):
        # revise the pair of cells xi and xj
        # for value in domain of xi, if value not consistent with domain of xj, remove value
        revised = False

        for x in self.domains[xi]:
            if puzzle[xj[0]][xj[1]] == 0:
                if not any([self.satisfy_binary_constraint(x, y) for y in self.domains[xj]]):
                    self.domains[xi].remove(x)
                    if pos:
                        self.pruned[pos].append((xi, x))
                    revised = True
            elif x == puzzle[xj[0]][xj[1]]:
                self.domains[xi].remove(x)
                if pos:
                    self.pruned[pos].append((xi, x))
                revised = True
        return revised


    def satisfy_binary_constraint(self, val1, val2):
        return val1 != val2


    def init_domain(self):
        result = {}
        for i in range(9):
            for j in range(9):
                if self.puzzle[i][j] != 0:
                    result[(i, j)] = [self.puzzle[i][j],]
                else:
                    result[(i, j)] = [x for x in range(1, 10)]
        return result
    

    def init_neighbours(self):
        # set up dict of cell -> [neighbours]
        result = {}
        for i in range(9):
            for j in range(9):
                result[(i, j)] = set()
                result[(i, j)].update([(i, x) for x in range(9)])
                result[(i, j)].update([(x, j) for x in range(9)])
                result[(i, j)].update(self.get_peers(self.puzzle, (i, j)))
                result[(i, j)].remove((i, j))
        return result


    def init_pruned(self):
        # set up dict of cell -> [(neighbour, pruned value)]
        result = {}
        for i in range(9):
            for j in range(9):
                result[(i, j)] = []
        return result


    def init_constraints(self):
        # set up list of [(cell, neighbour)]
        result = []
        for i in range(9):
            for j in range(9):
                for neighbour in self.neighbours[(i, j)]:
                    result.append(((i, j), neighbour))
        return result


    def print_puzzle(self):
        for i in range(9):
            for j in range(9):
                print(str(puzzle[i][j]) + " "),
            print("")

    def print_domains(self):
        print("Total: " + str(self.count_domain_vals()))
        x = 1
        for key, val in sorted(self.domains.items()):
            if x % 3 != 0:
                print(str(key) + ": " + str(val) + " "*(30 - len(str(key) + ": " + str(val)))),
            else:
                print(str(key) + ": " + str(val))
            x += 1
        print("")

    
    def count_domain_vals(self):
        return sum([len(val) for key, val in self.domains.items()])

    # you may add more classes/functions if you think is useful
    # However, ensure all the classes/functions are in this file ONLY
    # Note that our evaluation scripts only call the solve method.
    # Any other methods that you write should be used within the solve() method.

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
