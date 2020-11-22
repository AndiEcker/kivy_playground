""" auto font size tests (final version implemented within ae.kivy_auto_width namespace portion) """
import resource
from typing import Optional

from ae.gui_app import MAX_FONT_SIZE, MIN_FONT_SIZE
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.widget import Widget

kv_root = '''
<AutoFontSizeTicker>

<AnimLabel@Label+AutoFontSizeTicker>

BoxLayout:
    TextInput:
        id: ti
        text: "displayed in the other (Label) widget with automatic shrunk font size as ticker"
        #text: "grow then run ticker"
        focus: True
    AnimLabel:
        text: ti.text
        font_size: 21.3
        multiline: False
        on_font_size: print("   ...Label font size changed:", self.font_size)
'''


class AutoFontSizeTicker:
    """ mixin """
    # abstracts
    bind: callable
    font_size: float
    text: str
    texture_size: tuple
    width: float
    height: float

    # public attributes
    text_spacing: float = 9.0

    # internal attributes
    _font_size_anim: Optional[Animation] = None
    _font_anim_mode: int = 0
    _last_font_size: float

    _length_anim: Optional[Animation] = None
    _ori_text: str = ""
    _offset_anim: Optional[Animation] = None
    _ticker_text_offset: int = 0
    _ticker_text_length: int = 0
    _ticker_texture_width: float = 0.0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(text=self.text_resize)
        self.bind(width=self.text_resize)
        self.bind(height=self.text_resize)

    def font_size_adjustable(self):
        """ check if font size need/has to be adjustable. """
        if self.texture_size[0] + self.text_spacing < self.width \
                and self.texture_size[1] + self.text_spacing < self.height \
                and self.font_size < min(MAX_FONT_SIZE, self.height):
            return 1
        elif (self.texture_size[0] + self.text_spacing > self.width
              or self.texture_size[1] + self.text_spacing > self.height) \
                and self.font_size > MIN_FONT_SIZE:
            return -1
        return 0

    def text_resize(self, *_args):
        """ called on label text/size changed """
        print(f"text_resize texture_width={self.texture_size[0]}", _args,
              "  mem=", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        # self._last_font_size = 0
        Clock.schedule_once(self._start_font_anim, 0.03)       # needed to update texture_size
        # self._start_font_anim()

    def _start_font_anim(self, *_args):
        """ delayed anim check """
        if not self.texture_size[0] or self._length_anim or self._offset_anim:
            print(f"      SKIP START FONT ANIM  texture_width={self.texture_size[0]}"
                  f"  length_anim={self._length_anim}  ticker_anim={self._offset_anim}")
            return
        self._stop_font_anim()
        print(f"font_anim: font={self.font_size:2.2f}  text={self.texture_size}  wid=({self.width}, {self.height})")
        self._font_anim_mode = self.font_size_adjustable()
        if self._font_anim_mode == 1:
            reach_size = min(MAX_FONT_SIZE, self.height)
            print(f"     GROW   font size to {reach_size}")
        elif self._font_anim_mode == -1:
            reach_size = MIN_FONT_SIZE
            print(f"     SHRINK font size to {MIN_FONT_SIZE}")
        else:
            self._stop_font_anim()
            if self.font_size <= MIN_FONT_SIZE:
                self._start_length_anim()
            else:
                print("     SKIP   font size (stopped)")
            return

        self._font_size_anim = Animation(font_size=reach_size)
        self._font_size_anim.bind(on_progress=self._font_size_progress)
        # self._font_size_anim.bind(on_complete=self._start_length_anim)
        self._font_size_anim.start(self)

    def _stop_font_anim(self):
        if self._font_size_anim:
            self._font_size_anim.stop(self)
            self._font_size_anim = None
        self._font_anim_mode = 0

    def _font_size_progress(self, _anim: Animation, _self: Widget, _progress: float):
        """ animation on_progress event handler. """
        print(f"   ON SIZE PROGRESS: font={self.font_size:2.2f}  texture={self.texture_size}")
        if self._font_anim_mode and self._font_anim_mode != self.font_size_adjustable():
            print(f"     STOPPED {'GROW' if self._font_anim_mode == 1 else 'SHRINK'}")
            self._stop_font_anim()
            if self._last_font_size:
                print(f"     correct font size to {self._last_font_size}")
                self.font_size = self._last_font_size
            self._start_length_anim()
        elif self.font_size <= MIN_FONT_SIZE:
            print(f"     SWITCH TO TICKER ANIM")
            self._stop_font_anim()
            self._start_length_anim()
        self._last_font_size = self.font_size

    def _start_length_anim(self, *_args):
        # self._stop_length_anim()
        print(f"length_anim: len={self._ticker_text_length}  text={self.text}  width={self.texture_size[0]}")

        self._ticker_texture_width = self.width - self.text_spacing
        self._ori_text = self.text
        print(f"     START  text width={len(self.text)} at texture width={self.texture_size[0]}"
              f" -> {self._ticker_texture_width}")

        self._length_anim = Animation(_ticker_text_length=round((len(self.text) + 1) / 2))
        self._length_anim.bind(on_progress=self._ticker_length_progress)
        self._length_anim.start(self)

    def _start_offset_anim(self, *_args):
        print(f"offset_anim: offset={self._ticker_text_offset}  text={self.text}")
        self._offset_anim = Animation(_ticker_text_offset=self._ticker_text_offset * 2, d=9.9)
        self._offset_anim.bind(on_progress=self._ticker_offset_progress)
        self._offset_anim.start(self)

    def _stop_length_anim(self):
        if self._length_anim:
            self.text = self._ori_text

            self._length_anim.stop(self)
            self._length_anim = None

            self._ticker_text_length = 0
            self._ticker_text_offset = 0
            self._ticker_texture_width = 0

        self._ori_text = ""

    def _ticker_length_progress(self, _anim: Animation, _self: Widget, _progress: float):
        print(f"   ON LENGTH PROGRESS: len={self._ticker_text_length}  off={self._ticker_text_offset}  txt={self.text}")
        if self.texture_size[0] + self.text_spacing < self._ticker_texture_width and not self._ticker_text_length:
            print(f"      FOUND  text width={len(self.text)} at texture width={self.texture_size[0]}")
            self._ticker_text_length = len(self.text)
            self._ticker_text_offset = round(self._ticker_max_offset() / 2)
            self._length_anim.stop(self)

            self._start_offset_anim()
        else:
            self.text = self.text[1:-1]
            print(f"     SHRUNK text width={len(self.text)} at texture width={self.texture_size[0]}")

    def _ticker_max_offset(self):
        return round(len(self._ori_text) + 1 - self._ticker_text_length)

    def _ticker_offset_progress(self, _anim: Animation, _self: Widget, _progress: float):
        print(f"   ON OFFSET PROGRESS: len={self._ticker_text_length}  off={self._ticker_text_offset}  txt={self.text}")
        beg = int(self._ticker_text_offset)
        end = beg + self._ticker_text_length
        self.text = self._ori_text[beg:end]
        if _progress >= 1.0:
            print(f"     {'BACKWARDS' if beg else 'FORWARDS'} {_progress}"
                  f"  mem={resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}")
            self._offset_anim.stop(self)
            self._offset_anim = Animation(_ticker_text_offset=0 if beg else self._ticker_max_offset(), d=9.9)
            self._offset_anim.bind(on_progress=self._ticker_offset_progress)
            self._offset_anim.start(self)


Factory.register('AutoFontSizeTicker', cls=AutoFontSizeTicker)


class FontSizeAnimApp(App):
    """ test app """
    def build(self):
        """ build app.root """
        return Builder.load_string(kv_root)


if __name__ == '__main__':
    FontSizeAnimApp().run()
