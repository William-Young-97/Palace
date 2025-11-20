from typing import List
import random

from core.game_view import GameView
from core.models import Move
from agents.player_agent import PlayerAgent


class SimpleAIAgent(PlayerAgent):
    """
    Very dumb AI: picks a random valid move.
    You can improve this later (e.g. prefer not picking up, avoid burning good cards, etc.)
    """

    def __init__(self, output_fn=print, name: str = "AI"):
        self.output_fn = output_fn
        self.name = name

    def choose_move(self, view: GameView, valid_moves: List[Move]) -> Move:
        move = random.choice(valid_moves)
        self.output_fn(f"{self.name} chooses: {self._describe(view, move)}")
        return move

    def _describe(self, view: GameView, move: Move) -> str:
        if move.kind == "pickup":
            return "picks up the pile"

        # Otherwise it's a play
        src = move.source
        idx = move.index
        pv = view.player_view

        if src == "hand":
            card = pv.hand[idx]
            return f"plays {card} from hand"

        if src == "face_up":
            card = pv.face_up[idx]
            return f"plays {card} from face-up cards"

        if src == "face_down":
            # Blind play – card will be revealed *after* apply_move
            return f"plays a face-down card at position {idx}"

        return f"plays from {src} index {idx} (unknown source)"
