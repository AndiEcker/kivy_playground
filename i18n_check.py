""" test kivy i18n support

inspired by:
- https://github.com/tito/kivy-gettext-example
- https://github.com/Kovak/kivy_i18n_test
- https://github.com/kivy/kivy/issues/1664
- https://git.bluedynamics.net/phil/woodmaster-trainer/-/blob/master/src/ui/kivy/i18n.py
"""
from typing import Optional

from kivy.base import runTouchApp
from kivy.lang import Builder
# from kivy.event import Observable
from kivy.lang import Observable

from ae.i18n import loaded_languages, default_language, get_f_string


loaded_languages['es_ES'] = dict(trans_text='txt par tra')
loaded_languages['de_DE'] = dict(trans_text='Txt ZUM übe')


# class LangBinderBase(Observable):
class GetTextBinder(Observable):
    """ redirect ae.i18n.get_text to an instance of this class. """
    observers = []
    callee = None

    def fbind(self, name, func, *args, **kwargs):
        """ bind """
        if name == "_":
            self.observers.append((func, args, kwargs))
        else:
            super().fbind(name, func, *args, **kwargs)

    def funbind(self, name, func, *args, **kwargs):
        """ unbind """
        if name == "_":
            key = (func, args, kwargs)
            if key in self.observers:
                self.observers.remove(key)
        else:
            super().funbind(name, func, *args, **kwargs)

    def switch_lang(self, lang):
        """ change language and update kv rules properties """
        default_language(lang)
        for func, args, kwargs in self.observers:
            func(args[0], None, None)

    def __call__(self, text: str, count: Optional[int] = None, language: str = '', **kwargs) -> str:
        """ translate text """
        return self.callee(text, count=count, language=language, **kwargs)


_ = GetTextBinder()
_.callee = get_f_string


runTouchApp(Builder.load_string('''
#: import _ __main__._

BoxLayout:
    size_hint_y: None
    height: 210
    Button:
        text: "ENG + HEIGHT++: " + _('trans_text') + " +" + str(root.height)
        on_release: root.height += 30; _.switch_lang('en_US')
    Button:
        text: "SPA: " + _('trans_text')
        on_release: _.switch_lang('es_ES')
    Button:
        text: "GER: " + _('trans_text')
        on_release: _.switch_lang('de_DE')
'''))
