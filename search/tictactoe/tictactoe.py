"""
Tic Tac Toe Player
"""

import math

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
    if terminal(board):
        return EMPTY
    else:
        count_X=0
        count_O=0
        for row in board:
            for marker in row:
                if marker=="X":
                    count_X += 1
                elif marker == "O":
                    count_O += 1
        if count_O==count_X:
            return "X"
        elif count_O > count_X:
            return "X" 
        elif count_O < count_X: 
            return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_moves = set()
    if terminal(board):
        return possible_moves
    else:
        for i in range(3):
            for j in range(3):
                if board[i][j] == EMPTY:
                    possible_moves.add((i,j))
        return possible_moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    from copy import deepcopy
    new_board = deepcopy(board)
    i, j = action
    #if i not in range(3):
    #    raise Exception("row out of range")
    #elif j not in range(3):
    #    raise Exception("column out of range")
    if new_board[i][j] is not None:
        raise Exception("invalid move")
    else:
        new_board[i][j] = player(new_board)
    return new_board

def check_X(board):
    """
    checks if X has won the game.
    """
    #from pprint import pprint
    possible_combinations = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
    ]
    combo = [[board[i][j]==X for i,j in combination]for combination in possible_combinations]
    #print("X_combo")
    #pprint(combo)
    for row in combo:
        if all(row):
            return True
    return None

def check_O(board):
    """
    checks if O has won the game.
    """
    #from pprint import pprint
    possible_combinations = [
        [(0,0),(0,1),(0,2)], [(1,0),(1,1),(1,2)], [(2,0),(2,1),(2,2)],
        [(0,0),(1,0),(2,0)], [(0,1),(1,1),(2,1)], [(0,2),(1,2),(2,2)],
        [(0,0),(1,1),(2,2)], [(0,2),(1,1),(2,0)]
    ]
    combo = [[board[i][j]==O for i,j in combination]for combination in possible_combinations]
    #print("O_combo")
    #pprint(combo)
    for row in combo:
        if all(row):
            return True
    return None


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    if check_X(board):
       return X
    elif check_O(board):
        return O
    else:
        return None

def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True
    else:
        for row in board:
            if EMPTY in row:
                return False
        return True

def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board)==X:
        return 1
    elif winner(board)==O:
        return -1
    else:
        return 0

def minimax_value(board, player, alpha, beta):
    """
    Assigns value to the final resulting state.
    """
    if terminal(board):
        return utility(board)
    # MAX agent
    if player == X:
        value = -math.inf
        for action in actions(board):
            value = max(value, minimax_value(result(board, action), O, alpha, beta))
            #print("minimax_value", value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    #MIN agent
    else:
        value = math.inf
        for action in actions(board):
            value = min(value, minimax_value(result(board, action), X, alpha, beta))
            #print("minimax_value", value)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Uses alpha-beta prunning.
    if terminal(board):
        return None
    
    optimal_move = None
    alpha = -math.inf
    beta = math.inf

    if player(board) == X:
        value = -math.inf
        for action in actions(board):
            new_value = minimax_value(result(board, action), O, alpha, beta)
            #print("MAX",new_value)
            alpha = max(value, new_value)
            if new_value > value:
                #print("MAX")
                value = new_value
                optimal_move = action
    
    else:
        value = math.inf
        for action in actions(board):
            new_value = minimax_value(result(board, action), X, alpha, beta)
            #print("MIN",new_value)
            beta = min(value, new_value)
            if new_value < value:
                #print("MIN")
                value = new_value
                optimal_move = action
    print("AI optimal_move",optimal_move)
    return optimal_move

