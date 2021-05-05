""" example taken from https://github.com/nskrypnik/kivy-graffiti """
import kivy
kivy.require('1.5.2')  # replace with your current kivy version !
from kivy.app import App
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Line
from kivy.lang import Builder
from kivy.properties import ObjectProperty
from kivy.uix.bubble import Bubble
from kivy.uix.button import Button
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget


DEFAULT_BRUSH_WIDTH = 10.0
DEFAULT_BRUSH_COLOR = (1, 1, 0, 1)

APP_CONTEXT = {}


Builder.load_string("""\
<Window>:
    width: 400
    height: 300

<MainFrame>:

    thickness_slider: thickness_slider
    graffiti_canvas: graffiti_canvas
    slider_label: slider_label
    choose_color_btn: choose_color_btn
    toolbar: toolbar
 
    BoxLayout:
        id: main_area
        orientation: "vertical"
        size_hint: 0.85, 1
        pos_hint: {'x': 0.15, 'y': 0}
 
        GraffitiBackground:
            size_hint: 1, 0.9
            canvas:
                Color:
                    rgb: 1, 1, 1
                Rectangle:
                    size: self.size
                    pos: self.pos
                
            Graffiti:
                id: graffiti_canvas
                
        GridLayout:
            id: toolbar
            size_hint: 1, 0.1
            cols: 2
            spacing: '5dp'
            padding: '5dp'
            canvas:
                Color:
                    rgb: 0.5, 0.5, 0.5
                Rectangle:
                    size: self.size
                    pos: self.pos
            ColorPickerButton:
                size_hint: None, 1
                size: '100dp', 0
                id: choose_color_btn
            BoxLayout:
                id: thickness_container
                spacing: 10
                size_hint: 0.4, 1
                Label:
                    id: slider_label
                    text: "Thickness:"
                    size_x: 100
                Slider:
                    id: thickness_slider
                    size_x: 300
                    label: slider_label 
                    min: 0
                    max: 30
    GridLayout:
        id: "sys_buttons"
        rows: 2
        padding: 10
        spacing: 10
        size_hint: 0.15, 1
        pos_hint: {'x': 0, 'y': 0}
        canvas:
            Color:
                rgb: 0.5, 0.5, 0.5
            Rectangle:
                pos: self.pos
                size: self.size
        Button:
            id: new_btn
            size_hint: 1, None
            size: 0, '100dp'
            text: "New"
        Button:
            id: save_btn
            size_hint: 1, None
            size: 0, '100dp'
            text: "Save"
                    
<ColorPickerContainer>:
    orientation: "horizontal"
    size_hint: 0.8, 0.8
    arrow_pos: 'bottom_left'
""")


class ColorPickerContainer(Bubble):
    """ color picker container """
    picker_callback = ObjectProperty()

    def __init__(self, **kw):
        super(ColorPickerContainer, self).__init__(**kw)
        brush = APP_CONTEXT.get('brush')
        self.color_picker = ColorPicker()
        if brush:
            self.color_picker.color = brush.color
        self.color_picker.bind(color=self.picker_callback)
        self.add_widget(self.color_picker)


class ColorPickerButton(Button):
    """ color picker button """
    def change_color(self, color):
        """ change color """
        with self.canvas.after:
            Color(*color)
            d = self.height * 0.8
            pos = (self.x + self.width / 2. - d / 2., self.y + 0.1 * self.height)
            Ellipse(pos=pos, size=(d, d))


class Brush(object):
    """ brush """
    def __init__(self, color=DEFAULT_BRUSH_COLOR, width=DEFAULT_BRUSH_WIDTH):
        self.color = color
        self.width = width

    def change_width(self, slider, value):
        """ change width """
        self.width = value
        slider.label.text = "Thickness: %.2f" % value


class GraffitiBackground(StackLayout):
    """
        This class represents background for graffiti canvas.
        Graffiti widget should lay on this widget
    """
    pass


def avoid_collation(func):
    """ avoid collation """

    def wrapper(self, touch):
        """ wrapper """
        if APP_CONTEXT.get('select_mode', False):
            return
        if self.collide_point(touch.x, touch.y) and not len(touch.grab_list):
            func(self, touch)

    return wrapper


class Graffiti(Widget):
    """
        Main application widget - canvas where user can draw
    """
    def __init__(self, **kw):
        super(Graffiti, self).__init__(**kw)
        self.brush = Brush()
        APP_CONTEXT['brush'] = self.brush

    @avoid_collation
    def on_touch_down(self, touch):
        """ touch down """
        with self.canvas:
            Color(*self.brush.color)
            touch.ud['line'] = Line(points=(touch.x, touch.y), width=self.brush.width)

    @avoid_collation
    def on_touch_move(self, touch):
        """ touch move """
        if touch.ud.get('line'):
            touch.ud['line'].points += (touch.x, touch.y)

    @avoid_collation
    def on_touch_up(self, touch):
        """ touch up """
        with self.canvas:
            Color(*self.brush.color)
            d = self.brush.width * 2
            Ellipse(pos=(touch.x - d / 2., touch.y - d / 2.), size=(d, d))


class MainFrame(FloatLayout):
    """ MainFrame class """

    def __init__(self, **kw):
        super(MainFrame, self).__init__(**kw)
        self.choose_color_btn.bind(on_press=self.show_color_picker)
        self.thickness_slider.value = DEFAULT_BRUSH_WIDTH
        self.slider_label.text = "Thickness: %s" % DEFAULT_BRUSH_WIDTH
        self.thickness_slider.bind(value=self.graffiti_canvas.brush.change_width)
        # trick to draw circle on choose_color_btn
        Clock.schedule_once(lambda dt: self.choose_color_btn.change_color(DEFAULT_BRUSH_COLOR), 0.5)
        self.color_picker_bubble = None

    def picker_callback(self, _inst, color):
        """ picker callback """
        self.graffiti_canvas.brush.color = color
        self.choose_color_btn.change_color(color)

    def show_color_picker(self, _btn):
        """ show color picker """
        if self.color_picker_bubble:
            self.remove_widget(self.color_picker_bubble)
            # del self.color_picker_bubble
            APP_CONTEXT['select_mode'] = False
        else:
            self.color_picker_bubble = ColorPickerContainer(picker_callback=self.picker_callback)
            # set color picker bubble position
            inner_x = self.choose_color_btn.pos[0] + self.choose_color_btn.width / 2
            inner_y = self.choose_color_btn.pos[1] + self.choose_color_btn.height
            bubble_x = inner_x - self.color_picker_bubble.size[0] / 2
            self.color_picker_bubble.pos = [bubble_x, inner_y]
            self.add_widget(self.color_picker_bubble)
            APP_CONTEXT['select_mode'] = True


class GraffitiApp(App):
    """ app """
    def build(self):
        """ load color picker kivy file """
        return MainFrame()


if __name__ == '__main__':
    GraffitiApp().run()
