import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for value in self.domains[variable].copy():
                if len(value) != variable.length:
                    self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        x_i, y_j = self.crossword.overlaps[x, y]
        for x_value in self.domains[x].copy():
            remove = True
            for y_value in self.domains[y]:
                #if len(x_value)==len(y_value) and x_value[x_i]!=y_value[y_j]:
                if x_value[x_i]==y_value[y_j]:
                    remove = False
            if remove:
                self.domains[x].remove(x_value)
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        if not arcs:
            #vars = list(self.domains.keys())
            arcs = [
                (v1,v2) for v1 in self.domains for v2 in self.crossword.neighbors(v1)
            ]
        while arcs:
            x, y = arcs.pop(0)
            if self.revise(x, y):
                if not self.domains[x]:
                    return False
                for z in self.crossword.neighbors(x)-self.domains[y]:
                    arcs.append((z,x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        #if len(self.domains)!=len(assignment):
        #    return False
        #elif all(assignment.values()):
        #    return True
        #return False
        #for var in assignment:
        #    if not assignment[var]:
        #        return False
        #return True
        return not bool(self.crossword.variables - set(assignment))

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all values are unique
        if len(assignment.values())!=len(set(assignment.values())):
            return False
        # check if no conflict
        #vars = list(assignment.keys())
        #var_pair = [
        #    (v1,v2) for v1 in vars for v2 in vars[vars.index(v1)]
        #    if self.crossword.overlaps[v1,v2]
        #]
        for var in assignment:
            # check if lengths are same
            if var.length != len(assignment[var]):
                return False
             # check if no conflict
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if assignment[var][i]!=assignment[neighbor][j]:
                        return False
        # check if lengths are same
        #for var,val in assignment.items():
        #    if var.length != len(val):
        #        return False
                
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        neighbors = self.crossword.neighbors(var)
        neighbors -= set(assignment)
        vals = dict()
        for value in self.domains[var]:
            vals[value] = 0
            for neighbor in neighbors:
                if value in self.domains[neighbor]:
                    vals[value] += 1
        
        return sorted(vals, key=vals.get) # sort by values of each key
        

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best_var = None
        for var in set(self.domains)-set(assignment):
            if (
                best_var is None or
                len(self.domains[var]) < len(self.domains[best_var]) or
                len(self.crossword.neighbors(var)) > len(self.crossword.neighbors(best_var))
            ):
                best_var = var
        return best_var

    #def inference(self, var, assignment):
    #    """
    ###   Algorithm for enforcing arc-consistency everytime
    ##    a new assignment is made.
    ##    """
    #    inferences = dict()
    #    arcs = [(v1,var) for v1 in self.crossword.neighbors(var)]
    #    if self.ac3(arcs):
    #        for variable in self.domains:
    #           if variable not in assignment and variable!=var:
    #               if len(self.domains[var])==1:
    #                   inferences[var]=self.domains[var]
    #        return inferences


    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment
        var = self.select_unassigned_variable(assignment)
        for value in self.domains[var]:
            new_assignment = assignment.copy()
            new_assignment[var]=value
            #assignment[var]=value
            if self.consistent(new_assignment):
                assignment[var]=value
                #inferences = self.inference(var, assignment)
                #if inferences:
                    #assignment.update(inferences)
                result = self.backtrack(assignment)
                if result is not None:
                    return result
            #assignment.pop(var)
            #else:
            #    assignment.pop(var)
            #    for variable in inferences:
            #        assignment.pop(variable)
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
