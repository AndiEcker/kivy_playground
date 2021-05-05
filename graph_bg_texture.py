""" demo from https://github.com/nskrypnik/kivy.tips/blob/master/repeat_bg/main.py """
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.scatter import ScatterPlane
from kivy.graphics import Rectangle
from kivy.core.image import Image

Builder.load_string('''
#place kivy notation of app here
''')


class RootWidget(ScatterPlane):
    """ root """
    def __init__(self, **kw):
        super(RootWidget, self).__init__(**kw)
        texture = Image('img/wood.png').texture
        texture.wrap = 'repeat'
        texture.uvsize = (8, 8)
        with self.canvas:
            Rectangle(size=(2048, 2048), texture=texture)


class MainApp(App):
    """ app """
    def build(self):
        """ build root """
        root = RootWidget()
        return root


if __name__ == '__main__':
    MainApp().run()
