from typing import List, Optional

from core.game_view import GameView
from core.models import Move
from agents.player_agent import PlayerAgent


class CliHumanAgent(PlayerAgent):
    """
    CLI-based human player. Handles:
    - Rendering the GameView as text
    - Showing all valid moves
    - Asking the user which move they want
    """

    def __init__(self, input_fn=input, output_fn=print):
        self.input_fn = input_fn
        self.output_fn = output_fn

    def choose_move(self, view: GameView, valid_moves: List[Move]) -> Move:
        # 1. Show current state
        self._render_view(view)

        # 2. Show all valid moves
        self._render_moves(view, valid_moves)

        # 3. Ask the user to choose
        while True:
            raw = self.input_fn("Choose move index (or 'p' to pick up if available): ").strip()

            # 'p' shortcut → choose pickup move if present
            if raw.lower() == "p":
                pickup_move = self._find_pickup_move(valid_moves)
                if pickup_move is not None:
                    desc = self._describe_move(view, pickup_move)
                    self.output_fn(f"You choose: {desc}")
                    return pickup_move
                else:
                    self.output_fn("Pickup is not a valid option right now.")
                    continue

            # Otherwise interpret as index into valid_moves
            try:
                idx = int(raw)
                if 0 <= idx < len(valid_moves):
                    move = valid_moves[idx]
                    desc = self._describe_move(view, move)
                    self.output_fn(f"You choose: {desc}")
                    return move
                else:
                    self.output_fn(f"Please enter a number between 0 and {len(valid_moves) - 1}.")
            except ValueError:
                self.output_fn("Invalid input. Enter a number or 'p'.")


    # ---------- helpers ----------

    def _render_view(self, view: GameView) -> None:
        pv = view.player_view
        self.output_fn("")
        self.output_fn(f"--- {pv.name}'s turn ---")
        self.output_fn(f"Deck remaining: {view.deck_remaining}")
        
        self.output_fn(f"Discard pile size: {view.discard_pile_size}")

        self.output_fn(f"Face down: {pv.face_down_count} cards")
        self.output_fn(f"Face up: {[str(c) for c in pv.face_up]}")
        self.output_fn(f"Hand: {[str(c) for c in pv.hand]}")
        self.output_fn("----------------------------")

        if view.discard_top_effective:
            self.output_fn(f"Effective top of pile: {view.discard_top_effective}")
        else:
            self.output_fn("Discard pile is empty.")

    def _render_moves(self, view: GameView, valid_moves: List[Move]) -> None:
        self.output_fn("Valid moves:")

        for i, move in enumerate(valid_moves):
            desc = self._describe_move(view, move)
            self.output_fn(f"{i}: {desc}")

    def _describe_move(self, view: GameView, move: Move) -> str:
        if move.kind == "pickup":
            return "Pick up the entire discard pile"

        # kind == "play"
        src = move.source
        idx = move.index

        # Defensive default
        if src is None or idx is None:
            return "Play (invalid move structure)"

        pv = view.player_view

        if src == "hand":
            # We can show the actual card here
            if 0 <= idx < len(pv.hand):
                card = pv.hand[idx]
                return f"Play {card} from hand (index {idx})"
            else:
                return f"Play card from hand (invalid index {idx})"

        if src == "face_up":
            # We can also show exact face-up card
            if 0 <= idx < len(pv.face_up):
                card = pv.face_up[idx]
                return f"Play {card} from face-up cards (index {idx})"
            else:
                return f"Play card from face-up cards (invalid index {idx})"

        if src == "face_down":
            # Blind play: we *don't* know the card, only the position.
            return f"Play a face-down card at position {idx} (blind)"

        return f"Play card from unknown source '{src}' (index {idx})"

    def _find_pickup_move(self, valid_moves: List[Move]) -> Optional[Move]:
        for move in valid_moves:
            if move.kind == "pickup":
                return move
        return None
