# CS3243 Project 2

## Sudoku Puzzle Solver

Basic implementation of sudoku puzzle solver is completed using bactracking search with forward checking and ac3 algo to improve efficiency.

An extra constraint is checked for in forward checking. The constraint states that in any group of cells, if a value is unique in all the cells' domains, the cell containing the value must be of that value. If that cell also contains other values, other values can be removed from the domain.

Meets benchmark set in the assignment.
