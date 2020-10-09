""" demonstrate color lightening change of Kivy's ColorPicker widget

If you want to use the ColorPicker widget as editor to change a
color that has max(color) < 1.0 will tweak/lighten the color on
opening/initializing of the ColorPicker.

The test color used in this example (0.0, 0.3, 0.6, 0.9) has a hsv
value of (0.5833333333333334, 1.0, 0.6), but the ColorPicker uses
instead a v value of 1.0 (coming from the TextInput). And with the
resulting hsv value (0.5833333333333334, 1.0, 1.0) the color will
be lightened erroneously.

Resulting that you cannot set the color property of the ColorPicker
directly. The same if you first convert the rgb value to hsv and
assign the result to the hsv property of the ColorPicker.

The only workaround I found was to use Clock.schedule_once which
is ugly and can fail on slow devices if the schedule waiting time
is too short (on my old laptop I have to put more than 0.6 seconds,
so the user does see shortly the lightened or initial color before
it gets set correctly).

"""
from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.colorpicker import ColorPicker

kv = """\
#: import rgb_to_hsv colorsys.rgb_to_hsv

BoxLayout:
    color_to_edit: (0.0, 0.3, 0.6, 0.9)
    Label:
        text: "Kivy rocks"
        font_size: sp(90)
        color: root.color_to_edit
        on_color:  print("Label.on_color:       ", self.color)
        on_parent: print("Label.on_parent:      ", self.color)
    #ColorPicker:
    #    color: root.color_to_edit
    #    on_color:  print("ColorPicker.on_color: ", self.color); root.color_to_edit = self.color
    #    on_parent: print("ColorPicker.on_parent:", self.color)
    ColorEditor:
        color: root.color_to_edit
        # NEITHER WORKS IF CONVERTING TO HSV
        # hsv: rgb_to_hsv(*root.color_to_edit[:3])
        on_color:  print("ColorEditor.on_color: ", self.color); root.color_to_edit = self.color
        on_parent: print("ColorEditor.on_parent:", self.color)
"""


class ColorEditor(ColorPicker):
    """ allow to edit colors with max() < 1.0 """
    sent = False

    def on_color(self, *_args):
        """ for debugging and setting breakpoints """
        print("ColorEditor.on_color: ", self.color)

    def on_parent(self, *_args):
        """ try delayed init. """
        print("ColorEditor.on_parent:", self.color, self.parent)
        if self.parent and not self.sent:
            Clock.schedule_once(self._set_color_delayed, 1.5)
            self.sent = True

    def _set_color_delayed(self, *_args):
        print("ColorEditor._set_color_delayed", self.color, self.parent.color_to_edit)
        self.color = (0.0, 0.3, 0.6, 0.9)       # already lightened: self.parent.color_to_edit


class ColorEditorApp(App):
    """ app """
    def build(self):
        """ build """
        return Builder.load_string(kv)


ColorEditorApp().run()
