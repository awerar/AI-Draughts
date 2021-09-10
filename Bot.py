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

            if time.time() >= start_time + 0.1:
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

        new_boards = []
        for move in moves:
            print(board.__str__())

            for p in move:
                print(p.__str__(), end=" ")
            print()
            new_board = board.make_move(move)
            print(new_board.revert().__str__())
            new_boards.append(new_board)

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

        for piece in board.whites:
            man_func = self.get_moves_man if not board.capture_possible() else self.get_captures_man
            king_func = self.get_moves_king if not board.capture_possible() else self.get_captures_king
            move_func = king_func if piece.king else man_func

            moves.extend(move_func(piece.position(), board))

        return moves

    def get_moves_king(self, pos: Position, board: Board):
        for xd in [-1, 1]:
            for yd in [-1, 1]:
                for i in range(1, 10):
                    new_pos = pos.add(yd * i, xd * i)
                    if board.on_board(new_pos) and board.isEmpty(new_pos):
                        yield [pos, new_pos]
                    else:
                        break

    def get_moves_man(self, pos: Position, board: Board):
        for xd in [-1, 1]:
            new_pos = pos.add(1, xd)
            if board.on_board(new_pos) and board.isEmpty(new_pos):
                yield [pos, new_pos]

    def get_captures_king(self, pos: Position, board: Board):
        for xd in [-1, 1]:
            for yd in [-1, 1]:
                for i in range(1, 10):
                    new_pos = pos.add(yd * i, xd * i)

                    if not board.on_board(new_pos):
                        break

                    if board.isBlack(new_pos):
                        after_kill_pos = new_pos.add(yd, xd)
                        if board.on_board(after_kill_pos) and board.isEmpty(after_kill_pos):
                            yield [pos, after_kill_pos]

                            for k in range(1, 10):
                                slide_pos = after_kill_pos.add(yd * k, xd * k)
                                if not board.on_board(slide_pos) or not board.isEmpty(slide_pos):
                                    break

                                yield [pos, slide_pos]

                            for dd in [-1, 1]:
                                for k in range(1, 10):
                                    dash_pos = after_kill_pos.add(-yd * k * dd, xd * k * dd)

                                    if not board.on_board(dash_pos) or not board.isEmpty(dash_pos):
                                        break

                                    yield [pos, after_kill_pos, dash_pos]

                    if not board.isEmpty(new_pos):
                        break

    def get_captures_man(self, pos: Position, board: Board, first=True):
        for yd in [-1, 1]:
            if yd == -1 and first:
                continue

            for xd in [-1, 1]:
                kill_pos = pos.add(yd, xd)

                if not board.on_board(kill_pos) or not board.isBlack(kill_pos):
                    continue

                after_kill_pos = kill_pos.add(yd, xd)

                if not board.on_board(after_kill_pos) or not board.isEmpty(after_kill_pos):
                    continue

                yield [pos, after_kill_pos]
                new_board = board.make_single_move(pos, after_kill_pos, True, first)
                tails = self.get_captures_man(after_kill_pos, new_board, False)

                for tail in tails:
                    move = [pos]
                    move.extend(tail)

                    yield move