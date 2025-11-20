from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import random

from typing import Literal, Optional

MoveKind = Literal["play", "pickup"]
SourceKind = Literal["hand", "face_up", "face_down"]

@dataclass
class Move:
    kind: MoveKind
    source: Optional[SourceKind] = None  # for "play"
    index: Optional[int] = None          # index in that source

@dataclass
class PlayerState:
    name: str
    face_down_cards: List[Card] = field(default_factory=list)
    face_up_cards: List[Card] = field(default_factory=list)
    hand: List[Card] = field(default_factory=list)

    @property
    def current_source(self) -> list[Card] | None:
        if self.hand:
            return self.hand
        if self.face_up_cards:
            return self.face_up_cards
        if self.face_down_cards:
            return self.face_down_cards
        return None

@dataclass
class Card:
    rank: str
    suit: str
    value: int

    def __str__(self) -> str:
        suit_symbols = {"Spades": "♠", "Hearts": "♥", "Diamonds": "♦", "Clubs": "♣"}
        return f"{self.rank}{suit_symbols[self.suit]}"


class Deck:
    def __init__(self) -> None:
        self.cards: List[Card] = self._create()

    def _create(self) -> List[Card]:
        deck: List[Card] = []
        suits = ["Spades", "Clubs", "Hearts", "Diamonds"]
        ranks = ["2", "3", "4", "5", "6", "7",
                 "8", "9", "10", "Jack", "Queen", "King",
                 "Ace"]
        values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

        for suit in suits:
            for rank, value in zip(ranks, values):
                deck.append(Card(rank, suit, value))
        return deck

    def shuffle(self) -> None:
        random.shuffle(self.cards)

    def draw(self) -> Card | None:
        return self.cards.pop() if self.cards else None
    # helper
    def get_card_list(self) -> list[tuple[str, str]]:
        return [(card.rank, card.suit) for card in self.cards]