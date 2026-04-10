import numpy as np
import math
import copy
import time
import threading


# This is Team ace :)
# Made by Ahmed Mohammed & Abdullah Mohammad Aref
class GomokuAgent:

    # To check the state of the board
    def available_moves(self, board):
        moves = []
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell == 0:
                    moves.append((i, j))
        return moves

    def player(self, board):
        p2_count = 0
        p1_count = 0
        for row in board:
            for cell in row:
                if cell == 2:
                    p2_count += 1
                elif cell == 1:
                    p1_count += 1

        # To know which player is next
        if p1_count > p2_count:
            return 2
        elif p2_count > p1_count:
            return 1
        else:
            return 1  # P1 is first

    # Make a move
    def next_move(self, board, move):
        outcome = copy.deepcopy(board)
        row, col = move
        player = self.player(board)  # whose turn is it?
        outcome[row][col] = player
        return outcome

    # Winner function and assign/identify pieces for each agent
    def winner_checker(self, board):
        my_agent_pieces = set()
        opponent_pieces = set()

        # generate and fine the winning patterns
        winning_patterns = self._generate_winning_patterns()

        # get all the pieces on the board
        for i, row in enumerate(board):
            for j, cell in enumerate(row):
                if cell == self.agent_symbol:
                    my_agent_pieces.add((i, j))
                elif cell == self.enemy_piece:
                    opponent_pieces.add((i, j))

        # Check if any of the generated winning patterns is satisfied
        for pattern in winning_patterns:
            if pattern.issubset(my_agent_pieces):
                return self.agent_symbol
            elif pattern.issubset(opponent_pieces):
                return self.enemy_piece

        return self.free_space

    # Helper function to generate winning patterns - added this to clean up the code
    def _generate_winning_patterns(self):
        patterns = []
        board_size = 15
        win_length = 5

        # r for rows and c for columns :)

        # Horizontal patterns
        for r in range(board_size):
            for c in range(board_size - win_length + 1):
                pattern = set((r, c + i) for i in range(win_length))
                patterns.append(pattern)

        # Vertical patterns
        for c in range(board_size):
            for r in range(board_size - win_length + 1):
                pattern = set((r + i, c) for i in range(win_length))
                patterns.append(pattern)

        # Diagonal patterns (top-left to bottom-right)
        for r in range(board_size - win_length + 1):
            for c in range(board_size - win_length + 1):
                pattern = set((r + i, c + i) for i in range(win_length))
                patterns.append(pattern)

        # Diagonal patterns (top-right to bottom-left)
        for r in range(board_size - win_length + 1):
            for c in range(win_length - 1, board_size):
                pattern = set((r + i, c - i) for i in range(win_length))
                patterns.append(pattern)

        return patterns

    def end_game(self, board):
        # Check for a winner
        if self.winner_checker(board) != self.free_space:
            return True

        # Check if the board is full
        for row in board:
            for cell in row:
                if cell == self.free_space:
                    return False
        return True

    def utility(self, board):
        # Simple utility function
        if self.winner_checker(board) == self.agent_symbol:
            return 1
        elif self.winner_checker(board) == self.enemy_piece:
            return -1
        else:
            return 0

    # Main agent code
    def __init__(self, agent_symbol, free_space, enemy_piece):
        self.name = __name__
        self.agent_symbol = agent_symbol
        self.free_space = free_space
        self.enemy_piece = enemy_piece

        self.board_size = 15
        self.win_length = 5  # gomoku so 5 in a row :)
        self.max_depth = 3  # depth of the search
        self.transposition_table = {}
        self.max_time = 5  # Almost 5 seconds per move
        self.forced_win_sequence = None
        self.sorted_moves_cache = {}

        # Pattern scores for evaluation

        self.patterns = {
            # Win
            (1, 1, 1, 1, 1): 1000000,

            # Open Four
            (0, 1, 1, 1, 1, 0): 200000,

            # Four
            (1, 1, 1, 1, 0): 20000,
            (0, 1, 1, 1, 1): 20000,
            (1, 1, 0, 1, 1): 20000,
            (1, 0, 1, 1, 1): 20000,
            (1, 1, 1, 0, 1): 20000,

            # Open Three
            (0, 1, 1, 1, 0): 2500,
            (0, 1, 1, 0, 1, 0): 2500,
            (0, 1, 0, 1, 1, 0): 2500,
            (0, 0, 1, 1, 1, 0, 0): 3000,

            # Three
            (1, 1, 1, 0, 0): 200,
            (0, 0, 1, 1, 1): 200,
            (1, 0, 1, 1, 0): 200,
            (0, 1, 1, 0, 1): 200,
            (1, 1, 0, 1, 0): 200,
            (0, 1, 0, 1, 1): 200,

            # Double-Threat
            (0, 1, 1, 0, 1, 0): 3000,
            (0, 1, 0, 1, 1, 0): 3000,
            (0, 1, 0, 0, 1, 1, 0): 1500,
            (0, 1, 1, 0, 0, 1, 0): 1500,

            # Open Two
            (0, 1, 1, 0, 0, 0): 30,
            (0, 0, 0, 1, 1, 0): 30,
            (0, 1, 0, 1, 0, 0): 30,
            (0, 0, 1, 0, 1, 0): 30,
            (0, 0, 1, 1, 0, 0, 0): 40,
            (0, 0, 0, 1, 1, 0, 0): 40,

            # after testing we added these patterns
            (0, 1, 0, 1, 0, 1, 0): 800,
            (0, 1, 1, 0, 0, 1, 0): 600,
            (0, 1, 0, 0, 1, 1, 0): 600,
            (0, 1, 1, 0, 1, 0, 0): 700,
            (0, 0, 1, 0, 1, 1, 0): 700,
        }

        # Counter patterns aka our defence
        self.opponent_patterns = {
            # MUST block these
            (0, -1, -1, -1, 0): 8000,
            (0, -1, -1, -1, -1, 0): 150000,  # open four - highest priority
            (-1, -1, -1, -1, 0): 18000,
            (0, -1, -1, -1, -1): 18000,
            (-1, -1, 0, -1, -1): 18000,
            (0, -1, -1, 0, -1, 0): 6000,
            (0, -1, 0, -1, -1, 0): 6000,

            # Other blocking patterns
            (0, 0, -1, -1, -1, 0, 0): 10000,
            (0, -1, 0, -1, 0, -1, 0): 3000,
            (0, -1, -1, 0, 0, -1, 0): 2500,
            (0, -1, 0, 0, -1, -1, 0): 2500,
        }

        # common situations
        self.common_playbook = {}
        self._init_openings()

        # For parallel search
        self.best_play = None
        self.search_done = False

    def _init_openings(self):

        # Set up some basic opening moves and responses
        center = self.board_size // 2

        # Empty board -> play center
        empty = np.zeros((self.board_size, self.board_size))
        self.common_playbook[hash(empty.tobytes())] = (center, center)

        # If opponent plays center, play adjacent
        board = np.zeros((self.board_size, self.board_size))
        board[center, center] = self.enemy_piece
        self.common_playbook[hash(board.tobytes())] = (center, center + 1)

        # other tested openings
        board = np.zeros((self.board_size, self.board_size))
        board[center, center] = self.enemy_piece
        board[center + 1, center + 1] = self.enemy_piece
        self.common_playbook[hash(board.tobytes())] = (center + 1, center)

    def play(self, board):

        # Main function to choose the best move

        start_time = time.time()
        self.best_play = None
        self.search_done = False

        # check our playbook :)
        board_hash = hash(board.tobytes())
        if board_hash in self.common_playbook:
            return self.common_playbook[board_hash]

        # place center if the board is empty
        if np.sum(board != self.free_space) == 0:
            return (self.board_size // 2, self.board_size // 2)

        # Continue with a winning sequence if we have one
        if self.forced_win_sequence and len(self.forced_win_sequence) > 0:
            move = self.forced_win_sequence.pop(0)
            if board[move[0], move[1]] == self.free_space:
                return move
            self.forced_win_sequence = None  # Invalid sequence

        # check for wins
        winning_moves = self.find_winning_moves(board, self.agent_symbol)
        if winning_moves:
            return winning_moves[0]

        # Check if blocks are needed
        blocking_moves = self.find_winning_moves(board, self.enemy_piece)
        if blocking_moves:
            return blocking_moves[0]

        # Look for moves that create multiple threats
        double_threat_moves = self.double_threat_detection(board)
        if double_threat_moves:
            return double_threat_moves[0]

        # Adjust search depth based on game phase
        pieces = np.sum(board != self.free_space)
        if pieces < 6:
            self.max_depth = 5
        elif pieces < 12:
            self.max_depth = 4
        elif pieces < 25:
            self.max_depth = 3
        else:
            self.max_depth = 2  # late game, too many options

        # Get the best moves to consider
        sorted_moves = self.get_sorted_moves(board)

        # Only one option? Take it.
        if len(sorted_moves) == 1:
            return sorted_moves[0]

        # Start a parallel search for winning sequences
        threading.Thread(target=self.search_forced_win, args=(board.copy(),)).start()

        # iterative deepening
        best_move = sorted_moves[0]  # Default to first move

        for depth in range(1, self.max_depth + 1):
            # Check if we have time for another iteration
            if time.time() - start_time > self.max_time * 0.5:
                break

            # Check if our parallel search found something
            if self.search_done and self.best_play:
                return self.best_play

            # Run minimax search with current depth
            minimax = MiniMaxTree(sorted_moves, start_time=start_time, agent=self,
                                  time_limit=self.max_time, depth_limit=depth)
            move = minimax.minmax_alpha_beta(board)

            if move is not None:
                best_move = move
            else:
                # Ran out of time
                break

        # If we have time, try to refine our choice
        elapsed = time.time() - start_time
        if elapsed < self.max_time * 0.75:
            refined = self.better_move(board, best_move, start_time)
            if refined:
                best_move = refined

        # check if our parallel search found a win
        if self.search_done and self.best_play:
            return self.best_play

        return best_move

    def search_forced_win(self, board):

        # use threads to find forced wins
        try:
            move, sequence = self.proof_nsearch(board.copy(), max_time=3.0)
            if move:
                self.best_play = move
                self.forced_win_sequence = sequence if sequence else []
            self.search_done = True

        except Exception as e:

            self.search_done = True

    def proof_nsearch(self, board, max_time=3.0):
        # find a forced win sequencE
        start_time = time.time()

        # find quick wins at shallow depths
        for depth in range(1, 4):
            if time.time() - start_time > max_time * 0.5:
                break

            # check possible moves
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if board[i, j] == self.free_space:
                        board_copy = board.copy()
                        board_copy[i, j] = self.agent_symbol

                        # check if it makes u win
                        win, seq = self.check_forced_win(board_copy, depth, start_time, max_time)
                        if win:
                            return (i, j), seq

        return None, None

    def check_forced_win(self, board, depth, start_time, max_time):
        """Check if there's a forced win from this position"""
        # Time check
        if time.time() - start_time > max_time * 0.8:
            return False, None

        # win check
        if self.winner_checker(board) == self.agent_symbol:
            return True, []

        # depth check if no depth
        if depth <= 0:
            return False, None

        # Look for threatening moves
        threats = self.dangerous_threats(board)
        if not threats:
            return False, None

        # Try each threat
        for move in threats:
            board_copy = board.copy()
            row, col = move
            board_copy[row, col] = self.agent_symbol

            # check enemy reaction
            opponent_forced = self.find_winning_moves(board_copy, self.enemy_piece)

            # If multiple forced responses, not a forced win
            if len(opponent_forced) > 1:
                continue

            # If exactly one forced response
            if len(opponent_forced) == 1:
                # Apply opponent's forced move
                reply = opponent_forced[0]
                board_copy[reply[0], reply[1]] = self.enemy_piece

                # winable?
                win, seq = self.check_forced_win(board_copy, depth - 1, start_time, max_time)
                if win:
                    sequence = [move]
                    if seq:
                        sequence.extend(seq)
                    return True, sequence
            else:

                win, seq = self.check_forced_win(board_copy, depth - 1, start_time, max_time)
                if win:
                    sequence = [move]
                    if seq:
                        sequence.extend(seq)
                    return True, sequence

        return False, None

    def dangerous_threats(self, board):
        """Find moves that create critical threats"""
        threats = []

        # Check possible threats
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space:
                    # Try this move
                    board_copy = board.copy()
                    board_copy[i, j] = self.agent_symbol

                    # Immediate win?
                    if self.winner_checker(board_copy) == self.agent_symbol:
                        return [(i, j)]

                    # Check threat level
                    threat_level = self.threat_level(board_copy, i, j, self.agent_symbol)
                    if threat_level > 0:
                        threats.append(((i, j), threat_level))

        # Sort by threat level
        if threats:
            threats.sort(key=lambda x: x[1], reverse=True)
            return [move for move, _ in threats]

        return []

    def threat_level(self, board, row, col, player):

        # Count different threat types
        open_four_count = 0
        four_count = 0
        open_three_count = 0

        # Check all directions
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dx, dy in directions:
            # Check for four in a row with one end open
            if self.check_pattern(board, row, col, dx, dy, [player, player, player, player, self.free_space]) or \
                    self.check_pattern(board, row, col, dx, dy, [self.free_space, player, player, player, player]):
                four_count += 1

            # Check for four with both ends open
            if self.check_pattern(board, row, col, dx, dy,
                                  [self.free_space, player, player, player, player, self.free_space]):
                open_four_count += 1

            # Check for open three
            if self.check_pattern(board, row, col, dx, dy,
                                  [self.free_space, player, player, player, self.free_space]):
                open_three_count += 1

        # Calculate overall threat level
        threat = open_four_count * 100 + four_count * 10 + open_three_count

        # Bonuses for multiple threats
        if open_four_count > 0:
            threat += 500  # Open four is very dangerous
        if four_count > 0 and open_three_count > 0:
            threat += 200  # Combo threat
        if open_three_count > 1:
            threat += 300  # Multiple open threes

        return threat

    def check_pattern(self, board, row, col, dx, dy, pattern):

        # Make sure pattern fits on board

        if not (0 <= row + dx * (len(pattern) - 1) < self.board_size and
                0 <= col + dy * (len(pattern) - 1) < self.board_size):
            return False

        # check each position
        for k, value in enumerate(pattern):
            r, c = row + dx * k, col + dy * k
            if r < 0 or r >= self.board_size or c < 0 or c >= self.board_size:
                return False
            if board[r, c] != value:
                return False

        return True

    def get_sorted_moves(self, board):
        """Get legal moves sorted by potential value"""
        moves = []

        # check immediate wins
        winning_moves = self.find_winning_moves(board, self.agent_symbol)
        if winning_moves:
            return winning_moves

        # check for blocks
        blocking_moves = self.find_winning_moves(board, self.enemy_piece)
        if blocking_moves:
            return blocking_moves

        # Look for double threats
        double_threats = self.double_threat_detection(board)
        if double_threats:
            return double_threats

        # look for single threats
        threatening_moves = self.find_threatening_moves(board)
        if threatening_moves:
            return threatening_moves

        # chck cached values if available
        board_hash = hash(board.tobytes())
        if board_hash in self.sorted_moves_cache:
            return self.sorted_moves_cache[board_hash][:15]  # Top 15 moves

        # Consider moves near existing pieces
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space:
                    if not self.has_neighbor(board, i, j):
                        continue  # Skip isolated moves

                    score = self.calc_position_score_value(board, i, j)
                    moves.append(((i, j), score))

        # Sort by score
        if moves:
            moves.sort(key=lambda x: x[1], reverse=True)
            sorted_moves = [move[0] for move in moves]
            # Cache for future use
            self.sorted_moves_cache[board_hash] = sorted_moves
            return sorted_moves

        empties = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space:
                    empties.append((i, j))

        return empties[:10] if empties else [(self.board_size // 2, self.board_size // 2)]

    def find_winning_moves(self, board, player):

        # Find moves that immediately win
        winners = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space:
                    test_board = board.copy()
                    test_board[i, j] = player

                    if self.winner_checker(test_board) == player:
                        winners.append((i, j))
        return winners

    def double_threat_detection(self, board):
        double_threats = []

        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space and self.has_neighbor(board, i, j):
                    test_board = board.copy()
                    test_board[i, j] = self.agent_symbol

                    # Count the threats in different directions
                    threat_count = 0
                    dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]

                    for dx, dy in dirs:
                        # Check for open three threats
                        if self.check_open_three(test_board, i, j, dx, dy, self.agent_symbol):
                            threat_count += 1

                        # Check for open four threats
                        if self.check_open_four(test_board, i, j, dx, dy, self.agent_symbol):
                            threat_count += 2  # Counts double

                    # Multiple threats checker
                    if threat_count >= 2:
                        double_threats.append((i, j))

        return double_threats

    def check_open_three(self, board, row, col, dx, dy, player):

        # check for an open three
        count = 1
        space_after = 0

        # Check forward
        r, c = row + dx, col + dy
        while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == player:
            count += 1
            r += dx
            c += dy

        # space after
        if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == self.free_space:
            space_after = 1

        # backward
        r, c = row - dx, col - dy
        while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == player:
            count += 1
            r -= dx
            c -= dy

        # before
        space_before = 0
        if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == self.free_space:
            space_before = 1

        # Open three has 3 stones and space on both ends
        return count == 3 and space_before == 1 and space_after == 1

    def check_open_four(self, board, row, col, dx, dy, player):
        # Check for an open four
        count = 1
        space_after = 0

        # forward
        r, c = row + dx, col + dy
        while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == player:
            count += 1
            r += dx
            c += dy

        # after :)
        if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == self.free_space:
            space_after = 1

        # backward
        r, c = row - dx, col - dy
        while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == player:
            count += 1
            r -= dx
            c -= dy

        # before?
        space_before = 0
        if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == self.free_space:
            space_before = 1

        # Open four has 4 stones and at least one open end
        return count == 4 and (space_before == 1 or space_after == 1)

    def find_threatening_moves(self, board):

        # Find moves that create threats
        threats = []

        # Check all empty spaces
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space and self.has_neighbor(board, i, j):
                    test_board = board.copy()
                    test_board[i, j] = self.agent_symbol

                    # count open lines
                    our_threes = self.count_open_lines(test_board, i, j, self.agent_symbol, 3)
                    our_fours = self.count_open_lines(test_board, i, j, self.agent_symbol, 4)

                    # Check defensive value
                    test_board[i, j] = self.enemy_piece
                    their_threes = self.count_open_lines(test_board, i, j, self.enemy_piece, 3)
                    their_fours = self.count_open_lines(test_board, i, j, self.enemy_piece, 4)

                    # Combined score
                    threat_score = (our_fours * 300 + our_threes * 30 +
                                    their_fours * 250 + their_threes * 25)

                    if threat_score > 0:
                        threats.append(((i, j), threat_score))

        # Sort by score
        if threats:
            threats.sort(key=lambda x: x[1], reverse=True)
            return [move[0] for move in threats]

        return []

    def has_neighbor(self, board, row, col, distance=2):
        # Check if position has any pieces nearby
        for i in range(max(0, row - distance), min(self.board_size, row + distance + 1)):
            for j in range(max(0, col - distance), min(self.board_size, col + distance + 1)):
                if board[i, j] != self.free_space:
                    return True
        return False

    def calc_position_score_value(self, board, row, col):

        # Score for playing at this position
        our_board = board.copy()
        our_board[row, col] = self.agent_symbol
        score_with = self.evaluate(our_board)

        # blocking
        their_board = board.copy()
        their_board[row, col] = self.enemy_piece
        score_against = -self.evaluate(their_board)

        # Balance scale offense and defense
        return score_with + score_against * 2.0  # Defense is more important

    def better_move(self, board, candidate_move, start_time):
        # Check if there is a better move
        test_board = board.copy()
        row, col = candidate_move
        test_board[row, col] = self.agent_symbol

        # if this creates a winning threat, keep it!
        if self.is_winning_threat(test_board, self.agent_symbol):
            return candidate_move

        # check other moves
        for r in range(self.board_size):
            for c in range(self.board_size):

                # Time check
                if time.time() - start_time > self.max_time * 0.9:
                    return candidate_move

                if board[r, c] == self.free_space:
                    alt_board = board.copy()
                    alt_board[r, c] = self.agent_symbol

                    # check this move
                    threat_count = self.count_threats(alt_board, self.agent_symbol)
                    block_value = self.counter_value(board, r, c)
                    pos_value = self.calc_position_score_value(board, r, c)

                    # Combined score
                    total_score = threat_count * 100 + block_value * 80 + pos_value

                    # compare to candidate
                    current_score = self.calc_position_score_value(board, row, col)
                    if total_score > current_score * 1.5:
                        return (r, c)

                    # double threat
                    if self.count_threats(alt_board, self.agent_symbol) > 1:
                        return (r, c)

        return candidate_move

    def counter_value(self, board, row, col):
        # Place opponent's piece
        test_board = board.copy()
        test_board[row, col] = self.enemy_piece

        # count the threats
        threes = self.count_open_lines(test_board, row, col, self.enemy_piece, 3)
        fours = self.count_open_lines(test_board, row, col, self.enemy_piece, 4)

        # Weighted score
        return fours * 100 + threes * 30

    def is_winning_threat(self, board, player):
        # check if there's a winning threat
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == self.free_space:
                    test_board = board.copy()
                    test_board[i, j] = player

                    if self.winner_checker(test_board) == player:
                        return True

        return False

    def count_threats(self, board, player):
        # Count threats on the board
        threats = 0

        # Check for open threes and open fours
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i, j] == player:
                    # Check all directions
                    dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
                    for dx, dy in dirs:
                        # for open fours
                        if self.check_pattern(board, i, j, dx, dy,
                                              [player, player, player, player, self.free_space]):
                            threats += 1
                        # open threes
                        if self.check_pattern(board, i, j, dx, dy,
                                              [player, player, player, self.free_space, self.free_space]):
                            threats += 1

        return threats

    def evaluate(self, board):

        # Evaluate board position
        score = 0

        # check patterns in all directions
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]

        # scan the board
        for i in range(self.board_size):
            for j in range(self.board_size):
                for dx, dy in dirs:
                    score += self.evaluate_patterns(board, i, j, dx, dy, self.agent_symbol)
                    score -= self.evaluate_patterns(board, i, j, dx, dy,
                                                    self.enemy_piece) * 1.5

        return score

    def evaluate_patterns(self, board, row, col, dx, dy, player):
        # Evaluate patterns in one direction
        score = 0

        # Check patterns of length 5 and 6
        for pattern_len in range(5, 7):
            if (row + dx * (pattern_len - 1) >= self.board_size or
                    row + dx * (pattern_len - 1) < 0 or
                    col + dy * (pattern_len - 1) >= self.board_size or
                    col + dy * (pattern_len - 1) < 0):
                continue

            pattern = []
            for k in range(pattern_len):
                r, c = row + k * dx, col + k * dy
                if board[r, c] == player:
                    pattern.append(1)  # Our piece
                elif board[r, c] == self.free_space:
                    pattern.append(0)  # Empty
                else:
                    pattern.append(-1)  # enemy

            # change to tuple
            pattern_tuple = tuple(pattern)

            # Check pattern
            if player == self.agent_symbol:
                for p, p_score in self.patterns.items():
                    if len(p) == len(pattern_tuple):
                        # check if pattern matches or not
                        match = True
                        for idx, val in enumerate(p):
                            if val == 1 and pattern_tuple[idx] != 1:
                                match = False
                                break
                            if val == 0 and pattern_tuple[idx] != 0:
                                match = False
                                break

                        if match:
                            score += p_score
            else:
                # enemy patterns
                for p, p_score in self.opponent_patterns.items():
                    if len(p) == len(pattern_tuple):
                        # check if pattern matches
                        match = True
                        for idx, val in enumerate(p):
                            if val == -1 and pattern_tuple[idx] != 1:
                                match = False
                                break
                            if val == 0 and pattern_tuple[idx] != 0:
                                match = False
                                break

                        if match:
                            score += p_score

        return score

    def count_open_lines(self, board, row, col, player, length):
        # Count open lines of given length
        dirs = [(0, 1), (1, 0), (1, 1), (1, -1)]
        count = 0

        for dx, dy in dirs:
            # Check both directions
            stones = 1  # Current stone
            open_ends = 0

            # forward direction
            r, c = row + dx, col + dy
            while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == player:
                stones += 1
                r += dx
                c += dy

            # check for open end
            if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == self.free_space:
                open_ends += 1

            # backward direction
            r, c = row - dx, col - dy
            while 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == player:
                stones += 1
                r -= dx
                c -= dy

            # check if other side open
            if 0 <= r < self.board_size and 0 <= c < self.board_size and board[r, c] == self.free_space:
                open_ends += 1

            # count if the length and at least one open end
            if stones == length and open_ends > 0:
                count += 1

        return count


