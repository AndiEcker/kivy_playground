""" text cursor demo from Elliot """
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty, NumericProperty

kv = """
BoxLayout:
    orientation: 'vertical'
    Label:
        text: 'Touch a Row Test'
    FindLineInput:
        id: ti
        hint_text: 'Enter text'


    GridLayout:
        cols: 3
        Label:
            text: 'cursor: ' + str(ti.cursor)
        Label:
            text: 'cursor_col: ' + str(ti.cursor_col)
        Label:
            text: 'cursor_row: ' + str(ti.cursor_row)
        Label:
            text: 'cursor_pos: {:.1f}, {:.1f}'.format(*ti.cursor_pos)
        Label:
            text: 'Scroll x,y: {:.1f}, {:.1f}'.format(ti.scroll_x, ti.scroll_y)
        Label:
            text: 'cursor_index: {}'.format(ti.cursor_index(ti.cursor))
"""


class FindLineInput(TextInput):
    """ text input """
    row = NumericProperty()
    row_text = StringProperty()

    def on_touch_down(self, touch):
        """ touch event handler """
        super().on_touch_down(touch)
        if self.collide_point(*touch.pos) and self.disabled is False:
            self.row = self.cursor_row
            self.row_text = self.text.split('\n')[self.row]
            return True

    def on_row(self, *_args):
        """ row changed event handler """
        print(f'click on row: {self.row}')

    def on_row_text(self, *_args):
        """ row_text changed event handler """
        print(f'Row Text: {self.row_text}')


class TITestApp(App):
    """ app class """
    def build(self):
        """ build widget tree """
        return Builder.load_string(kv)


TITestApp().run()
