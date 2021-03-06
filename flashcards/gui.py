from os import rename
from os.path import join
from collections import deque

from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, NoTransition

from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.app import MDApp
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.button import MDFlatButton, MDFloatingActionButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, TwoLineListItem
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import BoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.screen import MDScreen

from flashcards.deck import Deck, decks_list, del_deck, deck_path


class SheetButton(ButtonBehavior, BoxLayout):
    text = StringProperty()
    on_release = ObjectProperty()
    icon = StringProperty()

    def __init__(self, text, on_release, icon):
        super(SheetButton, self).__init__()
        self.text = text
        self.icon = icon
        self.on_release = on_release


class DialogLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(DialogLayout, self).__init__(**kwargs)
#         self.cols = 1
        self.orientation = 'vertical'
        self.size_hint_y = None


class DecksScreen(MDScreen):
    def on_enter(self):
        super().on_enter(self)
        self.refresh()
        self.selection = None

    def item_click(self, deck):
        self.selection = deck
        grid = GridLayout(cols=5)
        grid.adaptive_size = True
        grid.add_widget(SheetButton('Study', self.study, 'cards'))
        grid.add_widget(SheetButton('View', self.view, 'eye'))
        grid.add_widget(SheetButton('Rename', self.rename, 'lead-pencil'))
        grid.add_widget(SheetButton('Stats', self.stats, 'chart-bar'))
        grid.add_widget(SheetButton('Delete', self.delete,
                                    'trash-can-outline'))
        self.bottom_menu = MDCustomBottomSheet(screen=grid)
        self.bottom_menu.open()

    def add(self):
        content = DialogLayout()
        self.field = MDTextField(hint_text='Name')
        content.add_widget(self.field)
        buttons = [MDFlatButton(text='Save',
                                on_release=lambda x: self.save(new=True)),
                   MDFlatButton(text='Cancel',
                                on_release=lambda x: self.dialog.dismiss())]
        self.dialog = MDDialog(title='New Deck',
                               type='custom',
                               content_cls=content,
                               buttons=buttons)
        self.dialog.open()

    def save(self, new):
        if new:
            new_path = join('flashcards', 'decks', self.field.text + '.csv')
            with open(new_path, 'x') as f:
                f.write('Front\tBack')
        else:
            rename(deck_path(self.selection), deck_path(self.field.text))
            self.bottom_menu.dismiss()
        self.refresh()
        self.dialog.dismiss()

    def study(self):
        self.manager.current = 'Study'
        self.manager.get_screen('Study').deck = Deck(deck_path(self.selection))
        self.bottom_menu.dismiss()

    def view(self):
        self.manager.get_screen('View').deck = Deck(deck_path(self.selection))
        self.manager.current = 'View'
        self.bottom_menu.dismiss()

    def rename(self):
        content = DialogLayout()
        self.field = MDTextField(hint_text='Name', text=self.selection)
        content.add_widget(self.field)
        buttons = [MDFlatButton(text='Save',
                                on_release=lambda x: self.save(new=False)),
                   MDFlatButton(text='Cancel',
                                on_release=lambda x: self.dialog.dismiss())]
        self.dialog = MDDialog(title='Rename Deck',
                               type='custom',
                               content_cls=content,
                               buttons=buttons)
        self.dialog.open()

    def stats(self):
        pass

    def delete(self):
        del_deck(self.selection)
        self.bottom_menu.dismiss()
        self.refresh()

    def refresh(self):
        self.ids.md_list.clear_widgets()
        for deck in decks_list():
            self.ids.md_list.add_widget(
                OneLineListItem(
                    text=f'{deck}',
                    on_release=lambda x, y=deck: self.item_click(y),
                    _no_ripple_effect=True))

    def dot_menu(self):
        content = DialogLayout()
        item = BoxLayout(orientation='horizontal')
        item.add_widget(MDLabel(text='Dark Theme'))
        self.switch = MDSwitch()
        self.switch.active = False if\
            MDApp.get_running_app().theme_cls.theme_style == 'Light' else True
        self.switch.on_release = self.theme_switch

        item.add_widget(self.switch)
        content.add_widget(item)

        self.dialog = MDDialog(title='Settings',
                               type='custom',
                               content_cls=content,
                               buttons=[])
        self.dialog.open()

    def theme_switch(self):
        MDApp.get_running_app().theme_cls.theme_style = 'Light' if\
            MDApp.get_running_app().theme_cls.theme_style == 'Dark'\
            else 'Dark'
#         self.switch.active = not self.switch.active


class EditRow(MDCardSwipe):
    """Swipe behavior for list item"""
    text = StringProperty()
    screen = ObjectProperty()


