""" demonstrate bug/crash in kivy.animation.Animation.have_properties_to_animate().

NOTE: This bug got fixed in kivy master with the PR #5926, merged 7-May-2020.

"""
from kivy.animation import Animation
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView

anim_seq = Animation(x=100) + Animation(x=0) + Animation(x=200) + Animation(x=0)
anim_seq.repeat = True


class MyApp(App):
    """ test app """
    def build(self):
        """ build app.root """
        # NOTE: happening only in conjunction with ScrollView - using only the single Label as app.root does not crash
        # root = Label(text="animated label widget")
        root = ScrollView()
        root.add_widget(Label(text="animated label widget"))
        return root

    def on_start(self):
        """ start app """
        anim_seq.start(self.root)


if __name__ == '__main__':
    MyApp().run()
