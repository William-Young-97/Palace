from dataclasses import dataclass
from typing import List, Optional
from core.models import Card

@dataclass
class PlayerView:
    name: str
    hand: List[Card]
    face_up: List[Card]
    face_down_count: int   # don’t expose which cards, just how many

@dataclass
class GameView:
    current_player_name: str
    deck_remaining: int
    player_view: PlayerView
    discard_top_effective: Optional[Card]
    discard_pile_size: int
