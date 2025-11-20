class Card:
    def __init__(self, rank, suit, value):
        self.rank = rank
        self.suit = suit
        self.value = value
       
    def __str__(self):
        suit_symbols = {"Spades": "♠", "Hearts": "♥", "Diamonds": "♦", "Clubs": "♣"}
        return f"{self.rank}{suit_symbols[self.suit]}" 