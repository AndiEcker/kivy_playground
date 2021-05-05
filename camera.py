from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
import time


kv = '''
CameraClick:
    orientation: 'vertical'
    Camera:
        id: camera
        resolution: (640, 480)
        play: True
    Button:
        text: 'Capture'
        size_hint_y: None
        height: '48dp'
        on_release: root.capture()
'''


class CameraClick(BoxLayout):
    def capture(self):
        camera = self.ids.camera
        time_str = time.strftime("%Y%m%d_%H%M%S")
        camera.export_to_png(f'IMG_{time_str}.png')
        print("Captured")


class TestCamera(App):
    def build(self):
        return Builder.load_string(kv)


TestCamera().run()
