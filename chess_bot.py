import chess
import chess.engine
import time

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 1000 
}

def evaluateBoard(board):
    if board.is_checkmate():
        return float('inf') if board.turn == chess.BLACK else float('-inf')
    if board.is_stalemate():
        return 0
    
    score = 0

    for piece in PIECE_VALUES:
        score += len(board.pieces(piece, chess.WHITE)) * PIECE_VALUES[piece]
        score -= len(board.pieces(piece, chess.BLACK)) * PIECE_VALUES[piece]

    return score


#implement alpha beta pruning - game tree

def alphaBetaPruning(board, depth, alpha, beta, player):
    if depth == 0 or board.is_game_over():
        return evaluateBoard(board)
    
    if player:
        bestValue = float('-inf')
        for move in board.legal_moves:
            board.push(move)
            value = alphaBetaPruning(board, depth-1, alpha, beta, False)
            board.pop()
            bestValue = max(bestValue, value)
            alpha =  max(alpha, bestValue)
            if beta <= alpha:
                break
        return bestValue
    else:
        bestValue = float('inf')
        for move in board.legal_moves:
            board.push(move)
            value = alphaBetaPruning(board, depth-1, alpha, beta, True)
            board.pop()
            bestValue = min(bestValue, value)
            beta = min(beta, bestValue);
            if beta <= alpha:
                break
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

    print("Enter your color: 1 (White) or 2 (Black): ")
    iPlay = input().strip()

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
            move = getBestMoveIterative(board, max_depth=6, time_limit=5)
            board.push(move)
            print(f"\nBot played: {move}")
        else:
            print("Enter opponent's move: ")
            opponentMove = input().strip()
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