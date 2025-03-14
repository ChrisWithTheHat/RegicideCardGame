from dataclasses import dataclass


@dataclass
class Card:

    suit: str
    name: str

    def __repr__(self):
        return f"{self.name} of {self.suit}"

    def __str__(self):
        return f"{self.name} of {self.suit}"

    @property
    def value(self):
        match self.name:
            case "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" | "10":
                return int(self.name)
            case "Ace":
                return 1
            case "Jack":
                return 10
            case "Queen":
                return 15
            case "King":
                return 20
            case "Jester":
                return 0


class Hand:

    def __init__(self, hand: list[Card]):
        self.hand: list[Card] = hand

    def __repr__(self):
        return str([f"{no}: {value}" for no, value in enumerate(self.hand)])

    def __str__(self):
        return str([f"{no}: {value}" for no, value in enumerate(self.hand)])


@dataclass
class Player:
    name: str
    hand: Hand

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name
