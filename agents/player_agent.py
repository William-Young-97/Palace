from typing import Protocol, List
from core.game_view import GameView
from core.models import Move


class PlayerAgent(Protocol):
    """
    An agent that chooses a Move for a player, given what they can see
    (GameView) and what they're allowed to do (valid_moves).
    """

    def choose_move(self, view: GameView, valid_moves: List[Move]) -> Move:
        ...
