""" relief canvas """
from typing import Any, Callable, Tuple, Union

from kivy.factory import Factory
from kivy.graphics import Color, Line
from kivy.graphics.instructions import InstructionGroup
from kivy.lang import Builder
from kivy.properties import NumericProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.uix.button import Button

from ae.kivy_app import FlowButton, FlowToggler, KivyMainApp
from kivy.uix.widget import Widget


DEF_NUM_PROP_VAL = "99px"


ANGLE_BEG = 87
ANGLE_END = 267


ColorRGB = Tuple[float, float, float]                   #: color with Red, Green and Blue parts between 0.0 and 1.0
ColorRGBA = Tuple[float, float, float, float]           #: ink is rgb color and alpha
ColorOrInk = Union[ColorRGB, ColorRGBA]                 #: color or ink type
ReliefColors = Union[Tuple[ColorRGB, ColorRGB], Tuple]  #: tuple of (top, bottom) relief colors or empty tuple
ReliefBrightness = Tuple[float, float]                  #: top and bottom brightness/darken factor


def relief_colors(color_or_ink: ColorOrInk = (0, 0, 0), darken_factors: ReliefBrightness = (0.6, 0.3)) -> ReliefColors:
    """ calculate the (top and bottom) colors used for the relief lines/drawings.

    :param color_or_ink:        color used for to calculate the relief colors from, which will first be lightened
                                until one of the color parts (R, G or B) reach the value 1.0; then the
                                darken factors will be applied to the color parts. If not passed then grey colors
                                will be returned.

                                .. note::
                                    If the alpha value of paramref:`~relief_colors.color_or_ink` is zero then no relief
                                    colors will be calculated and an empty tuple will be returned (disabling relief).

    :param darken_factors:      two factors for to darken (1) the top and (2) the bottom relief color parts.

    :return:                    tuple with darkened colors calculated from ink or an empty tuple if the alpha
                                value of paramref:`~relief_colors.ink` has a zero value.
    """
    if len(color_or_ink) > 3 and not color_or_ink[3]:
        return ()
    max_col_part = max(color_or_ink[:3])
    if max_col_part == 0:                   # prevent zero division if color_or_ink is black/default
        lightened_color = (1.0, 1.0, 1.0)
    else:
        brighten_factor = 1 / max_col_part
        lightened_color = tuple([(col * brighten_factor) for col in color_or_ink[:3]])
    return tuple([tuple([col_part * darken for col_part in lightened_color]) for darken in darken_factors])


