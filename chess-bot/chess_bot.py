import chess
import chess.engine
import time

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 300,
    chess.BISHOP: 320,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 10000 
}

transpo_table = {}

def pieceSafety(board):
    safety_score = 0
    for square, piece in board.piece_map().items():
        attackers = len(board.attackers(not piece.color, square))
        defenders = len(board.attackers(piece.color, square))
        if attackers > defenders:
            safety_score -= PIECE_VALUES[piece.piece_type] * 0.5  # Penalize unsafe positions
    return safety_score

def evaluateBoard(board):
    if board.is_checkmate():
        return float('-inf') if board.turn else float('inf')
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    score = 0
    score += pieceSafety(board)

    for piece, value in PIECE_VALUES.items():
        score += len(board.pieces(piece, chess.WHITE)) * value
        score -= len(board.pieces(piece, chess.BLACK)) * value


    for square, piece in board.piece_map().items():
        attackers = board.attackers(not piece.color , square)
        defenders = board.attackers(piece.color, square)
        if len(attackers) > 0 and len(defenders) == 0:
            score -= PIECE_VALUES[piece.piece_type] if piece.color == chess.WHITE else -PIECE_VALUES[piece.piece_type]

    for square in board.pieces(chess.PAWN, chess.WHITE):
        if board.is_attacked_by(chess.BLACK, square):
            score -= 0.2
    
    for square in board.pieces(chess.PAWN, chess.BLACK):
        if board.is_attacked_by(chess.WHITE, square):
            score += 0.2

    if board.has_kingside_castling_rights(chess.WHITE):
        score += 2
    if board.has_kingside_castling_rights(chess.BLACK):
        score -= 2

    if board.is_check():
        score -= 3 if board.turn == chess.WHITE else -3

    return score

def orderMoves(board):
    def score(move):
        piece = board.piece_at(move.to_square)
        CENTRAL_SQUARES = {chess.D4, chess.E4, chess.D5, chess.E5}
        central_bonus = 1 if move.to_square in CENTRAL_SQUARES else 0
        capture_bonus = PIECE_VALUES.get(piece.piece_type, 0) if piece else 0
        development_bonus = 2 if move.to_square in board.attacks(chess.D4) or board.attacks(chess.E4) else 0
        check_bonus = 5 if board.gives_check(move) else 0
        safe_move_bonus = 1 if len(board.attackers(not board.turn, move.to_square)) == 0 else -5
        return central_bonus + capture_bonus + check_bonus + safe_move_bonus + development_bonus

    return sorted(board.legal_moves, key=score, reverse=True)
    
def determineDepth(board):
    numberOfMoves = len(list(board.legal_moves))

    if board.is_check():
        return 6
    if numberOfMoves < 15:
        return 6 if not board.turn else 5
    elif numberOfMoves < 30:
        return 4 if not board.turn else 3
    else:
        return 3
    
#implement alpha beta pruning - game tree
def alphaBetaPruning(board, depth, alpha, beta, player):
    
    if depth == 0 or board.is_game_over():
        return evaluateBoard(board)
    
    hash_board = hash(board.fen())
    
    if hash_board in transpo_table:
        return transpo_table[hash_board]

    
    if player:
        bestValue = float('-inf')
        for move in orderMoves(board):
            board.push(move)
            value = alphaBetaPruning(board, depth-1, alpha, beta, False)
            board.pop()
            bestValue = max(bestValue, value)
            alpha =  max(alpha, bestValue)
            if beta <= alpha:
                break
        transpo_table[hash_board] = bestValue
        return bestValue
    else:
        bestValue = float('inf')
        for move in orderMoves(board):
            board.push(move)
            value = alphaBetaPruning(board, depth-1, alpha, beta, True)
            board.pop()
            bestValue = min(bestValue, value)
            beta = min(beta, bestValue);
            if beta <= alpha:
                break
        transpo_table[hash_board] = bestValue
        return bestValue 
    
#implement create a function that determines the best move based on the alpha beta pruning - returns the best move 
def getBestMove(board, depth):
    bestMove = None
    bestVal = float('-inf')
    alpha = float('-inf')
    beta = float('inf')

    for move in board.legal_moves:
        board.push(move)
        move_value = alphaBetaPruning(board, depth+1, alpha, beta, False)
        board.pop()

        if move_value > bestVal:
            bestVal = move_value
            bestMove = move

    return bestMove

def getBestMoveIterative(board, max_depth, time_limit):
    """Iterative deepening with time control."""
    best_move = None
    start_time = time.time()

    for depth in range(1, max_depth + 1):
        if time.time() - start_time > time_limit:
            break
        best_move = getBestMove(board, depth)
    return best_move

def main():
    board = chess.Board()
    print("Starting new game\n")

    iPlay = input("Enter your color: 1 (White) or 2 (Black): ").strip()

    if iPlay == "1":
        userIsWhite = True
    elif iPlay == "2":
        userIsWhite = False
    else:
        print("Invalid input")

    while not board.is_game_over():
        print("\nCurrent board state:")
        print(board)

        if board.turn == userIsWhite:
            print("\nChess Bot is thinking...")
            move = getBestMoveIterative(board, max_depth=determineDepth(board), time_limit=5)
            board.push(move)
            print(f"\nBot played: {move}")
        else:
            opponentMove = input("\nEnter opponent's move: ").strip()
            try:
                move = chess.Move.from_uci(opponentMove)
                if move in board.legal_moves:
                    board.push(move)
                else:
                    print("Illegal move. Try again.")
            except ValueError:
                print("Invalid input")

    print("Game Over")


if __name__ == '__main__':
    main()