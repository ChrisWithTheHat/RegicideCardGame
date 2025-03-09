from dataclasses import dataclass
from random import shuffle
from typing import Tuple


@dataclass
class Card:
    value: int
    suit: str
    name: str

    def __repr__(self):
        return f"{self.name} of {self.suit}"

    def __str__(self):
        return f"{self.name} of {self.suit}"

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

class Game:

    def __init__(self, castle_deck:list[Card], tavern_deck: list[Card],
                 hand_size: int, player_names: list[str]):

        self.castle_deck: list[Card] = castle_deck
        self.tavern_deck: list[Card] = tavern_deck
        self.discard_pile: list[Card] = []

        self.hand_size: int = hand_size

        self.players_hands: list[Player] = []
        for name in player_names:
            player_hand, self.tavern_deck = Hand(self.tavern_deck[-self.hand_size:]), self.tavern_deck[:-self.hand_size]
            self.players_hands.append(Player(name, player_hand))

        self.number_of_players = len(self.players_hands)
        self.current_player_id = 0

        self.current_enemy: Card = self.castle_deck.pop()
        self.current_damage: int = 0
        self.current_shield: int = 0

        self.display = TerminalDisplay()

        self.is_finished = False
        self.is_won = None

    def current_player(self):
        return self.players_hands[self.current_player_id]

    def enemy_health(self):
        health_lookup = {
            'Jack': 20,
            'Queen': 30,
            'King': 40
        }
        return health_lookup[self.current_enemy.name] - self.current_damage

    def enemy_attack(self):
        attack_lookup = {
            'Jack': 10,
            'Queen': 15,
            'King': 20
        }
        return attack_lookup[self.current_enemy.name]

    def active_shield(self):
        return self.current_shield if self.current_enemy.suit != 'Spades' else 0

    @staticmethod
    def calculate_play(cards: list[Card], current_enemy: Card):

        if Game.can_combo(cards):
            return Game.combo(cards, current_enemy)
        elif Game.can_companion(cards):
            return Game.companion(cards, current_enemy)

        if len(cards) != 1:
            return False
        else:
            cards = cards[0]
            damage = cards.value * 2 if cards.suit == 'Clubs' and current_enemy.suit != 'Clubs' else cards.value
            shield = cards.value if cards.suit == 'Spades' else 0
            effect = cards.value if cards.suit in ['Diamonds', 'Hearts'] and cards.suit != current_enemy.suit else 0
            effect_type = cards.suit if cards.suit in ['Diamonds', 'Hearts'] and cards.suit != current_enemy.suit else []

        return damage, shield, effect, effect_type

    @staticmethod
    def can_combo(cards: list[Card]):
        names = [card.name for card in cards]
        values = [card.value for card in cards]
        return len(set(names)) == 1 and sum(values) <= 10

    @staticmethod
    def combo(cards: list[Card], current_enemy: Card):

        damage = 0
        shield = 0
        effect = 0
        effect_type = []

        for card in cards:

            damage += card.value
            shield += card.value
            effect += card.value

            if card.suit == 'Clubs' and card.suit != current_enemy.suit:
                damage += card.value

            if card.suit in ['Hearts', 'Diamonds'] and card.suit != current_enemy.suit:
                effect_type.append(card.suit)

        return damage, shield, effect, effect_type

    @staticmethod
    def can_companion(cards: list[Card]):
        names = [card.name for card in cards]
        return len(cards) == 2 and "Ace" in names

    @staticmethod
    def companion(cards: list[Card], current_enemy: Card):
        return Game.combo(cards, current_enemy)

    def play_turn(self):

        self.current_player_id = (self.current_player_id + 1) % self.number_of_players

        if not self.current_enemy:
            self.current_enemy = self.castle_deck.pop()

        self.display.display_turn_info(self)


class TerminalDisplay:

    @staticmethod
    def display_turn_info(game: Game):

        current_player = game.current_player()

        print("---------| BOARD INFO |---------")
        print(f"{current_player.name}: It's your turn!")
        print(f"Your hand is {current_player.hand}")
        print("------------------")
        print(f"The current enemy is the {game.current_enemy} and it has {game.enemy_health()} health.")
        print(f"This enemy will deal {game.enemy_attack() - game.active_shield()} damage, after shields.")
        print("------------------")
        print(f"Enemies Remaining: {len(game.castle_deck) + 1}")
        print(f"Cards in Tavern: {len(game.tavern_deck)}")
        print(f"Cards in Discard: {len(game.discard_pile)}")
        print("------------------")


def get_value(name: str):
    match name:
        case "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9"| "10":
            return int(name)
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

def generate_castle_deck(randomize: bool = False) -> list[Card]:

    castle_deck = []
    names = ['King', 'Queen', 'Jack']
    suits = ['Diamonds', 'Hearts', 'Clubs', 'Spades']

    for name in names:
        suited_values = []
        for suit in suits:
            suited_values.append(Card(get_value(name), suit, name))

        shuffle(suited_values)
        castle_deck += suited_values

    if randomize:
        shuffle(castle_deck)

    return castle_deck

def generate_tavern_deck(no_of_jokers):

    suits = ['Diamonds', 'Hearts', 'Clubs', 'Spades']
    names = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    tavern_deck = [Card(get_value(name), suit, name) for name in names for suit in suits]
    tavern_deck += ['Jester']*no_of_jokers
    shuffle(tavern_deck)

    return tavern_deck

def setup(player_names: list[str], random_enemies: bool = False):

    no_of_players = len(player_names)

    hand_size_lookup = {
        1: 8,
        2: 7,
        3: 6,
        4: 5
    }
    #TODO Implement Jesters
    # no_of_jesters_lookup = {
    #     1: 0,
    #     2: 0,
    #     3: 1,
    #     4: 2
    # }
    no_of_jesters_lookup = {
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    if not 1 < no_of_players < 4:
        raise NotImplemented

    hand_size = hand_size_lookup[no_of_players]
    no_of_jesters = no_of_jesters_lookup[no_of_players]

    return Game(generate_castle_deck(random_enemies), generate_tavern_deck(no_of_jesters), hand_size, player_names)


if __name__ == '__main__':
    game = setup(["Chris", "Charlie", "Will"])
    while not game.is_finished:
        game.play_turn()