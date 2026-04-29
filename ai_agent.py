from board import Board
import random


MAX_DEPTH = 2  
SCORE_WIN = 100000
SCORE_LOSS = -100000

def evaluate_H1(board):

    if board.check_win(board.board, -1):  # AI wins
        return SCORE_WIN
    if board.check_win(board.board, 1):   # Human wins
        return SCORE_LOSS
    

    available = len(board.get_available_moves())
    return available * 10

def evaluate_H2(board):

    if board.check_win(board.board, -1):
        return SCORE_WIN
    if board.check_win(board.board, 1):
        return SCORE_LOSS
    

    score = 0
    center_positions = [
        (1,1,1), (1,1,2), (1,2,1), (1,2,2),
        (2,1,1), (2,1,2), (2,2,1), (2,2,2)
    ]
    
    for z, y, x in center_positions:
        if board.board[z][y][x] == -1:  # AI
            score += 50
        elif board.board[z][y][x] == 1:  # Human
            score -= 50
    
    return score

def minimax(board, depth, is_maximizing_player, alpha, beta, heuristic_func):

    if depth == 0 or board.is_game_over():
        return heuristic_func(board)
    
    moves = board.get_available_moves()
    
    if not moves:
        return heuristic_func(board)
    
    if is_maximizing_player:  
        max_eval = -999999
        for z, y, x in moves:

            board.board[z][y][x] = -1
            

            eval_score = minimax(board, depth - 1, False, alpha, beta, heuristic_func)
            

            board.board[z][y][x] = 0
            
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            
            # Alpha-Beta Pruning
            if beta <= alpha:
                break
        
        return max_eval
    
    else: 
        min_eval = 999999
        for z, y, x in moves:
            
            board.board[z][y][x] = 1
            
            
            eval_score = minimax(board, depth - 1, True, alpha, beta, heuristic_func)
            
            
            board.board[z][y][x] = 0
            
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            
            # Alpha-Beta Pruning
            if beta <= alpha:
                break
        
        return min_eval

def find_best_move(board):

    # CURRENT_HEURISTIC = evaluate_H1  # 
    CURRENT_HEURISTIC = evaluate_H2  

    moves = board.get_available_moves()
    
    if not moves:
        return None, None, None
    
   
    if len(moves) == 1:
        return moves[0]
    
    
    num_filled = 64 - len(moves)  
    if num_filled <= 2:
        
        center_positions = [
            (1,1,1), (1,1,2), (1,2,1), (1,2,2),
            (2,1,1), (2,1,2), (2,2,1), (2,2,2)
        ]
        
        available_centers = [pos for pos in center_positions if pos in moves]
        
        if available_centers:
            return random.choice(available_centers)
        else:
            
            return random.choice(moves)
    
    best_score = -999999
    best_moves = []  
    
    
    for z, y, x in moves:
        
        board.board[z][y][x] = -1
        
        
        score = minimax(board, MAX_DEPTH - 1, False, -999999, 999999, CURRENT_HEURISTIC)
        
        
        board.board[z][y][x] = 0
        
        
        if score > best_score:
            best_score = score
            best_moves = [(z, y, x)]  
        elif score == best_score:
            
            best_moves.append((z, y, x))
    
    
    if best_moves:
        return random.choice(best_moves)
    
    
    return random.choice(moves)
