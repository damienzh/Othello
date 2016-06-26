import sys, time, copy

# 1-dimension board
#  0  1  2  3  4  5  6  7  8  9
# 10 11 12 13 14 15 16 17 18 19
# 20 21 22 23 24 25 26 27 28 29
# 30 31 32 33 34 35 36 37 38 39
# 40 41 42 43 44 45 46 47 48 49
# 50 51 52 53 54 55 56 57 58 59
# 60 61 62 63 64 65 66 67 68 69
# 70 71 72 73 74 75 76 77 78 79
# 80 81 82 83 84 85 86 87 88 89
# 90 91 92 93 94 95 96 97 98 99


EMPTY, BLACK, WHITE, OUTER = 'E', 'X', 'O', '?'
PIECES = (EMPTY, BLACK, WHITE, OUTER)
PLAYERS = dict(B=BLACK, W=WHITE)

# To refer to neighbor squares we can add a direction to a square.
UP, DOWN, LEFT, RIGHT = -10, 10, -1, 1
UP_RIGHT, DOWN_RIGHT, DOWN_LEFT, UP_LEFT = -9, 11, 9, -11
DIRECTIONS = (UP, UP_RIGHT, RIGHT, DOWN_RIGHT, DOWN, DOWN_LEFT, LEFT, UP_LEFT)


def squares():
    """Valid board index"""
    return [i for i in range(11, 89) if 1 <= (i % 10) <= 8]

CORNERS = [11, 18, 81, 88]

def input_board(text):
    """Input board status"""
    board = [OUTER] * 100
    board_text = list(text)
    player = PLAYERS[board_text.pop(0)]
    j = 0
    for i in squares():
        board[i] = board_text[j]
        j += 1

    return board, player


def show_board(board):
    """Represent current board"""
    rep = ''
    rep += '  1 2 3 4 5 6 7 8\n'
    for row in range(1,9):
        rep += str(row)
        for col in range(1,9):
            rep += ' ' + board[10*row + col]
        rep += '\n'
    rep += '  1 2 3 4 5 6 7 8\n'
    print(rep)


def is_valid(move):
    """Check whether the move is ob board"""
    return isinstance(move, int) and move in squares()


def opponent(player):
    """Get player's opponent piece."""
    return BLACK if player is WHITE else WHITE


def find_bracket(square, player, board, direction):
    """
    Find a square that forms a bracket with `square` for `player` in the given
    `direction`.  Returns None if no such square exists.
    """
    bracket = square + direction
    if board[bracket] == player:
        return None
    opp = opponent(player)
    while board[bracket] == opp:
        bracket += direction
    return None if board[bracket] in (OUTER, EMPTY) else bracket


def is_legal(move, player, board):
    """Is this a legal move for the player?"""
    hasbracket = lambda direction: find_bracket(move, player, board, direction)
    return board[move] == EMPTY and any(map(hasbracket, DIRECTIONS))


def legal_moves(player, board):
    """Get a list of all legal moves for player."""
    return [sq for sq in squares() if is_legal(sq, player, board)]


def any_legal_move(player, board):
    """Can player make any moves?"""
    return any(is_legal(sq, player, board) for sq in squares())


