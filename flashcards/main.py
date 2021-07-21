import os
import random
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.popup import Popup
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput

from deck import Deck, Card


class DecksScreen(Screen):
    def new_deck(self):
        content = self._new_deck_dialog()
        self.popup = Popup(title='New Deck',
                           content=content,
                           size_hint_y=None,
                           height=150,
                           size_hint_x=0.6)
        self.popup.open()

    def _new_deck_dialog(self):
        content = BoxLayout(orientation='vertical')
        title_label = Label(text='Enter a Deck Name',
                            size_hint_y=None,
                            height=30)
        error_label = Label(text='',
                            size_hint_y=None,
                            height=30)
        content.add_widget(title_label)
        content.add_widget(error_label)

        box = BoxLayout(orientation='horizontal',
                        size_hint_y=None,
                        height=30)
        text_input = TextInput(multiline=False,
                               # focus=True,
                               on_text_validate=lambda x: self.save_deck(text_input.text))
        save_btn = Button(text='Save',
                          size_hint_x=None,
                          width=70,
                          on_release=lambda x: self.save_deck(text_input.text))
        box.add_widget(text_input)
        box.add_widget(save_btn)

        content.add_widget(box)

        return content

    def save_deck(self, new_filename):
        # TODO check for correct filename characters
        new_path = os.path.join('decks', new_filename + '.csv')
        with open(new_path, 'x') as f:
            # TODO catch error if the file already exists
            f.write('Front\tBack')
        self.ids.deck_rv.data.append({'deck_name': new_filename,
                                      'num_of_cards': '0'})
        self.popup.dismiss()

    def view_deck(self):
        deck_name = self.ids.deck_rv.selected_row
        deck_filename = os.path.join('decks/', deck_name + '.csv')
        self.manager.get_screen('Cards').current_deck = \
            Deck(filename=deck_filename)
        self.manager.current = 'Cards'

    def study(self):
        deck_name = self.ids.deck_rv.selected_row
        deck_filename = os.path.join('decks/', deck_name + '.csv')
        deck = Deck(filename=deck_filename)
        deck.shuffle()
        study_screen = self.manager.get_screen('Study')
        study_screen.current_deck = deck
        study_screen.text = deck.cards[0].front
        study_screen.is_front = True
        study_screen.index = 0
        self.manager.current = 'Study'


class CardsScreen(Screen):
    def __init__(self, **kwargs):
        super(CardsScreen, self).__init__(**kwargs)
        self.current_deck = None
        self.selected_row = None

    def new_card(self):
        content = self._new_card_dialog()
        self.popup = Popup(title='New Card',
                           content=content,
                           size_hint_y=None,
                           height=150,
                           size_hint=(0.6, 0.6))
        self.popup.open()

    def _new_card_dialog(self):
        content = BoxLayout(orientation='vertical')
        front_label = Label(text='Front',
                            size_hint_y=None,
                            height=30)
        front_input = TextInput()
        back_label = Label(text='Back',
                           size_hint_y=None,
                           height=30)
        back_input = TextInput()
        btns = BoxLayout(orientation='horizontal')
        save_btn = Button(text='Save',  # try lamda without the x
                          on_release=lambda x: self.save_card(front_input.text,
                                                              back_input.text))
        cancel_btn = Button(text='Cancel')
        btns.add_widget(save_btn)
        btns.add_widget(cancel_btn)

        content.add_widget(front_label)
        content.add_widget(front_input)
        content.add_widget(back_label)
        content.add_widget(back_input)
        content.add_widget(btns)

        return content

    def save_card(self, front, back):
        self.current_deck.add_card(front, back)
        self.ids.card_rv.data.append({'front': front,
                                      'back': back})
        self.popup.dismiss()

    def on_pre_enter(self):
        super(CardsScreen, self).on_pre_enter()
        self.ids.card_rv.data = self._cards_data()

    def _cards_data(self):
        data = []
        for card in self.current_deck:
            data.append({'front': card.front,
                        'back': card.back})
        return data

    def del_card(self):
        row = self.ids.card_rv.selected_row
        card = Card(row['front'], row['back'])
        self.current_deck.del_card(card)
        self.ids.card_rv.data.remove(row)
        print('row: ', row)
        print('cards: ', self.current_deck.cards)


class StudyScreen(Screen):
    text = StringProperty('')

    def __init__(self, **kwargs):
        super(StudyScreen, self).__init__(**kwargs)
        self.current_deck = None
        self.is_front = None
        self.index = None

    def flip(self):
        if self.is_front:
            self.text = self.current_deck.cards[self.index].back
            self.is_front = False
        else:
            self.text = self.current_deck.cards[self.index].front
            self.is_front = True

    def next(self):
        print('cards: ', len(self.current_deck.cards))
        print('index: ', self.index)
        if self.index < len(self.current_deck.cards) - 1:
            self.index += 1
            self.is_front = True
            self.text = self.current_deck.cards[self.index].front
        else:
            self.text = 'Deck Finished'

    def prev(self):
        if self.index > 0:
            self.index -= 1
            self.is_front = True
            self.text = self.current_deck.cards[self.index].front


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behaviour to the view. '''


class CardRow(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    front = StringProperty('')
    back = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(CardRow, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(CardRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
#             self.parent.parent.selected_row = rv.data[index]
            rv.selected_row = rv.data[index]
            print(rv)
        else:
            print("selection removed for {0}".format(rv.data[index]))


class DeckRow(RecycleDataViewBehavior, BoxLayout):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    deck_name = StringProperty('')
    num_of_cards = StringProperty('')

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(DeckRow, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(DeckRow, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        if is_selected:
            print("selection changed to {0}".format(rv.data[index]))
#             self.parent.parent.selected_row = rv.data[index]['deck_name']
            rv.selected_row = rv.data[index]['deck_name']
        else:
            print("selection removed for {0}".format(rv.data[index]))


class CardRV(RecycleView):

    def __init__(self, **kwargs):
        super(CardRV, self).__init__(**kwargs)
        self.data = []
        self.selected_row = None



class DeckRV(RecycleView):
    def __init__(self, **kwargs):
        super(DeckRV, self).__init__(**kwargs)
        self.data = self._decks_data()
        self.selected_row = None

    @staticmethod
    def _count_cards(filename):
        with open(filename) as f:
            line_count = 0
            for line in f:
                line_count += 1

            return line_count - 1 if line_count > 1 else 0

    def _decks_data(self):
        data = []
        cwd = os.getcwd()
        for d in os.listdir('decks/'):
            deck_path = os.path.join(cwd, 'decks', d)
            if os.path.isfile(deck_path):
                data.append({'deck_name': d[:-4],
                             'num_of_cards': str(self._count_cards(deck_path))})
        # return sorted data
        return sorted(data, key=lambda x: x['deck_name'])


class ScreensApp(App):

    def build(self):
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(DecksScreen(name='Decks'))
        sm.add_widget(CardsScreen(name='Cards'))
        sm.add_widget(StudyScreen(name='Study'))
        return sm


if __name__ == '__main__':
    ScreensApp().run()
