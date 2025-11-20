from typing import List, Optional
from core.models import PlayerState, Card, Deck, Move, MoveKind, SourceKind
from core.game_view import GameView, PlayerView
from core.card_effects import get_card_effect

class Game:
    def __init__(self, num_players: int = 2):
        self.deck = Deck()
        self.players: List[PlayerState] = []
        self.discard_pile: List[Card] = []
        self.current_player_index: int = 0
        self.is_reversed: bool = False
        self.current_player_gets_extra_turn: bool = False
        self._init_players(num_players)

    def _init_players(self, num_players: int) -> None:
        for i in range(num_players):
            self.players.append(PlayerState(name=f"Player {i+1}"))

    def start(self) -> None:
        self.deck.shuffle()
        self._deal_initial_cards()

    def _deal_initial_cards(self) -> None:
        for player in self.players:
            # 3 face-down
            for _ in range(3):
                card = self.deck.draw()
                if card is None:
                    raise RuntimeError("Deck ran out while dealing face-down cards")
                player.face_down_cards.append(card)

            # 3 face-up
            for _ in range(3):
                card = self.deck.draw()
                if card is None:
                    raise RuntimeError("Deck ran out while dealing face-up cards")
                player.face_up_cards.append(card)

            # 3 in hand
            for _ in range(3):
                card = self.deck.draw()
                if card is None:
                    raise RuntimeError("Deck ran out while dealing hand cards")
                player.hand.append(card)

    def get_view_for_player(self, player_index: int) -> GameView:
        player: PlayerState = self.players[player_index]

        # Build the per-player view (what THIS player can see)
        player_view = PlayerView(
            name=player.name,
            hand=list(player.hand),                    # copy so UI can't mutate
            face_up=list(player.face_up_cards),        # visible cards
            face_down_count=len(player.face_down_cards)  # hidden info
        )

        # What’s on top of the discard pile, ignoring 3s
        top_effective = self.get_effective_top_card()  # you already had this logic

        # Build the full GameView
        return GameView(
            current_player_name=self.players[self.current_player_index].name,
            deck_remaining=len(self.deck.cards),
            player_view=player_view,
            discard_top_effective=top_effective,
            discard_pile_size=len(self.discard_pile),
        )

    def _is_card_playable(self, card: Card) -> bool:
        """
        Return True if this card can legally be played on the current pile
        given is_reversed and special-card rules.
        """
        # Special cards are always allowed (2,3,7,10 etc.)
        if get_card_effect(card.rank):
            return True

        # If there is no discard pile yet, any non-special card can start
        if not self.discard_pile:
            return True

        top = self.get_effective_top_card()
        if top is None:
            # All 3s or something weird – treat as no effective top
            return True

        if not self.is_reversed:
            # Normal ascending mode: must be >= top
            return card.value >= top.value
        else:
            # Reversed mode: must be <= top
            return card.value <= top.value

    def get_valid_moves(self, player_index: int) -> list[Move]:
        player = self.players[player_index]
        source_list = player.current_source
        moves: list[Move] = []

        if not source_list:
            return moves  # probably game over; let is_game_over() handle it

        # Determine which source we're currently playing from
        if source_list is player.hand:
            source: SourceKind = "hand"
        elif source_list is player.face_up_cards:
            source = "face_up"
        else:
            source = "face_down"

        # Special case: face-down play is BLIND.
        # Any index is a valid *attempt*; rules checked later in apply_move.
        if source == "face_down":
            for idx in range(len(source_list)):
                moves.append(Move(kind="play", source=source, index=idx))
            # No "pickup" option here – you must try a card.
            return moves

        # Normal case: hand or face_up – only include cards that are actually playable
        for idx, card in enumerate(source_list):
            if self._is_card_playable(card):
                moves.append(Move(kind="play", source=source, index=idx))

        # If no playable cards from this source and there's a pile, pickup is the only option
        if not moves and self.discard_pile:
            moves.append(Move(kind="pickup"))

        return moves


    def apply_move(self, player_index: int, move: Move) -> None:
        player = self.players[player_index]

        # Reset extra-turn flag by default
        self.current_player_gets_extra_turn = False

        if move.kind == "pickup":
            self._apply_pickup(player)
            return

        if move.kind == "play":
            if move.source is None or move.index is None:
                raise ValueError("Play move must have source and index")

            source_list = self._get_source_list(player, move.source)

            if move.index < 0 or move.index >= len(source_list):
                raise ValueError("Card index out of range for source")

            # --- FACE-DOWN SPECIAL CASE ---
            if move.source == "face_down":
                revealed_card = source_list.pop(move.index)

                if self._is_card_playable(revealed_card):
                    self.discard_pile.append(revealed_card)
                    self._refill_hand(player)
                    self._apply_effect_if_any(revealed_card)
                    self._check_four_of_a_kind_burn()

                    # If the revealed card is a 2 and the game is not over,
                    # give this player an extra turn.
                    if revealed_card.rank == "2" and not self.is_game_over():
                        self.current_player_gets_extra_turn = True

                else:
                    # Not playable: card + pile go into hand.
                    player.hand.append(revealed_card)
                    if self.discard_pile:
                        player.hand.extend(self.discard_pile)
                        self.discard_pile.clear()
                        self.is_reversed = False

                return
            # --- END FACE-DOWN SPECIAL CASE ---

            # Normal case: hand or face_up
            card = source_list[move.index]

            if not self._is_card_playable(card):
                raise ValueError("Card is not playable in current state")

            played_card = source_list.pop(move.index)
            self.discard_pile.append(played_card)

            self._refill_hand(player)
            self._apply_effect_if_any(played_card)
            self._check_four_of_a_kind_burn()

            # If this was a 2 and the game isn't over, give extra turn
            if played_card.rank == "2" and not self.is_game_over():
                self.current_player_gets_extra_turn = True
                self.is_reversed = False

            return

        raise ValueError(f"Unknown move kind: {move.kind}")


    def is_game_over(self) -> bool:
        """Return True as soon as any player has no cards at all."""
        return self.get_winner() is not None

    def get_winner(self) -> Optional[PlayerState]:
        """
        Return the first player who has no hand, no face-up, and no face-down cards.
        If no one has won yet, return None.
        """
        for player in self.players:
            if (
                not player.hand
                and not player.face_up_cards
                and not player.face_down_cards
            ):
                return player
        return None

    def _get_source_list(self, player: PlayerState, source: SourceKind) -> list[Card]:
        if source == "hand":
            return player.hand
        if source == "face_up":
            return player.face_up_cards
        if source == "face_down":
            return player.face_down_cards
        raise ValueError(f"Unknown source: {source}")

    def _refill_hand(self, player: PlayerState) -> None:
        """
        Refill the player's hand from the deck up to 3 cards,
        as long as there are cards left in the deck.
        """
        while len(player.hand) < 3 and self.deck.cards:
            card = self.deck.draw()
            if card is None:
                break
            player.hand.append(card)


    def _apply_pickup(self, player: PlayerState) -> None:
        """Pick up the entire discard pile."""
        if not self.discard_pile:
            return
        player.hand.extend(self.discard_pile)
        self.discard_pile.clear()
        self.is_reversed = False  # picking up resets reversed state in your old design

    def _apply_effect_if_any(self, card: Card) -> None:
        """
        Apply any special effect associated with this card rank.
        No printing – just mutate Game state.
        """
        effect = get_card_effect(card.rank)
        if effect:
            effect.apply(self)  # your old code already used effect.apply(game)

    def _check_four_of_a_kind_burn(self) -> None:
        """If last 4 cards on pile share same rank, burn (clear) the pile."""
        if len(self.discard_pile) < 4:
            return
        last_four = self.discard_pile[-4:]
        rank = last_four[0].rank
        if all(c.rank == rank for c in last_four):
            # Burn pile: remove it from play. You can track a burn_pile if you want;
            # for now we just clear it and reset reversed.
            self.discard_pile.clear()
            self.is_reversed = False
    
    def get_effective_top_card(self) -> Optional[Card]:
        """
        Return the top card that actually has a value for comparison.
        Skips 3s, since they inherit the previous card's value.
        """
        for card in reversed(self.discard_pile):
            if card.rank != "3":
                return card
        return None

    def get_current_player_index(self) -> int:
        return self.current_player_index

    def advance_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)


    def get_actual_top_card(self) -> Optional[Card]:
        return self.discard_pile[-1] if self.discard_pile else None
    
    def _clear_discard_pile(self) -> None:
        """
        Clears the discard pile and resets any pile-related state.
        Called by effects like TenEffect to burn the pile out of the game.
        """
        self.discard_pile.clear()
        self.is_reversed = False
