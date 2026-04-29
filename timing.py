
import time
import matplotlib.pyplot as plt
import numpy as np
from board import Board
from ai_agent import evaluate_H1, evaluate_H2

# ============================================================================
# 1️⃣ MiniMax WITHOUT Alpha-Beta (بطيء!)
# ============================================================================
def minimax_no_pruning(board, depth, is_maximizing_player, heuristic_func):
    """
    MiniMax عادي بدون Alpha-Beta Pruning
    ⚠️ بطيء جداً! بس عشان المقارنة
    """
    # Base case
    if depth == 0 or board.is_game_over():
        return heuristic_func(board)
    
    moves = board.get_available_moves()
    if not moves:
        return heuristic_func(board)
    
    if is_maximizing_player:  # AI turn
        max_eval = -999999
        for z, y, x in moves:
            board.board[z][y][x] = -1
            eval_score = minimax_no_pruning(board, depth - 1, False, heuristic_func)
            board.board[z][y][x] = 0
            max_eval = max(max_eval, eval_score)
            # ❌ لا يوجد pruning هنا!
        return max_eval
    else:  # Human turn
        min_eval = 999999
        for z, y, x in moves:
            board.board[z][y][x] = 1
            eval_score = minimax_no_pruning(board, depth - 1, True, heuristic_func)
            board.board[z][y][x] = 0
            min_eval = min(min_eval, eval_score)
            # ❌ لا يوجد pruning هنا!
        return min_eval

# ============================================================================
# 2️⃣ MiniMax WITH Alpha-Beta (سريع!)
# ============================================================================
def minimax_with_pruning(board, depth, is_maximizing_player, alpha, beta, heuristic_func):
    """
    MiniMax مع Alpha-Beta Pruning
    ✅ سريع جداً!
    """
    if depth == 0 or board.is_game_over():
        return heuristic_func(board)
    
    moves = board.get_available_moves()
    if not moves:
        return heuristic_func(board)
    
    if is_maximizing_player:
        max_eval = -999999
        for z, y, x in moves:
            board.board[z][y][x] = -1
            eval_score = minimax_with_pruning(board, depth - 1, False, alpha, beta, heuristic_func)
            board.board[z][y][x] = 0
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:  # ✅ Pruning!
                break
        return max_eval
    else:
        min_eval = 999999
        for z, y, x in moves:
            board.board[z][y][x] = 1
            eval_score = minimax_with_pruning(board, depth - 1, True, alpha, beta, heuristic_func)
            board.board[z][y][x] = 0
            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:  # ✅ Pruning!
                break
        return min_eval