class ViewScreen(MDScreen):
    def __init(self, **kwargs):
        super().__init__(self, **kwargs)
        self.deck = None
        self.card = None

    def on_enter(self):
        super().on_enter(self)
        self.refresh()

    def item_click(self, card):
        self.card = card
        grid = GridLayout(cols=5)
        grid.adaptive_size = True
        grid.add_widget(SheetButton('Edit',
                                    self.edit,
                                    'lead-pencil'))
        grid.add_widget(SheetButton('Stats',
                                    self.stats,
                                    'chart-bar'))
        grid.add_widget(SheetButton('Delete',
                                    self.delete,
                                    'trash-can-outline'))
        self.bottom_menu = MDCustomBottomSheet(screen=grid)
        self.bottom_menu.open()

    def add(self):
        content = DialogLayout()
        self.term_field = MDTextField(hint_text='Term')
        self.def_field = MDTextField(hint_text='Definition', multiline=True)
        content.add_widget(self.term_field)
        content.add_widget(self.def_field)
        buttons = [MDFlatButton(text='Save',
                                on_release=lambda x: self.save(new=True)),
                   MDFlatButton(text='Cancel',
                                on_release=lambda x: self.dialog.dismiss())]
        self.dialog = MDDialog(title='New Card',
                               type='custom',
                               content_cls=content,
                               buttons=buttons)
        self.dialog.open()

    def save(self, new):
        self.deck.add_card(self.term_field.text, self.def_field.text)
        if not new:
            self.deck.del_card(self.card)
        self.refresh()
        self.dialog.dismiss()

    def stats(self):
        pass

    def delete(self):
        self.deck.del_card(self.card)
        self.refresh()
        self.bottom_menu.dismiss()

    def refresh(self):
        self.ids.md_list.clear_widgets()
        for card in self.deck:
            self.ids.md_list.add_widget(
                TwoLineListItem(
                    text=f'{card.term}',
                    secondary_text=f'{card.definition}',
                    on_release=lambda x, y=card: self.item_click(y),
                    _no_ripple_effect=True))

    def edit(self):
        self.bottom_menu.dismiss()
        content = DialogLayout()
        self.term_field = MDTextField(hint_text='Term', text=self.card.term)
        self.def_field = MDTextField(hint_text='Definition',
                                     text=self.card.definition,
                                     multiline=True)
        content.add_widget(self.term_field)
        content.add_widget(self.def_field)
        buttons = [MDFlatButton(text='Save',
                                on_release=lambda x: self.save(new=False)),
                   MDFlatButton(text='Cancel',
                                on_release=lambda x: self.dialog.dismiss())]
        self.dialog = MDDialog(title='Edit Card',
                               type='custom',
                               content_cls=content,
                               buttons=buttons)
        self.dialog.open()

    def back(self):
        self.manager.current = 'Decks'


class StudyScreen(MDScreen, MDLabel):
    text = StringProperty()

    def on_enter(self):
        super().on_enter(self)
        self.cards_left = deque(self.deck.shuffle())
        self.curr_card = self.cards_left.pop()
        self.ids.md_label.text = self.curr_card.term
        self.flipped = False
        self.c_btn = MDFloatingActionButton(icon='check-bold',
                                            pos_hint={'center_x': 0.65,
                                                      'center_y': 0.1},
                                            on_release=lambda x: self.correct())
        self.i_btn = MDFloatingActionButton(icon='close-thick',
                                            pos_hint={'center_x': 0.35,
                                                      'center_y': 0.1},
                                            on_release=lambda x: self.incorrect())
        if self.c_btn.parent:
            self.remove(self.c_btn)
            self.remove(self.i_btn)

    def flip(self):
        if self.flipped:
            self.ids.md_label.text = self.curr_card.term
            self.flipped = False

        else:
            self.ids.md_label.text = self.curr_card.definition
            if not self.c_btn.parent:
                self.add_widget(self.c_btn)
                self.add_widget(self.i_btn)
            self.flipped = True

    def correct(self):
        self.next_card()

    def incorrect(self):
        self.cards_left.appendleft(self.curr_card)
        self.next_card()

    def next_card(self):
        self.remove_widget(self.c_btn)
        self.remove_widget(self.i_btn)
        if self.cards_left:
            self.curr_card = self.cards_left.pop()
            self.ids.md_label.text = self.curr_card.term
            self.flipped = False
        else:
            self.popup()

    def popup(self):
        self.dialog = MDDialog(
            title='Retry?',
            buttons=[
                MDFlatButton(text='No',
                             on_release=lambda x: self.noretry()),
                MDFlatButton(text='Yes',
                             on_release=lambda x: self.retry())])
        self.dialog.open()

    def retry(self):
        self.cards_left = deque(self.deck.shuffle())
        self.curr_card = self.cards_left.pop()
        self.ids.md_label.text = self.curr_card.term
        self.flipped = False
        self.dialog.dismiss()

    def noretry(self):
        self.dialog.dismiss()
        self.back()

    def back(self):
        self.manager.current = 'Decks'


class FlashcardApp(MDApp):

    def build(self):
        self.theme_cls.primary_palette = 'DeepPurple'
        self.theme_cls.theme_style = 'Light'
        sm = ScreenManager(transition=NoTransition())
        sm.add_widget(DecksScreen(name='Decks'))
        sm.add_widget(ViewScreen(name='View'))
        sm.add_widget(StudyScreen(name='Study'))
        return sm


def main():
    Builder.load_file(join('flashcards', 'screens.kv'))
    FlashcardApp().run()


if __name__ == '__main__':
    main()
