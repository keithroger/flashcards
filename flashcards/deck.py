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

    def __init__(self, filename):
        """Loads a deck from an existing file"""
        self.filename = filename
        self.cards = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, delimiter='\t')
            next(reader)
            for row in reader:
                self.cards.append(Card(row[0], row[1]))

    def __del__(self):
        """Removes deck csv file"""
        if path.exists('decks/' + self.filename):
            remove('decks/' + self.filename)

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
        with open(self.filename, 'w') as file:
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
