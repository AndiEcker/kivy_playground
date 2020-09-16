""" EffectWidget example from Elliot, kivy-users email from 16-Sep-2020 18:11 """
from kivy.app import App
from kivy.lang import Builder

kv = """\
#: import ew kivy.uix.effectwidget

FloatLayout:
    EffectWidget:
        id: effect_widget
        ToggleButton:
            size_hint: None, None
            size: 200, 200
            pos_hint: {'center_x': .5, 'center_y': .5}
            text: 'Blur Test'
            on_state: 
                self.text = {'normal':'Blur Test', 'down': 'Engaged'} [self.state]
                effect_widget.effects = {'normal':[], 'down': [ew.HorizontalBlurEffect(size=10.0)]} [self.state]
                self.opacity = {'normal': 1, 'down': 0.9} [self.state]
"""


class BlurTestApp(App):
    """ app """
    def build(self):
        """ build """
        return Builder.load_string(kv)


BlurTestApp().run()
