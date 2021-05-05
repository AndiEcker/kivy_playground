""" TextInput with autocompletion """
from typing import Any, List, Tuple

from ae.gui_app import id_of_flow, replace_flow_action
from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from ae.kivy_app import FlowDropDown
from ae.kivy_app import KivyMainApp

from relief_canvas import ReliefCanvas


class AcTextInput(ReliefCanvas, TextInput):
    """ autocompletion text input """
    auto_complete_texts: List[str]
    auto_complete_selector_index_ink: Tuple[float, float, float, float]

    _ac_dropdown: FlowDropDown = None                   #: singleton DropDown instance for all TextInput instances
    _matching_ac_texts: List[str] = list()              #: one list instance for all TextInput instances is enough
    _matching_ac_index: int = 0                         #: index of selected text in the drop down matching texts list

    def __init__(self, **kwargs):
        self.auto_complete_texts = kwargs.pop('auto_complete_texts', list())
        self.auto_complete_selector_index_ink = kwargs.pop('auto_complete_selector_index_ink', (0.69, 0.69, 0.69, 1))

        super().__init__(**kwargs)

        if not AcTextInput._ac_dropdown:
            AcTextInput._ac_dropdown = FlowDropDown()   # widget instances cannot be created in class var declaration

    def _change_selector_index(self, delta: int):
        """ change/update/set the index of the matching texts in the opened autocompletion dropdown.

        :param delta:           index delta value between old and new index (e.g. pass +1 to increment index).
                                Set index to zero if the old/last index was on the last item in the matching list.
        """
        cnt = len(self._matching_ac_texts)
        chi = list(reversed(self._ac_dropdown.container.children))
        idx = self._matching_ac_index
        chi[idx].square_fill_ink = Window.clearcolor
        self._matching_ac_index = (idx + delta + cnt) % cnt
        chi[self._matching_ac_index].square_fill_ink = self.auto_complete_selector_index_ink
        # suggestion_text will be removed in Kivy 2.1.0 - see PR #7437
        # self.suggestion_text = self._matching_ac_texts[self._matching_ac_index][len(self.text):]

    def keyboard_on_key_down(self, keyboard: Any, keycode: Tuple[int, str], text: str, modifiers: List[str]) -> bool:
        """ overwritten TextInput/FocusBehavior kbd event handler.

        :param keyboard:        keyboard window.
        :param keycode:         pressed key as tuple of (numeric key code, key name string).
        :param text:            pressed key value string.
        :param modifiers:       list of modifier keys (pressed or locked).
        :return:                True if key event get processed/used by this method.
        """
        if self._ac_dropdown.attach_to:
            if keycode[1] in ('enter', 'right'):
                # suggestion_text will be removed in Kivy 2.1.0 - see PR #7437
                # self.suggestion_text will be reset to "" by TextInput instance
                self.text = self._matching_ac_texts[self._matching_ac_index]
                self._ac_dropdown.dismiss()
                return True

            if keycode[1] == 'down':
                self._change_selector_index(1)
            elif keycode[1] == 'up':
                self._change_selector_index(-1)

        return super().keyboard_on_key_down(keyboard, keycode, text, modifiers)

    def on_focus(self, _self, focus: bool):
        """ change flow on text input change of focus.

        :param _self:
        :param focus:           True if this text input got focus, False on unfocus.
        """
        if focus:
            flow_id = self.focus_flow_id or id_of_flow('edit')
        else:
            flow_id = self.unfocus_flow_id or id_of_flow('close')
        App.get_running_app().main_app.change_flow(flow_id)

    def on_text(self, _self, text: str):
        """ TextInput.text change event handler.

        :param _self:           unneeded duplicate reference to TextInput/self.
        :param text:            new/current text property value.
        """
        if text:
            matching = [txt for txt in self.auto_complete_texts if txt[:-1].startswith(text)]
        else:
            matching = list()
        self._matching_ac_texts[:] = matching
        self._matching_ac_index = 0

        if matching:
            cdm = list()
            for idx, txt in enumerate(matching):
                cdm.append(dict(cls='FlowButton', kwargs=dict(text=txt, on_release=self._select_ac_text)))
            self._ac_dropdown.child_data_maps[:] = cdm
            if not self._ac_dropdown.attach_to:
                App.get_running_app().main_app.change_flow(replace_flow_action(self.focus_flow_id, 'suggest'))
                self._ac_dropdown.open(self)
            self._change_selector_index(0)
            # suggestion_text will be removed in Kivy 2.1.0 - see PR #7437
            # self.suggestion_text = matching[self._matching_ac_index][len(self.text):]
        elif self._ac_dropdown.attach_to:
            self._ac_dropdown.dismiss()

    def _select_ac_text(self, selector: Widget):
        """ put selected autocompletion text into text input and close _ac_dropdown """
        self.text = selector.text
        self._ac_dropdown.dismiss()


if __name__ == '__main__':
    Builder.load_string("""\
#: import relief_colors relief_canvas.relief_colors

<AcTextInput>:
    focus_flow_id: ''
    unfocus_flow_id: ''
    font_size: app.app_states['font_size']
    #cursor_color: app.font_color
    #foreground_color: app.font_color
    #background_color: Window.clearcolor
    multiline: False
    use_bubble: True
    use_handles: True
    write_tab: False
    relief_square_outer_colors: relief_colors()
    relief_square_outer_lines: "9sp"

<Main@FloatLayout>:
    AcTextInput:
        focus_flow_id: id_of_flow('edit', 'band')
        auto_complete_texts: ["10cc", "Abba", "BrandX", "Becker Bothers", "BTO", "Miles Davis", "John Sco", "Zappa"]
        hint_text: "enter band name"
        size_hint: 0.9, None
        height: app.main_app.font_size * 2.7
        pos_hint: dict(center_x=0.5, center_y=0.69)
        focus: True
    AcTextInput:
        focus_flow_id: id_of_flow('edit', 'song')
        auto_complete_texts: ["all she wants", "all you want", "all fine", "another road", "aba kad abra"]
        hint_text: "enter song name"
        size_hint: 0.9, None
        height: app.main_app.font_size * 2.7
        pos_hint: dict(center_x=0.5, center_y=0.39)
    HelpToggler:
        size_hint: None, None
        size: sp(30), sp(30)
    FlowButton:
        text: "toggle theme"
        on_release: app.main_app.change_app_state('light_theme', not app.app_states['light_theme'])
""")


    class AcTextInputApp(KivyMainApp):
        """ main app """
        pass


    AcTextInputApp().run_app()