# Minimax implementation
class MiniMaxTree:
    def __init__(self, legal_moves, start_time, agent, time_limit=5, depth_limit=3):
        self.time_limit = time_limit
        self.agent = agent
        self.alpha = -math.inf
        self.beta = math.inf
        self.start_time = start_time
        self.depth_limit = depth_limit
        self.nodes_counter = 0  # for debugging ^_^
        self.legal_moves = legal_moves

    def min_value(self, board, alpha, beta, depth):
        depth += 1
        first_try = True
        self.nodes_counter += 1

        # Terminal state
        if self.agent.end_game(board):
            if self.agent.utility(board) == 1:
                return 1000000, depth  # We win
            elif self.agent.utility(board) == -1:
                return -1000000, depth  # We lose
            else:
                return self.agent.evaluate(board), depth  # Draw

        # check if Depth limit reached
        if depth == self.depth_limit:
            return self.agent.evaluate(board), depth

        # Time check
        if (time.time() - self.start_time) > self.time_limit:
            return self.agent.evaluate(board), depth

        best_values = [(math.inf, depth)]

        # Limit the moves to consider at deeper depths
        if depth <= 2:
            move_limit = 15
        elif depth <= 3:
            move_limit = 10
        else:
            move_limit = 6

        moves = self.agent.get_sorted_moves(board)[:move_limit]

        for move in moves:
            # Time check
            if (time.time() - self.start_time) > self.time_limit and first_try:
                return None, depth
            elif (time.time() - self.start_time) > self.time_limit and not first_try:
                return None, depth
            else:
                first_try = False

            # Recursive call
            util, branch_depth = self.max_value(self.agent.next_move(board, move), alpha, beta, depth)

            if util is None:
                return None, branch_depth

            # Update the new best values
            if best_values:
                if util < sorted(best_values, key=lambda x: (x[0], x[1]))[0][0]:
                    best_values = [(util, branch_depth)]
                elif util == sorted(best_values, key=lambda x: (x[0], x[1]))[0][0]:
                    best_values.append((util, branch_depth))

                # Alpha-beta pruning
                if sorted(best_values, key=lambda x: (x[0], x[1]))[0][0] <= alpha:
                    return sorted(best_values, key=lambda x: (x[0], x[1]))[0]

                beta = min(beta, sorted(best_values, key=lambda x: (x[0], x[1]))[0][0])

        return sorted(best_values, key=lambda x: (x[0], x[1]))[0]

    def max_value(self, board, alpha, beta, depth):
        depth += 1
        first_try = True
        self.nodes_counter += 1

        # Terminal state?
        if self.agent.end_game(board):
            if self.agent.utility(board) == 1:
                return 1000000, depth  # We win
            elif self.agent.utility(board) == -1:
                return -1000000, depth  # We lose
            else:
                return self.agent.evaluate(board), depth  # Draw

        # Depth limit reached?
        if depth == self.depth_limit:
            return self.agent.evaluate(board), depth

        # Time check
        if (time.time() - self.start_time) > self.time_limit:
            return None, depth

        best_values = [(-math.inf, depth)]

        # Limit moves to consider
        if depth <= 2:
            move_limit = 15
        elif depth <= 3:
            move_limit = 10
        else:
            move_limit = 6

        moves = self.agent.get_sorted_moves(board)[:move_limit]

        for move in moves:
            # Time check
            if (time.time() - self.start_time) > self.time_limit and first_try:
                return None, depth
            elif (time.time() - self.start_time) > self.time_limit and not first_try:
                return None, depth
            else:
                first_try = False

            # Recursive call
            util, branch_depth = self.min_value(self.agent.next_move(board, move), alpha, beta, depth)

            if util is None:
                return None, branch_depth

            # change new best values
            if best_values:
                if util > sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0]:
                    best_values = [(util, branch_depth)]
                elif util == sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0]:
                    best_values.append((util, branch_depth))

                # Alpha-beta pruning :)
                if sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0] >= beta:
                    return sorted(best_values, key=lambda x: (-x[0], x[1]))[0]

                alpha = max(alpha, sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0])

        return sorted(best_values, key=lambda x: (-x[0], x[1]))[0]

    def minmax_alpha_beta(self, board):
        depth = 0
        best_values = [(-math.inf, depth, None)]

        # Limit moves
        move_limit = 15

        for move in self.legal_moves[:move_limit]:
            # Time check
            if (time.time() - self.start_time) > self.time_limit:
                return None

            # Recursive search
            value, branch_depth = self.min_value(self.agent.next_move(board, move), self.alpha, self.beta, depth)

            if value is None:
                return None

            # update new best values
            if best_values:
                if value > sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0]:
                    best_values = [(value, branch_depth, move)]
                elif value == sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0]:
                    best_values.append((value, branch_depth, move))

                # Alpha-beta pruning algorithm
                if sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0] >= self.beta:
                    return sorted(best_values, key=lambda x: (-x[0], x[1]))[0][2]

                self.alpha = max(self.alpha, sorted(best_values, key=lambda x: (-x[0], x[1]))[0][0])

        return sorted(best_values, key=lambda x: (-x[0], x[1]))[0][2]