from dataclasses import dataclass
from random import shuffle
from DataStructures import Card, Hand, Player


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
            card = cards[0]
            damage = card.value * 2 if card.suit == 'Clubs' and current_enemy.suit != 'Clubs' else card.value
            shield = card.value if card.suit == 'Spades' else 0
            effect = card.value if card.suit in ['Diamonds', 'Hearts'] and card.suit != current_enemy.suit else 0
            effect_type = [card.suit] if card.suit in ['Diamonds', 'Hearts'] and card.suit != current_enemy.suit else []

        return damage, shield, effect, effect_type

    @staticmethod
    def can_combo(cards: list[Card]):
        names = [card.name for card in cards]
        values = [card.value for card in cards]
        return len(names) > 1 and len(set(names)) == 1 and sum(values) <= 10

    @staticmethod
    def combo(cards: list[Card], current_enemy: Card):

        damage = 0
        shield = 0
        effect = 0
        effect_type = []

        for card in cards:

            damage += card.value

            if not card.suit == current_enemy.suit:
                effect_type.append(card.suit)

        effect_type = list(set(effect_type))
        if "Spades" in effect_type:
            shield = damage
            effect_type.remove("Spades")
        if "Clubs" in effect_type:
            damage *= 2
        if "Diamonds" in effect_type or "Hearts" in effect_type:
            effect = damage


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

        self.display.display_board_status(self)
        cards, turn_results = self.display.get_user_turn(self)
        self.display.display_turn_result(cards, turn_results)


class TerminalDisplay:

    @staticmethod
    def display_board_status(game: Game):

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

    @staticmethod
    def get_user_turn(game: Game):

        current_player = game.current_player()

        print("---------| PLAY SELECTION |---------")
        correct_input = False
        while not correct_input:

            correct_input = True

            selection = input(f"Which card(s) would you like to play. Use commas to separate multiple cards... ")
            selection = selection.split(",")
            converted_selection = []
            for choice in selection:
                try:
                    converted_choice = int(choice.strip())
                    if not 0 <= converted_choice <= len(current_player.hand.hand) - 1:
                        raise ValueError
                    converted_selection.append(converted_choice)
                except ValueError:
                    print("!!! At least one of the values entered is not a valid selection !!!")
                    correct_input = False
                    break
            if not correct_input:
                continue

            cards = [current_player.hand.hand[i] for i in converted_selection]
            play_result = game.calculate_play(cards, game.current_enemy)

            if not play_result:
                print("!!! You entered an illegal play !!!")
                correct_input = False
                continue

            return cards, play_result

    @staticmethod
    def display_turn_result(cards, turn_results):
        damage, shield, effect, effect_types = turn_results
        action = None
        if len(effect_types) == 0:
            pass
        elif len(effect_types) == 2:
            action = "refreshed and drew"
        elif effect_types[0] == "Diamonds":
            action = "drew"
        elif effect_types[0] == "Hearts":
            action = "refreshed"

        print("---------| TURN INFO |---------")
        print(f"You played: {str.join(", ", [str(card) for card in cards])}")
        print(f"You dealt {damage} damage.")
        if action:
            print(f"You also {action} {damage} cards.")


def generate_castle_deck(randomize: bool = False) -> list[Card]:

    castle_deck = []
    names = ['King', 'Queen', 'Jack']
    suits = ['Diamonds', 'Hearts', 'Clubs', 'Spades']

    for name in names:
        suited_values = []
        for suit in suits:
            suited_values.append(Card(suit, name))

        shuffle(suited_values)
        castle_deck += suited_values

    if randomize:
        shuffle(castle_deck)

    return castle_deck

def generate_tavern_deck(no_of_jokers):

    suits = ['Diamonds', 'Hearts', 'Clubs', 'Spades']
    names = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10']

    tavern_deck = [Card(suit, name) for name in names for suit in suits]
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