# ============================================================================
# 3️⃣ Benchmark Function - المقارنة الكاملة
# ============================================================================
def complete_benchmark(max_depth=2, num_trials=3):
    """
    يقارن كل الاحتمالات:
    1. MiniMax + H1 (بدون pruning)
    2. MiniMax + H2 (بدون pruning)
    3. Alpha-Beta + H1 (مع pruning)
    4. Alpha-Beta + H2 (مع pruning)
    """
    
    results = {
        'depths': [],
        'minimax_h1': [],      # MiniMax without pruning + H1
        'minimax_h2': [],      # MiniMax without pruning + H2
        'alphabeta_h1': [],    # Alpha-Beta + H1
        'alphabeta_h2': []     # Alpha-Beta + H2
    }
    
    print("\n" + "="*80)
    print("🎮 COMPLETE ALGORITHM COMPARISON - 4x4x4 QUBIC")
    print("="*80)
    print("\n⚠️  WARNING: MiniMax without pruning is VERY SLOW!")
    print("   Recommended: max_depth=2 only\n")
    
    for depth in range(1, max_depth + 1):
        print(f"\n{'='*80}")
        print(f"📊 TESTING DEPTH = {depth}")
        print(f"{'='*80}\n")
        
        times = {
            'minimax_h1': [],
            'minimax_h2': [],
            'alphabeta_h1': [],
            'alphabeta_h2': []
        }
        
        for trial in range(num_trials):
            print(f"🔄 Trial {trial + 1}/{num_trials}")
            print("-" * 60)
            
            # Setup test board
            board = Board()
            board.make_move(1, 1, 1, 1)   # Player
            board.make_move(2, 2, 2, -1)  # AI
            
            moves = board.get_available_moves()
            test_move = moves[0] if moves else None
            
            if not test_move:
                continue
            
            # Test 1: MiniMax + H1 (No Pruning)
            print("  🔴 MiniMax (No Pruning) + H1... ", end='', flush=True)
            board_copy = Board()
            board_copy.board = [[[board.board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
            
            start = time.time()
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = -1
            score = minimax_no_pruning(board_copy, depth - 1, False, evaluate_H1)
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = 0
            elapsed = time.time() - start
            times['minimax_h1'].append(elapsed)
            print(f"{elapsed:.4f}s")
            
            # Test 2: MiniMax + H2 (No Pruning)
            print("  🔴 MiniMax (No Pruning) + H2... ", end='', flush=True)
            board_copy = Board()
            board_copy.board = [[[board.board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
            
            start = time.time()
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = -1
            score = minimax_no_pruning(board_copy, depth - 1, False, evaluate_H2)
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = 0
            elapsed = time.time() - start
            times['minimax_h2'].append(elapsed)
            print(f"{elapsed:.4f}s")
            
            # Test 3: Alpha-Beta + H1
            print("  🟢 Alpha-Beta + H1... ", end='', flush=True)
            board_copy = Board()
            board_copy.board = [[[board.board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
            
            start = time.time()
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = -1
            score = minimax_with_pruning(board_copy, depth - 1, False, -999999, 999999, evaluate_H1)
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = 0
            elapsed = time.time() - start
            times['alphabeta_h1'].append(elapsed)
            print(f"{elapsed:.4f}s")
            
            # Test 4: Alpha-Beta + H2
            print("  🟢 Alpha-Beta + H2... ", end='', flush=True)
            board_copy = Board()
            board_copy.board = [[[board.board[z][y][x] for x in range(4)] for y in range(4)] for z in range(4)]
            
            start = time.time()
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = -1
            score = minimax_with_pruning(board_copy, depth - 1, False, -999999, 999999, evaluate_H2)
            board_copy.board[test_move[0]][test_move[1]][test_move[2]] = 0
            elapsed = time.time() - start
            times['alphabeta_h2'].append(elapsed)
            print(f"{elapsed:.4f}s\n")
        
        # Calculate averages
        results['depths'].append(depth)
        results['minimax_h1'].append(np.mean(times['minimax_h1']))
        results['minimax_h2'].append(np.mean(times['minimax_h2']))
        results['alphabeta_h1'].append(np.mean(times['alphabeta_h1']))
        results['alphabeta_h2'].append(np.mean(times['alphabeta_h2']))
        
        # Print summary
        print(f"{'='*80}")
        print(f"✅ DEPTH {depth} SUMMARY:")
        print(f"{'='*80}")
        print(f"  MiniMax (No Pruning) + H1: {results['minimax_h1'][-1]:.4f}s")
        print(f"  MiniMax (No Pruning) + H2: {results['minimax_h2'][-1]:.4f}s")
        print(f"  Alpha-Beta + H1:           {results['alphabeta_h1'][-1]:.4f}s")
        print(f"  Alpha-Beta + H2:           {results['alphabeta_h2'][-1]:.4f}s")
        print(f"\n  🚀 Speedup with Alpha-Beta:")
        speedup_h1 = results['minimax_h1'][-1] / results['alphabeta_h1'][-1]
        speedup_h2 = results['minimax_h2'][-1] / results['alphabeta_h2'][-1]
        print(f"     H1: {speedup_h1:.1f}x faster")
        print(f"     H2: {speedup_h2:.1f}x faster")
        print()
    
    return results

# ============================================================================
# 4️⃣ Plotting Function - رسم المقارنة الكاملة
# ============================================================================
def plot_complete_comparison(results):
    """
    رسم شامل يوضح كل المقارنات
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # ============ Plot 1: All Algorithms Together ============
    ax = axes[0, 0]
    ax.plot(results['depths'], results['minimax_h1'], 
            'o-', label='MiniMax (No Pruning) + H1', 
            linewidth=2.5, markersize=10, color='#e74c3c')
    ax.plot(results['depths'], results['minimax_h2'], 
            's-', label='MiniMax (No Pruning) + H2', 
            linewidth=2.5, markersize=10, color='#c0392b')
    ax.plot(results['depths'], results['alphabeta_h1'], 
            '^-', label='Alpha-Beta + H1', 
            linewidth=2.5, markersize=10, color='#3498db')
    ax.plot(results['depths'], results['alphabeta_h2'], 
            'd-', label='Alpha-Beta + H2', 
            linewidth=2.5, markersize=10, color='#2ecc71')
    
    ax.set_xlabel('Depth', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Complete Comparison - All Algorithms', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # ============ Plot 2: Heuristic 1 Comparison ============
    ax = axes[0, 1]
    ax.plot(results['depths'], results['minimax_h1'], 
            'o-', label='MiniMax + H1', 
            linewidth=3, markersize=12, color='#e74c3c')
    ax.plot(results['depths'], results['alphabeta_h1'], 
            '^-', label='Alpha-Beta + H1', 
            linewidth=3, markersize=12, color='#3498db')
    
    # Add speedup annotations
    for i, depth in enumerate(results['depths']):
        speedup = results['minimax_h1'][i] / results['alphabeta_h1'][i]
        mid_y = np.sqrt(results['minimax_h1'][i] * results['alphabeta_h1'][i])
        ax.annotate(f'{speedup:.1f}x', 
                   xy=(depth, mid_y), 
                   fontsize=10, fontweight='bold', color='green',
                   ha='center')
    
    ax.set_xlabel('Depth', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Heuristic 1: MiniMax vs Alpha-Beta', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # ============ Plot 3: Heuristic 2 Comparison ============
    ax = axes[1, 0]
    ax.plot(results['depths'], results['minimax_h2'], 
            's-', label='MiniMax + H2', 
            linewidth=3, markersize=12, color='#c0392b')
    ax.plot(results['depths'], results['alphabeta_h2'], 
            'd-', label='Alpha-Beta + H2', 
            linewidth=3, markersize=12, color='#2ecc71')
    
    # Add speedup annotations
    for i, depth in enumerate(results['depths']):
        speedup = results['minimax_h2'][i] / results['alphabeta_h2'][i]
        mid_y = np.sqrt(results['minimax_h2'][i] * results['alphabeta_h2'][i])
        ax.annotate(f'{speedup:.1f}x', 
                   xy=(depth, mid_y), 
                   fontsize=10, fontweight='bold', color='green',
                   ha='center')
    
    ax.set_xlabel('Depth', fontsize=12, fontweight='bold')
    ax.set_ylabel('Time (seconds)', fontsize=12, fontweight='bold')
    ax.set_title('Heuristic 2: MiniMax vs Alpha-Beta', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    
    # ============ Plot 4: Speedup Comparison ============
    ax = axes[1, 1]
    speedup_h1 = [results['minimax_h1'][i] / results['alphabeta_h1'][i] 
                  for i in range(len(results['depths']))]
    speedup_h2 = [results['minimax_h2'][i] / results['alphabeta_h2'][i] 
                  for i in range(len(results['depths']))]
    
    x = np.arange(len(results['depths']))
    width = 0.35
    
    bars1 = ax.bar(x - width/2, speedup_h1, width, label='H1 Speedup', color='#3498db')
    bars2 = ax.bar(x + width/2, speedup_h2, width, label='H2 Speedup', color='#2ecc71')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}x',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    ax.set_xlabel('Depth', fontsize=12, fontweight='bold')
    ax.set_ylabel('Speedup Factor', fontsize=12, fontweight='bold')
    ax.set_title('Alpha-Beta Pruning Speedup', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(results['depths'])
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.axhline(y=1, color='red', linestyle='--', linewidth=2, alpha=0.5)
    
    plt.tight_layout()
    plt.savefig('complete_algorithm_comparison.png', dpi=300, bbox_inches='tight')
    print("\n✅ Complete comparison plot saved!")
    plt.show()

# ============================================================================
# 5️⃣ Main Execution
# ============================================================================
if __name__ == "__main__":
    print("\n" + "🎮"*40)
    print("     COMPLETE ALGORITHM COMPARISON")
    print("     4x4x4 QUBIC - All Variants")
    print("🎮"*40 + "\n")
    
    print("⚠️  IMPORTANT:")
    print("   This compares ALL 4 algorithm variants:")
    print("   1. MiniMax (No Pruning) + Heuristic 1")
    print("   2. MiniMax (No Pruning) + Heuristic 2")
    print("   3. Alpha-Beta Pruning + Heuristic 1")
    print("   4. Alpha-Beta Pruning + Heuristic 2")
    print("\n   ⏰ MiniMax without pruning is VERY slow!")
    print("   📊 Recommended: depth=2 max (takes ~2-5 minutes)\n")
    
    choice = input("Choose max depth:\n  [1] Quick (depth=1)\n  [2] Recommended (depth=2) ⭐\n  [3] Slow (depth=3) ⚠️\n\nChoice: ")
    
    if choice == '1':
        max_depth = 1
    elif choice == '3':
        max_depth = 3
    else:
        max_depth = 2
    
    print(f"\n✅ Running complete benchmark (max_depth={max_depth})...")
    print("⏳ This will take a few minutes...\n")
    
    results = complete_benchmark(max_depth=max_depth, num_trials=3)
    plot_complete_comparison(results)
    
    print("\n" + "="*80)
    print("🎉 BENCHMARK COMPLETE!")
    print("="*80)
    print("\n📁 Generated: complete_algorithm_comparison.png")
    print("\n✅ You now have ALL comparisons you need for your report!")