class ReliefCanvas:     # (Widget):     # also works without Widget/any ancestor
    """ relief behavior """

    relief_ellipse_inner_colors: ReliefColors = ObjectProperty(())
    relief_ellipse_inner_lines: NumericProperty = NumericProperty('6sp')
    relief_ellipse_inner_offset: NumericProperty = NumericProperty('1sp')

    relief_ellipse_outer_colors: ReliefColors = ObjectProperty(())
    relief_ellipse_outer_lines: NumericProperty = NumericProperty('6sp')

    relief_square_inner_colors: ReliefColors = ObjectProperty(())
    relief_square_inner_lines: NumericProperty = NumericProperty('3sp')
    relief_square_inner_offset: NumericProperty = NumericProperty('1sp')

    relief_square_outer_colors: ReliefColors = ObjectProperty(())
    relief_square_outer_lines: NumericProperty = NumericProperty('3sp')

    _relief_graphic_instructions: InstructionGroup

    # attributes provided by the class to be mixed into
    x: float
    y: float
    width: float
    height: float
    canvas: Any
    bind: Any

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self._relief_refresh)
        self.bind(size=self._relief_refresh)
        self.bind(relief_ellipse_inner_colors=self._relief_refresh)
        self.bind(relief_ellipse_inner_lines=self._relief_refresh)
        self.bind(relief_ellipse_inner_offset=self._relief_refresh)
        self.bind(relief_ellipse_outer_colors=self._relief_refresh)
        self.bind(relief_ellipse_outer_lines=self._relief_refresh)
        self.bind(relief_square_inner_colors=self._relief_refresh)
        self.bind(relief_square_inner_lines=self._relief_refresh)
        self.bind(relief_square_inner_offset=self._relief_refresh)
        self.bind(relief_square_outer_colors=self._relief_refresh)
        self.bind(relief_square_outer_lines=self._relief_refresh)

        self._relief_graphic_instructions = InstructionGroup()

    def _relief_refresh(self, *_args):
        """ pos/size or color changed event handler. """
        if self._relief_graphic_instructions.length():
            self.canvas.after.remove(self._relief_graphic_instructions)
            self._relief_graphic_instructions.clear()

        add = self._relief_graphic_instructions.add
        pos_size = self.x, self.y, self.width, self.height
        if self.relief_ellipse_inner_colors and self.relief_ellipse_inner_lines:
            self._relief_ellipse_inner_refresh(add, *self.relief_ellipse_inner_colors, *pos_size)
        if self.relief_ellipse_outer_colors and self.relief_ellipse_outer_lines:
            self._relief_ellipse_outer_refresh(add, *self.relief_ellipse_outer_colors, *pos_size)
        if self.relief_square_inner_colors and self.relief_square_inner_lines:
            self._relief_square_inner_refresh(add, *self.relief_square_inner_colors, *pos_size)
        if self.relief_square_outer_colors and self.relief_square_outer_lines:
            self._relief_square_outer_refresh(add, *self.relief_square_outer_colors, *pos_size)

        if self._relief_graphic_instructions.length():
            self.canvas.after.add(self._relief_graphic_instructions)

    def _relief_ellipse_inner_refresh(self, add_instruction: Callable,
                                      top_color: ColorRGB, bottom_color: ColorRGB,
                                      wid_x: float, wid_y: float, wid_width: float, wid_height: float):
        """ ellipse pos/size or color changed event handler. """
        lines = int(self.relief_ellipse_inner_lines)
        offset = int(self.relief_ellipse_inner_offset)
        for line in range(1, lines + 1):
            alpha = 0.9 - (line / lines) * 0.81
            line += offset
            line2 = 2 * line

            in_x1 = wid_x + line
            in_y1 = wid_y + line
            in_width = wid_width - line2
            in_height = wid_height - line2

            add_instruction(Color(*top_color, alpha))                   # inside top left
            add_instruction(Line(ellipse=[in_x1, in_y1, in_width, in_height, ANGLE_END, 360 + ANGLE_BEG]))
            add_instruction(Color(*bottom_color, alpha))                # inside bottom right
            add_instruction(Line(ellipse=[in_x1, in_y1, in_width, in_height, ANGLE_BEG, ANGLE_END]))

    def _relief_ellipse_outer_refresh(self, add_instruction: Callable,
                                      top_color: ColorRGB, bottom_color: ColorRGB,
                                      wid_x: float, wid_y: float, wid_width: float, wid_height: float):
        """ ellipse pos/size or color changed event handler. """
        lines = int(self.relief_ellipse_outer_lines)
        for line in range(1, lines + 1):
            alpha = 0.9 - (line / lines) * 0.81
            line2 = 2 * line

            out_x1 = wid_x - line
            out_y1 = wid_y - line
            out_width = wid_width + line2
            out_height = wid_height + line2

            add_instruction(Color(*top_color, alpha))                   # outside top left
            add_instruction(Line(ellipse=[out_x1, out_y1, out_width, out_height, ANGLE_END, 360 + ANGLE_BEG]))
            add_instruction(Color(*bottom_color, alpha))                # outside bottom right
            add_instruction(Line(ellipse=[out_x1, out_y1, out_width, out_height, ANGLE_BEG, ANGLE_END]))

    def _relief_square_inner_refresh(self, add_instruction: Callable,
                                     top_color: ColorRGB, bottom_color: ColorRGB,
                                     wid_x: float, wid_y: float, wid_width: float, wid_height: float):
        """ square pos/size or color changed event handler. """
        lines = int(self.relief_square_inner_lines)
        offset = int(self.relief_square_inner_offset)
        for line in range(1, lines + 1):
            alpha = 0.9 - (line / lines) * 0.81
            line += offset
            line2 = 2 * line

            in_x1 = wid_x + line
            in_x2 = in_x1 + wid_width - line2
            in_y1 = wid_y + line
            in_y2 = in_y1 + wid_height - line2

            add_instruction(Color(*top_color, alpha))                   # inside top left
            add_instruction(Line(points=[in_x1, in_y1, in_x1, in_y2, in_x2, in_y2]))
            add_instruction(Color(*bottom_color, alpha))                # inside bottom right
            add_instruction(Line(points=[in_x1, in_y1, in_x2, in_y1, in_x2, in_y2]))

    def _relief_square_outer_refresh(self, add_instruction: Callable,
                                     top_color: ColorRGB, bottom_color: ColorRGB,
                                     wid_x: float, wid_y: float, wid_width: float, wid_height: float):
        """ square pos/size or color changed event handler. """
        lines = int(self.relief_square_outer_lines)
        for line in range(1, lines + 1):
            alpha = 0.9 - (line / lines) * 0.81
            line2 = 2 * line

            out_x1 = wid_x - line
            out_x2 = out_x1 + wid_width + line2
            out_y1 = wid_y - line
            out_y2 = out_y1 + wid_height + line2

            add_instruction(Color(*top_color, alpha))                   # outside upper left
            add_instruction(Line(points=[out_x1, out_y1, out_x1, out_y2, out_x2, out_y2]))
            add_instruction(Color(*bottom_color, alpha))                # outside bottom right
            add_instruction(Line(points=[out_x1, out_y1, out_x2, out_y1, out_x2, out_y2]))


