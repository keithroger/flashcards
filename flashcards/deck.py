import os
import csv
import random
from os import path, remove
from dataclasses import dataclass


@dataclass
class Card:
    """Stores card information"""
    front: str
    back: str


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
            with open(self.deck_path):
                pass

    def __del__(self):
        """Removes deck csv file"""
        if path.exists(self.deck_path):
            remove(self.deck_path)

    def __iter__(self):
        return DeckIterator(self.cards)

    def add_card(self, front, back):
        """Add a new card to the deck."""
        self.cards.append(Card(front, back))
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
                writer.writerow([card.front, card.back])

    def shuffle(self):
        random.shuffle(self.cards)


class DeckIterator:
    """Iterator used to get cards in a Deck object"""
    def __init__(self, cards):
        self.cards = cards.copy()

    def __next__(self):
        if self.cards:
            return self.cards.pop()
        else:
            raise StopIteration


def decks_list():
    """Returns a sorted list of all the decks that are saved"""
    decks = []
    deck_dir = os.path.join('flashcards', 'decks')
    for d in os.listdir(deck_dir):
        deck_path = os.path.join(deck_dir, d)
        if os.path.isfile(deck_path):
            decks.append(d)
    decks.sort()
    return decks
