# contains all the data structures  that we will need in this awesome project
import time
import random

color_set = ['red', 'blue']
number_set = range(1, 11)


def opposite_color(color):
    if color == 'red':
        return 'blue'
    else:
        return 'red'


def bytestoCard(string):
    """ this is the exact reverse function of the __str__ methode for a card"""
    if 'red' in string:
        return Card('red', int(string[3:]))
    else:
        return Card('blue', int(string[4:]))


class Card:
    def __init__(self, color=None, number=None, string=None):
        if string is None:
            self.color = color
            self.number = number
        else:  # parse a string into a card object example Card(string="red1") returns a card object red 1
            if 'red' in string:
                self.color = 'red'
                self.number = int(string[3:])
            else:
                self.color = 'blue'
                self.number = int(string[4:])

        self.image = "Assets/Cards/" + str(self.number)
        self.image += "H" if self.color == "red" else "S"
        self.image += ".png"  # finding the right image file

    def print(self):  # for debug purposes
        print(self.color, self.number)

    def __str__(self):
        return self.color + str(self.number)

    def __eq__(self, other):
        if self.color == other.color and self.number == other.number:
            return True
        return False

    def nextvalidmove(self):  # return a list of next playable cards
        if self.number == 10:
            return [Card(self.color, 9), Card(opposite_color(self.color), 10), Card(opposite_color(self.color), 9)]
        if self.number == 1:
            return [Card(self.color, 2), Card(opposite_color(self.color), 1), Card(opposite_color(self.color), 2)]
        else:
            return [Card(self.color, self.number + 1), Card(self.color, self.number - 1),
                    Card(opposite_color(self.color), self.number), Card(opposite_color(self.color), self.number + 1),
                    Card(opposite_color(self.color), self.number - 1)]

    def toBytes(self):
        return self.__str__().encode()


class Deck:  # mainly for clarity purposes

    def __init__(self, Players=2):
        self.deck = []
        self.reset()
        if Players > 3:  # generate more cards if there are too many players
            self.deck = [item for item in self.deck for repetitions in range(Players)]
            random.shuffle(self.deck)

    def reset(self):  # generate a deck and shuffles it
        for color in color_set:
            for number in number_set:
                self.deck.append(Card(color, number))
        random.shuffle(self.deck)

    def pick(self, number_of_cards=1):  # default value of picked cards is 1
        try:
            picked_cards = self.deck[:number_of_cards]
            self.deck = self.deck[number_of_cards:]
            return picked_cards
        except IndexError():
            # this part is never reached with our implementation because we check before discarding a card
            print("the deck is empty \nIT'S A TIE\nGAME OVER!")

    def show(self):  # debug purposes
        for card in self.deck:
            card.print()

    def top_deck(self):  # the card on the top of the deck as the name suggest
        return self.deck[0]

    def AllLost(self):
        if not self.deck:
            return True
        else:
            return False


class Hand:  # mainly for clarity purposes
    def __init__(self, initial_cards):
        self.hand = initial_cards

    def add_cards(self, cards):  # add a list of cards to the hand
        for card in cards:
            self.hand.append(card)

    def discard_card(self, card):  # when a move is valid we discard the card from the hand
        self.hand.remove(card)

    def playsmartbot(self, topdeck):  # to play with a bot
        time.sleep(random.randint(1, 3))
        validmoves = topdeck.nextvalidmove()
        for card in self.hand:
            if card in validmoves:
                return card
        return self.playbot()

    def playbot(self):  # to play with a bot (less smart)
        time.sleep(random.randint(1, 5))
        return self.hand[random.randint(0, len(self.hand) - 1)]

    def __str__(self):  # prints out the cards
        cards = ""
        for card in self.hand:
            cards += str(card) + " "
        # print(cards)
        return cards

    def DidWin(self):
        """returns true if the hand is empty"""
        if not self.hand:
            return True
        else:
            return False