def present_move(move):
    """Print out the move in request format"""
    if move == None:
        print('pass')
    else:
        m = (move//10, move%10)
        print(repr(m).replace(" " , ""))

### Making moves

# When the player makes a move, we need to update the board and flip all the
# bracketed pieces.

def make_move(move, player, board):
    """Update the board to reflect the move by the specified player."""
    board[move] = player
    for d in DIRECTIONS:
        make_flips(move, player, board, d)
    return board


def make_flips(move, player, board, direction):
    """Flip pieces in the given direction as a result of the move by player."""
    bracket = find_bracket(move, player, board, direction)
    if not bracket:
        return
    square = move + direction
    while square != bracket:
        board[square] = player
        square += direction


def score(player, board):
    """Compute player's score (number of player's pieces minus opponent's)."""
    mine, theirs = 0, 0
    opp = opponent(player)
    for sq in squares():
        piece = board[sq]
        if piece == player: mine += 1
        elif piece == opp: theirs += 1
    return mine - theirs


SQUARE_WEIGHTS = [
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
    0, 120, -20,  20,   5,   5,  20, -20, 120,   0,
    0, -20, -40,  -5,  -5,  -5,  -5, -40, -20,   0,
    0,  20,  -5,  15,   3,   3,  15,  -5,  20,   0,
    0,   5,  -5,   3,   3,   3,   3,  -5,   5,   0,
    0,   5,  -5,   3,   3,   3,   3,  -5,   5,   0,
    0,  20,  -5,  15,   3,   3,  15,  -5,  20,   0,
    0, -20, -40,  -5,  -5,  -5,  -5, -40, -20,   0,
    0, 120, -20,  20,   5,   5,  20, -20, 120,   0,
    0,   0,   0,   0,   0,   0,   0,   0,   0,   0,
]

def newWeights(board):
    """compute modified square weights, corner occupicy make different"""
    NEW_WEIGHTS = copy.deepcopy(SQUARE_WEIGHTS)
    for sq in CORNERS:
        if board[sq] != EMPTY:
            for i in neighbour(sq):
                NEW_WEIGHTS[i] *= -3
    return NEW_WEIGHTS

def neighbour(square):
    neighbours = []
    for d in DIRECTIONS:
        neighbours.append(square + d)
    return neighbours

def weighted_score(player, board):
    """
    Compute the difference between the sum of the weights of player's
    squares and the sum of the weights of opponent's squares.
    """
    opp = opponent(player)
    total = 0
    weights = newWeights(board)
    for sq in squares():
        if board[sq] == player:
            total += weights[sq]
        elif board[sq] == opp:
            total -= weights[sq]
    return total



# Values for endgame boards are big constants.
MAX_VALUE = sum(map(abs, SQUARE_WEIGHTS))
MIN_VALUE = -MAX_VALUE

def final_value(player, board):
    """The game is over--find the value of this board to player."""
    diff = score(player, board)
    if diff < 0:
        return MIN_VALUE
    elif diff > 0:
        return MAX_VALUE
    return diff


def alphabeta(player, board, alpha, beta, depth, evaluate):
    """
    Find the best legal move for player, searching to the specified depth.  Like
    minimax, but uses the bounds alpha and beta to prune branches.
    """
    if depth == 0:
        return evaluate(player, board), None

    def value(board, alpha, beta):
        # We pass in `-beta` and `-alpha` as the alpha and beta values.
        # Respectively, for the opponent, since `alpha` represents
        # the best score we know we can achieve and is therefore the worst score
        # achievable by the opponent.  Similarly, `beta` is the worst score that
        # our opponent can hold us to, so it is the best score that they can
        # achieve.
        return -alphabeta(opponent(player), board, -beta, -alpha, depth-1, evaluate)[0]

    moves = legal_moves(player, board)
    if not moves:
        if not any_legal_move(opponent(player), board):
            return final_value(player, board), None
        return value(board, alpha, beta), None

    best_move = moves[0]
    for move in moves:
        if alpha >= beta:
            # If one of the legal moves leads to a better score than beta, then
            # the opponent will avoid this branch, so we can quit looking.
            break
        val = value(make_move(move, player, list(board)), alpha, beta)
        if val > alpha:
            # If one of the moves leads to a better score than the current best
            # achievable score, then replace it with this one.
            alpha = val
            best_move = move
    return alpha, best_move

def alphabeta_searcher(depth, evaluate):
    def strategy(player, board):
        return alphabeta(player, board, MIN_VALUE, MAX_VALUE, depth, evaluate)[1]
    return strategy


if __name__ == '__main__':
    board_in, player = input_board(sys.argv[1])
    time_limit = int(sys.argv[2])
    #show_board(board_in)
    #for m in legal_moves(player, board_in):
        #present_move(m)
    #print(alphabeta(player, board_in, MIN_VALUE, MAX_VALUE, 5, weighted_score))
    if time_limit >= 10:
        DEPTH = 6
    else:
        DEPTH = 5

    best_move = alphabeta(player, board_in, MIN_VALUE, MAX_VALUE, DEPTH, weighted_score)[1]
    present_move(best_move)
