import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) <= self.count:
            return set(self.cells)
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0: # if no mines near it, its safe
            return set(self.cells)
        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # make sure that cell is in the KB
        if cell not in self.cells:
            return
        self.cells.remove(cell)
        self.count = max(0,self.count - 1)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        if cell not in self.cells:
            return
        self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def genAdjCellList(self, cell):
        # split the cell to Row and Col
        cellRow ,cellCol = cell

        # calc the position of the bounding RECT around our cell - from (Row-1,col-1) to (Row+1,col+1)
        row1 = cellRow - 1
        # fix lower Row bound to 0, if smaller than 0
        if row1 < 0:
            row1 = 0

        row2 = cellRow + 2 # additional +1 for the FOR RANGE
        # fix upper Row bound to board height, if bigger than board height
        if row2 > self.height:
            row2 = self.height

        col1 = cellCol - 1
        # fix lower Col bound to 0, if smaller than 0
        if col1 < 0:
            col1 = 0

        col2 = cellCol + 2 # additional +1 for the FOR RANGE
        # fix upper Col bound to board width, if bigger than board width
        if col2 > self.width:
            col2 = self.width

        adjCells = set()
        for i in range (row1,row2):
            for j in range (col1,col2):
                if (i,j) != cell:
                    if (i,j) not in self.moves_made:
                        adjCells.add((i,j))
        return adjCells

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        # mark the cell as a "made move"
        self.moves_made.add(cell)

        # mark the cell as safe
        self.mark_safe(cell)

        # add the new sentence to the KB, with all adjecent cells with thier COUNT value
        self.knowledge.append(Sentence(self.genAdjCellList(cell),count))

        # mark cells as safe, where possible
        for sentence in self.knowledge:
            safes = sentence.known_safes()
            for safe in safes:
                self.mark_safe(safe)

        # mark cells as mines, where possible
        for sentence in self.knowledge:
            mines = sentence.known_mines()
            for mine in mines:
                self.mark_mine(mine)

        # update KB with new data - compare each KB sentence to any other sentence (except for itself)
        for i,s1 in enumerate(self.knowledge):
            for j,s2 in enumerate(self.knowledge):
                if i == j: # no need to compare a sentence to itself
                    continue

                # check if sentence1 is a subset of sentence 2, and if so, remove the subset cells and decrease the count accordingly
                if s1.cells.issubset(s2.cells):
                    s2.cells = s2.cells - s1.cells
                    s2.count = max(0, s2.count - s1.count)

                # and also check if sentence 2 is a subset of sentence 1, and if so, remove the subset cells and decrease the count accordingly
                elif s2.cells.issubset(s1.cells):
                    s1.cells = s1.cells - s2.cells
                    s1.count = max(0, s1.count - s2.count)

        # sentences with empty cells should be removed
        for sentence in self.knowledge:
            if len(sentence.cells) == 0:
                self.knowledge.remove(sentence)

        # create the safe moves list -> moves in safes - movesmade
        safelist = list()
        for safeMove in self.safes:
            if safeMove not in self.moves_made:
                safelist.append(safeMove)

        # print the data
        print("--------------------------------------------------------------------------------")
        print("Safe cells (row,col):", safelist)
        print("Cells with mines (row,col):", self.mines)
        print("Knowledge:")
        for sentence in self.knowledge:
            if sentence.count > 0: # no need for sentences with count of 0 (they are safe moves)
                print(str(sentence))
        print("--------------------------------------------------------------------------------")

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for safeMove in self.safes:
            if safeMove not in self.moves_made:
                print("Performing safe move from the list (row,col):", safeMove)
                return safeMove

        # if we got here, there is no safe move to make :-(
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        cellList = list()
        for row in range(self.height):
            for col in range(self.width):
                if ((row,col) not in self.moves_made) and ((row, col) not in self.mines):
                    cellList.append((row,col))

        if not cellList:
            return None

        randCell = random.choice(cellList)
        print("AI random move (row,col):",randCell)
        return randCell
