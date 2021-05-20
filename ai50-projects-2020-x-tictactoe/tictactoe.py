"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    emptycounter = 0
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                emptycounter = emptycounter + 1
    # we know how many board cells are EMPTY. if there are 9 EMPTY cells, its X turn, if there are 8 EMPTY cells, its O turn, etc.
    if emptycounter % 2 == 0:
        return O
    else:
        return X

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] == EMPTY:
                actions.add((row, col))
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    currplayer = player(board)
    dupboard = copy.deepcopy(board)

    # change the field that is being played
    row,col = action
    # action can only be performed if row,col is EMPTY
    if dupboard[row][col] == EMPTY:
        # if cell is empty, put value in it matching current player turn (X or O)
        dupboard[row][col] = currplayer
        return dupboard
    else:
        raise Exception("ERROR, Cell not empty")

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # check Rows
    for row in board:
        if row.count(X) == 3:
            return X
        elif row.count(O) == 3:
            return O

    # check cols
    for col in range(3):
        col = (board[0][col],board[1][col],board[2][col])
        if col.count(X) == 3:
            return X
        elif col.count(O) == 3:
            return O

    # check diagonals
    diag1 = (board[0][0], board[1][1], board[2][2])
    diag2 = (board[0][2], board[1][1], board[2][0])
    if (diag1.count(X) == 3) or (diag2.count(X) == 3):
        return X
    elif (diag1.count(O) == 3) or (diag2.count(O) == 3):
        return O
    # if we reached here, no win was found, so return None
    return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # if there's already a winner, then game is over = return True
    if winner(board):
        return True
    else:
        # if no winner, check each row, and if EMTPY value is anywhere in a row, then game isn't over yet = return False
        for row in board:
            if EMPTY in row:
                return False
        # if we got here, there's no EMPTY cell in the board, and there's no winner, so game is over = return True
        return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # If X has won the game, the utility is 1. If O has won the game, the utility is -1. If the game is a tie, the utility is 0.
    thewinner = winner(board)
    if thewinner == X:
        return 1
    elif thewinner == O:
        return -1
    else:
        return 0

def calcMaxValue(board):
    if terminal(board):
        return utility(board)

    res = -math.inf
    for action in actions(board):
        res = max(res, calcMinValue(result(board, action)))

    return res


def calcMinValue(board):
    if terminal(board):
        return utility(board)

    res = math.inf
    for action in actions(board):
        res = min(res, calcMaxValue(result(board, action)))

    return res

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    else:
        # Who's turn is it?
        currplayer = player(board)
        bestaction = None # this shouldn't happen...

        # if it's player X, we need to calc the MIN value (for player O)
        if currplayer == X:
            #start with lowest value
            res = -math.inf
            for action in actions(board):
                # for each action, get the min result value (because its X player)
                bestres = calcMinValue(result(board, action))
                if bestres > res: # if higher found, use it as the new highest
                    res = bestres
                    bestaction = action
        else: # if it's player O, we need to calc the MAX value (for player X)
            # start with highest value
            res = math.inf
            for action in actions(board):
                #for each action, get the max result value (because its O player)
                bestres = calcMaxValue(result(board, action))
                if bestres < res: # if lower found, use it as the new lowest
                    res = bestres
                    bestaction = action

        return bestaction

