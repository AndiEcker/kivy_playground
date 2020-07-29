""" example from Elliot Garbus - see kivy-users from 29-Jul-2020 16:45 """
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture


class MyWidget(Widget):
    def __init__(self, **args):
        super(MyWidget, self).__init__(**args)

        texture = Texture.create(size=(2, 1), colorfmt='rgb')

        color1 = 0
        color2 = 255

        buf = ''.join(map(chr, [color1, color2])).encode()

        texture.blit_buffer(buf)

        with self.canvas:
            Rectangle(pos=self.pos, size=self.size, texture=texture)


class TestGApp(App):
    def build(self):
        return MyWidget(size=(200, 200))


if __name__ == '__main__':
    TestGApp().run()
