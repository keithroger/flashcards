import csv
import random
from os import path, remove, listdir
from dataclasses import dataclass


@dataclass
class Card:
    """Stores card information"""
    term: str
    definition: str


class Deck:
    """Stores a list of flashcards."""

    def __init__(self, deckpath):
        """Loads a deck from an existing file"""
        self.deck_path = deckpath
        self.cards = []
        if path.exists(self.deck_path):
            with open(self.deck_path) as csvfile:
                reader = csv.reader(csvfile, delimiter='\t')
                next(reader)
                for row in reader:
                    self.cards.append(Card(row[0], row[1]))
        else:
            with open(self.deck_path, 'x') as file:
                writer = csv.writer(file, delimiter='\t')
                writer.writerow(['Term', 'Definition'])

    def __iter__(self):
        return DeckIterator(self.cards)

    def add_card(self, term, definition):
        """Add a new card to the deck."""
        self.cards.append(Card(term, definition))
        self.save()

    def del_card(self, card):
        """Delete a card from the deck."""
        self.cards.remove(card)
        self.save()

    def save(self):
        """Save the deck as a csv."""
        with open(self.deck_path, 'w') as file:
            writer = csv.writer(file, delimiter='\t')
            writer.writerow(['Front', 'Back'])
            for card in self.cards:
                writer.writerow([card.term, card.definition])

    def shuffle(self):
        random.shuffle(self.cards)
        return self.cards.copy()

    def rename(self):
        pass  # TODO create rename function


class DeckIterator:
    """Iterator used to get cards in a Deck object"""
    def __init__(self, cards):
        self.cards = cards.copy()
        self.cards = sorted(self.cards, key=lambda x: x.term, reverse=True)

    def __next__(self):
        if self.cards:
            return self.cards.pop()
        else:
            raise StopIteration


def decks_list():
    """Returns a sorted list of all the decks that are saved"""
    decks = []
    deck_dir = path.join('flashcards', 'decks')
    for d in listdir(deck_dir):
        deck_path = path.join(deck_dir, d)
        if path.isfile(deck_path):
            decks.append(d[:-4])
    decks.sort()
    return decks


def deck_path(deck_name):
    return path.join('flashcards', 'decks', deck_name + '.csv')


def del_deck(deck_name):
    d_path = deck_path(deck_name)
    if path.isfile(d_path):
        remove(d_path)