class ReliefLabel(ReliefCanvas, Label):
    """ relief label """


class ReliefButton(ReliefCanvas, Button):
    """ relief button """


class ReliefFlowButton(ReliefCanvas, FlowButton):
    """ relief flow button """


class ReliefFlowToggler(ReliefCanvas, FlowToggler):
    """ relief flow toggle button """


if __name__ == '__main__':
    Builder.load_string("""\
#: import relief_colors relief_canvas.relief_colors
#: import ERR relief_canvas.DEF_NUM_PROP_VAL

<ReliefHelpToggler@ReliefCanvas+HelpToggler>:

<Main@FloatLayout>:
    BoxLayout:
        orientation: 'vertical'
        padding: 3
        spacing: 6
        BoxLayout:
            padding: 3
            spacing: 6
            size_hint_y: None
            height: 90
            #HelpToggler:        # needed for to run kivy_app
            ReliefHelpToggler:
                relief_square_outer_colors:
                    relief_colors((1, 1, 0) if app.help_layout else (1, 0, 1), darken_factors=(.81, .51))
                relief_square_outer_lines: app.main_app.correct_num_prop_value(squ_out.text)
                relief_square_inner_lines: app.main_app.correct_num_prop_value(squ_inn.text)
                relief_square_inner_offset: app.main_app.correct_num_prop_value(squ_off.text)
            FlowButton:
                text: "toggle theme"
                on_release: app.main_app.change_app_state('light_theme', not app.app_states['light_theme'])
            BoxLayout:
                orientation: 'vertical'
                size_hint_x: 3
                BoxLayout:
                    ImageLabel:
                        text: "lines"
                    ImageLabel:
                        text: "outer"
                    ImageLabel:
                        text: "inner"
                    ImageLabel:
                        text: "offset"
                BoxLayout:
                    ImageLabel:
                        text: "ellipse"
                    FlowInput:
                        id: ell_out
                        text: "6sp"
                        background_color:
                            (1, 0, 0, .3) if app.main_app.correct_num_prop_value(self.text) == ERR else (1, 1, 1, 1)
                    FlowInput:
                        id: ell_inn
                        text: "3sp"
                        background_color:
                            (1, 0, 0, .3) if app.main_app.correct_num_prop_value(self.text) == ERR else (1, 1, 1, 1)
                    FlowInput:
                        id: ell_off
                        text: "1sp"
                        background_color:
                            (1, 0, 0, .3) if app.main_app.correct_num_prop_value(self.text) == ERR else (1, 1, 1, 1)
                BoxLayout:
                    ImageLabel:
                        text: "square"
                    FlowInput:
                        id: squ_out
                        text: "6sp"
                        background_color:
                            (1, 0, 0, .3) if app.main_app.correct_num_prop_value(self.text) == ERR else (1, 1, 1, 1)
                    FlowInput:
                        id: squ_inn
                        text: "3sp"
                        background_color:
                            (1, 0, 0, .3) if app.main_app.correct_num_prop_value(self.text) == ERR else (1, 1, 1, 1)
                    FlowInput:
                        id: squ_off
                        text: "1sp"
                        background_color:
                            (1, 0, 0, .3) if app.main_app.correct_num_prop_value(self.text) == ERR else (1, 1, 1, 1)
        BoxLayout:
            padding: app.main_app.correct_num_prop_value(ell_out.text)
            spacing: 69
            ReliefFlowButton:
                text: "FlowDarkFac36"
                ellipse_fill_ink: .6, .3, .3, 1
                on_ellipse_fill_ink: print("INK changed", args)
                #relief_ellipse_outer_lines: '9sp'
                #relief_ellipse_inner_lines: '6sp'
                relief_ellipse_inner_colors: relief_colors(self.ellipse_fill_ink, darken_factors=(0.3, 0.6))
                on_relief_ellipse_inner_colors: print("COL changed", args)
                relief_ellipse_inner_lines: app.main_app.correct_num_prop_value(ell_inn.text)
                relief_ellipse_outer_colors: relief_colors(self.ellipse_fill_ink)
                on_relief_ellipse_outer_colors: print("COL changed", args)
                relief_ellipse_outer_lines: app.main_app.correct_num_prop_value(ell_out.text)
                relief_ellipse_inner_offset: app.main_app.correct_num_prop_value(ell_off.text)
                size_hint: 1, 1
                on_release: app.main_app.toggle_color_picker(self, 'ellipse_fill_ink')
            ReliefFlowButton:
                text: "Flow"
                ellipse_fill_ink: .7, .7, .3, 1
                relief_ellipse_inner_colors: relief_colors(self.ellipse_fill_ink)
                relief_ellipse_outer_colors: relief_colors(self.ellipse_fill_ink)
                relief_ellipse_outer_lines: app.main_app.correct_num_prop_value(ell_out.text)
                relief_ellipse_inner_lines: app.main_app.correct_num_prop_value(ell_inn.text)
                relief_ellipse_inner_offset: app.main_app.correct_num_prop_value(ell_off.text)
                size_hint: 1, 1
                on_release: app.main_app.toggle_color_picker(self, 'ellipse_fill_ink')
            ReliefFlowButton:
                text: "0 alpha"
                ellipse_fill_ink: .4, .7, .7, 0     # the 0 alpha is preventing relief
                relief_ellipse_colors: relief_colors(self.ellipse_fill_ink)
                relief_ellipse_outer_lines: app.main_app.correct_num_prop_value(ell_out.text)
                relief_ellipse_inner_lines: app.main_app.correct_num_prop_value(ell_inn.text)
                relief_ellipse_inner_offset: app.main_app.correct_num_prop_value(ell_off.text)
                square_fill_ink: .6, .6, .6, .6
                size_hint: None, 1
                width: self.height
                on_release: app.main_app.toggle_color_picker(self, 'ellipse_fill_ink')
            ReliefFlowToggler:
                text: "Toggler"
                ellipse_fill_ink: .42, .63, .93, 1
                relief_ellipse_inner_colors: relief_colors(self.ellipse_fill_ink, darken_factors=(0.3, 0.6))
                relief_ellipse_inner_lines:
                    app.main_app.correct_num_prop_value(ell_inn.text if self.state == 'down' else '18sp')
                relief_ellipse_outer_colors: relief_colors(self.ellipse_fill_ink)
                relief_ellipse_outer_lines: 
                    app.main_app.correct_num_prop_value(ell_out.text if self.state == 'down' else '12sp')
                relief_ellipse_inner_offset: app.main_app.correct_num_prop_value(ell_off.text)
                size_hint: None, 1
                width: self.height
                on_state: print("Ellipse Toggler state change", args)
        BoxLayout:
            padding: app.main_app.correct_num_prop_value(squ_out.text)
            spacing: 69
            ReliefLabel:
                text: "kivy label"
                color: (0, 0, 0, 1) if app.app_states['light_theme'] else (1, 1, 1, 1)
                relief_square_inner_colors: relief_colors((1, 1, 1), darken_factors=(0.3, 0.6))
                relief_square_outer_colors: relief_colors((1, 1, 1))
                relief_square_outer_lines: app.main_app.correct_num_prop_value(squ_out.text)
                relief_square_inner_lines: app.main_app.correct_num_prop_value(squ_inn.text)
                relief_square_inner_offset: app.main_app.correct_num_prop_value(squ_off.text)
            ReliefButton:
                text: "kivy button"
                color: (0, 0, 0, 1) if app.app_states['light_theme'] else (1, 1, 1, 1)
                relief_square_inner_colors: relief_colors((1, 1, 0), darken_factors=(0.3, 0.6))
                relief_square_outer_colors: relief_colors((0, 0, 1))
                relief_square_outer_lines: app.main_app.correct_num_prop_value(squ_out.text)
                relief_square_inner_lines: app.main_app.correct_num_prop_value(squ_inn.text)
                relief_square_inner_offset: app.main_app.correct_num_prop_value(squ_off.text)
            ReliefFlowButton:
                text: "flow button"
                square_fill_ink: .42, .63, .93, 1
                relief_square_inner_colors: relief_colors(self.square_fill_ink, darken_factors=(0.3, 0.6))
                relief_square_outer_colors: relief_colors(self.square_fill_ink)
                relief_square_outer_lines: app.main_app.correct_num_prop_value(squ_out.text)
                relief_square_inner_lines: app.main_app.correct_num_prop_value(squ_inn.text)
                relief_square_inner_offset: app.main_app.correct_num_prop_value(squ_off.text)
                size_hint: 1, 1
                on_release: app.main_app.toggle_color_picker(self)
            ReliefFlowToggler:
                text: "flow toggler"
                square_fill_ink: .42, .63, .93, 1
                relief_square_inner_colors: relief_colors(self.square_fill_ink, darken_factors=(0.3, 0.6))
                relief_square_outer_colors: relief_colors(self.square_fill_ink)
                relief_square_inner_lines: 
                    app.main_app.correct_num_prop_value(squ_inn.text) if self.state == 'down' else '18sp'
                relief_square_outer_lines: 
                    app.main_app.correct_num_prop_value(squ_out.text) if self.state == 'down' else '9sp'
                relief_square_inner_offset: app.main_app.correct_num_prop_value(squ_off.text)
                size_hint: 1, 1
                on_release: app.main_app.toggle_color_picker(self)

<ColorPickerDD@FlowDropDown>:
    ColorPicker:
        id: col_pic
        size_hint_y: None
        height: self.width
        on_color: print("PIC changed", args)

""")

    Factory.register('ReliefCanvas', ReliefCanvas)


    class NumPropTester(Widget):
        """ test NumericProperty values """
        num_prop = NumericProperty()


    class ReliefCanvasApp(KivyMainApp):
        """ app """
        color_picker: Any = None
        color_dropdown: Any = None

        @staticmethod
        def correct_num_prop_value(num_prop_value: Union[str, int, float]) -> Union[str, int, float]:
            """ test if num_prop_value has a valid/assignable NumericProperty value and if not correct it to 21sp """
            wid = NumPropTester()
            try:
                wid.num_prop = num_prop_value
            except ValueError:
                print(f"ReliefCanvasApp.correct_num_prop_value() got invalid numeric property value '{num_prop_value}'")
                return DEF_NUM_PROP_VAL
            return num_prop_value

        def toggle_color_picker(self, wid, color_name='square_fill_ink'):
            """ show or hide color picker"""
            print("TOGGLE COLOR PICKER", getattr(wid, color_name), self.color_picker)
            if self.color_dropdown:
                self.color_picker.unbind(color=wid.setter(color_name))
                self.color_picker = None
                self.color_dropdown = None
            else:
                self.color_dropdown = Factory.ColorPickerDD()
                self.color_dropdown.open(wid)
                self.color_picker = self.color_dropdown.ids.col_pic
                self.color_picker.color = getattr(wid, color_name)
                self.color_picker.bind(color=wid.setter(color_name))


    ReliefCanvasApp().run_app()
