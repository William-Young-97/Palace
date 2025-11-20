from typing import Dict
from core.game import Game
from core.models import Move
from core.game_view import GameView
from agents.player_agent import PlayerAgent  # Protocol: choose_move(view, valid_moves) -> Move

class GameController:
    def __init__(self, game: Game, agents: Dict[int, PlayerAgent], output_fn=print):
        self.game = game
        self.agents = agents     # dict[player_index] -> PlayerAgent
        self.output_fn = output_fn

    def run(self) -> None:
        self.game.start()

        while not self.game.is_game_over():
            self.play_turn()

        winner = self.game.get_winner()
        if winner:
            self.output_fn(f"\nGame over! {winner.name} wins!")

    def play_turn(self) -> None:
        pid = self.game.get_current_player_index()
        agent = self.agents[pid]

        view = self.game.get_view_for_player(pid)
        valid_moves = self.game.get_valid_moves(pid)

        if not valid_moves:
            self.output_fn(f"\n{view.player_view.name} has no valid moves. Skipping turn.")
            self.game.advance_turn()
            return

        move = agent.choose_move(view, valid_moves)

        self.game.apply_move(pid, move)

        actual_top = self.game.get_actual_top_card()
        if actual_top:
            self.output_fn(f"Top of discard pile is now: {actual_top}")
        else:
            self.output_fn("Discard pile is now empty.")

        # Decide whether to advance to next player
        if not self.game.is_game_over():
            if not self.game.current_player_gets_extra_turn:
                self.game.advance_turn()
            else:
                # Same player goes again – optional debug output:
                self.output_fn(f"{view.player_view.name} gets another turn!")