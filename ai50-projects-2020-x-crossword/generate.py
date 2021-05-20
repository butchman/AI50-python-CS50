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

        # if the word length is different then the variable length,
        # it can't be used at this specific variable, so remove it...
        for variable in self.crossword.variables:
            for word in self.crossword.words:
                if variable.length != len(word):
                    self.domains[variable].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        removeList = []
        overlap = self.crossword.overlaps[x, y]

        # check if there's overlap between variable X and variable Y
        if overlap is None:
            return False
        else:
            index1, index2 = overlap

        # index1 and index2 are the positions inside the variables of the overlapping square
        for word1 in self.domains[x]:
            overlap_possible = False
            # compare the word from the first domain to all potential words in the second domain
            for word2 in self.domains[y]:
                # check if both words match on their overlapping square (and make sure they're different...)
                if (word1 != word2) and (word1[index1] == word2[index2]):
                    overlap_possible = True
                    break
            # if word1 doesn't have a matching word that overlaps on the square, add it to the list
            # of words to be removed (those words cannot be used)
            if not overlap_possible:
                removeList.append(word1)

        # remove the words from X domain
        for word in removeList:
            self.domains[x].remove(word)

        # if we found at least one word to remove, return True
        return len(removeList) > 0

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        if arcs is None:
            # create the list of arcs - for each arc, get its neighbors and add the pair
            arcs = []
            for variable in self.crossword.variables:
                for neighbor in self.crossword.neighbors(variable):
                    arcs.append((variable, neighbor))

        # process the arcs in the list
        for x, y in arcs:
            if self.revise(x, y):
                # if we removed words from domain X, add all arcs from X to its neighbors so they would be re-processed
                for neighbor in self.crossword.neighbors(x):
                    arcs.append((x, neighbor))

        # is the domain list empty?
        return len(self.domains[x]) > 0

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        # iterate through all the crossword variables and make sure they exist in the assignment
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        # go through the list of variables in the current assignment
        for var1 in assignment:
            word1 = assignment[var1]
            # check word length to make sure it matches the constraint length
            if len(word1) != var1.length:
                return False

            # check if the other words setup matches word1 setup
            for var2 in assignment:
                word2 = assignment[var2]
                # dont compare var to itself...
                if var1 == var2:
                    continue

                # check if different assignment variables use the same word
                if word1 == word2:
                    return False

                # now check the overlaps
                overlap = self.crossword.overlaps[var1, var2]
                # if no overlap for this pair of variables, move to the next variable in the assignment
                if overlap is None:
                    continue

                # get the overlap indexes
                index1, index2 = overlap
                # check if letter in index1 of word1 doesnt match letter in index2 of word2
                if word1[index1] != word2[index2]:
                    # words don't satisfy overlap constraints
                    return False

        # if we got here, all is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        """
        def countRuledOut(var2check, neighbors):
            co = 0
            for neighbor in neighbors:
                index1,index2 = self.crossword.overlaps[var,neighbor]
                for item in self.domains[neighbor]:
                    if var2check[index1] != item[index2]:
                        co += 1
            return co

        # create a list of variables to sort (excluding the already assigned variables)
        neighborList = []
        for var2Check in self.crossword.neighbors(var):
            if var2Check not in assignment:
                neighborList.append(var2Check)
        """

        return self.domains[var]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # return the first occurrence of variable not in the assignment
        for variable in self.crossword.variables:
            if variable not in assignment.keys():
                return variable

        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # did we assign all variables with fitting words?
        if self.assignment_complete(assignment):
            return assignment

        # get a variable to fill a word into
        variable = self.select_unassigned_variable(assignment)

        # run through the list of potential words
        for value in self.order_domain_values(variable, assignment):
            # try using the word chosen
            assignment[variable] = value

            # do all words fit in the crossword puzzle without conflicting characters
            if self.consistent(assignment):
                # check if the new partial assignment works
                result = self.backtrack(assignment)

                # if it doesnt work, remove the assignment to this variable,
                # and move to the next potential word (if exists..)
                if result is None:
                    assignment[variable] = None
                else:
                    return result

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
