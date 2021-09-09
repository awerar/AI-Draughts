import time
from cmath import inf
from typing import List

from Piece import Piece
from Position import Position
from Board import Board


class Bot:
    def make_move(self, board: Board) -> List[type(Position)]:
        start_time = time.time()
        best_move = []

        for depth in range(1, 100):
            best_move = self.get_best_move(board, depth)

            print(depth)
            if time.time() >= start_time + 0.2:
                break

        return best_move

    def get_best_move(self, board: Board, depth):
        best_score = -inf
        best_move = []

        for move in self.get_possible_moves(board):
            new_board = board.make_move(move)
            new_score = -self.evaluate_board(new_board, depth - 1, -inf, inf, False)

            if new_score > best_score or best_score == -inf:
                best_move = move
                best_score = new_score

        return best_move

    def evaluate_board(self, board: Board, rec_left, best, worst, my_turn):
        if rec_left <= 0:
            return self.get_board_score(board)

        moves = self.get_possible_moves(board)
        new_boards = [board.make_move(move) for move in moves]
        new_boards = sorted(new_boards, key=lambda b: -self.get_board_score(b))

        best_score = inf if not my_turn else -inf
        for new_board in new_boards:
            new_score = -self.evaluate_board(new_board, rec_left - 1, best, worst, not my_turn)

            if my_turn:
                best = max(best, new_score)
                if new_score >= worst:
                    return new_score

                best_score = max(best_score, new_score)
            else:
                worst = min(worst, new_score)
                if new_score > best:
                    return new_score

                best_score = min(best_score, new_score)

        return best_score

    def get_board_score(self, board: Board):
        if board.white_lost():
            return -inf
        return self.get_white_score(board) - self.get_white_score(board.revert())

    def get_white_score(self, board: Board):
        score = 0.0
        for piece in board.whites:
            if not piece.king:
                score += (piece.position().y / 9.0) * 0.2
            score += 3 if piece.king else 1

        return score

    def get_possible_moves(self, board: Board):
        moves = []

        if not board.capture_possible():
            for piece in board.whites:
                possible_positions = list(self.get_possible_next_positions(piece, board))
                possible_positions = [p[0] for p in possible_positions]
                possible_positions = [pos for pos in possible_positions if
                                      board.on_board(pos) and board.world[pos.y][pos.x] is None]
                new_moves = [[piece.position(), pos] for pos in possible_positions]
                if len(new_moves) > 0:
                    moves.extend(new_moves)
        else:
            for piece in board.whites:
                moves.extend(list(self.get_capture_moves(piece, board)))

        return moves

    # Returns a list of pairs: [pos, capture_pos]
    # Probably not valid though
    def get_possible_next_positions(self, piece: Piece, board: Board, first_move=True, bad_xd=0, bad_yd=0):
        if not piece.king:
            for yd in [-1, 1]:
                if yd == -1 and first_move:
                    continue

                for xd in [-1, 1]:
                    yield [Position(piece.y + 1, piece.x + xd), Position(piece.y + 2, piece.x + xd * 2)]
        else:
            for xd in [-1, 1]:
                for yd in [-1, 1]:
                    if bad_yd == yd and bad_xd == xd:
                        continue

                    for i in range(1, 9):
                        pos = Position(piece.y + i * yd, piece.x + i * xd)
                        capture_pos = []
                        if not board.isEmpty(pos):
                            for j in range(i + 1, 9):
                                cap_pos = Position(piece.y + j * yd, piece.x + j * xd)
                                if not board.on_board(cap_pos) or not board.isEmpty(cap_pos):
                                    break
                                capture_pos.append(cap_pos)

                        if len(capture_pos) > 0:
                            yield [pos, capture_pos]

                        if not board.on_board(pos) or not board.isEmpty(pos):
                            break

    def get_capture_moves(self, piece: Piece, board: Board, first_capture=True):
        if not piece.king:
            for pos_pair in self.get_possible_next_positions(piece, board, first_capture):
                if board.on_board(pos_pair[0]) and board.on_board(pos_pair[1]):
                    if board.isBlack(pos_pair[0]) and board.isEmpty(pos_pair[1]):
                        yield [piece.position(), pos_pair[1]]

                        new_board = board.make_single_move(piece.position(), pos_pair[1], True, first_capture)
                        new_piece = new_board.world[pos_pair[1].y][pos_pair[1].x]
                        additional = self.get_capture_moves(new_piece, new_board, False)

                        for extra in additional:
                            move = [piece.position()]
                            move.extend(extra)

                            yield move

    def valid_location(self, y, x, board):
        return 0 <= x < 10 and 0 <= y < 10 and board.world[y][x] is None
