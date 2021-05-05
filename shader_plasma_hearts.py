"""
Plasma Shader
=============

This shader example have been taken from https://github.com/kivy/kivy/blob/master/examples/shader/plasma.py
with some adaptation.

This might become a Kivy widget mixin when experimentation will be done.
"""
from functools import partial
from typing import Any, List

from kivy.clock import Clock
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.fbo import Fbo
from kivy.graphics.gl_instructions import ClearBuffers, ClearColor
from kivy.graphics.instructions import Canvas
from kivy.graphics.vertex_instructions import Rectangle
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
# from kivy.uix.slider import Slider
from kivy.graphics import RenderContext
from kivy.properties import ListProperty, ObjectProperty

# from kivy.core.window import Window       # moved to ShaderWidget.__init__ to ensure window render context


# Plasma shader
# taken from kivy examples/shader/plasma.py
# optimized literals into constants via https://stackoverflow.com/questions/20936086

plasma_hearts_shader_code = '''
$HEADER$

uniform float opacity;
uniform float tex_col_mix;
uniform float time;
uniform vec2 resolution;
uniform vec4 user_color;
uniform vec2 user_pos;

const float THOUSAND = 963.9;
const float HUNDRED = 69.3;
//const float TEN = 9.9;
const float TWO = 1.8;
const float ONE = 0.99;

void main(void)
{
  vec4 frag_coord = frag_modelview_mat * gl_FragCoord;
  float x = abs(frag_coord.x - user_pos.x);
  float y = abs(frag_coord.y - user_pos.y - resolution.y);
  
  float m1 = x + y + cos(sin(time) * TWO) * HUNDRED + sin(x / HUNDRED) * THOUSAND;
  float m2 = y / resolution.y;
  float m3 = x / resolution.x + time * TWO;
  
  float c1 = abs(sin(m2 + time) / TWO + m3 / TWO - m2 - m3 + time);
  float c2 = abs(sin(c1 + sin(m1 / THOUSAND + time) + sin(y / HUNDRED + time) + sin((x + y) / HUNDRED) * TWO));
  float c3 = abs(sin(c2 + cos(m2 + m3 + c2) + cos(m3) + sin(x / THOUSAND)));

  vec4 tex = texture2D(texture0, tex_coord0);
  float dis = distance(frag_coord.xy, user_pos) / resolution.x;
  gl_FragColor = mix(tex, vec4(c1, c2, c3, opacity * (1. - dis)) * user_color * TWO, tex_col_mix);
}
'''


class ShadersMixin:
    """ shader mixin base class """
    center_x: list
    opacity: float
    parent: Any
    pos: list
    backgrounds: List[dict]
    size: list
    user_pos: list = ListProperty()

    def update_glsl(self, background_idx, _dt):
        """ timer to animate and sync shader """
        background = self.backgrounds[background_idx]
        # print("UPDATE GLSL", self.__class__, background_idx, dt)
        # print("           BACKGROUND=", background)
        rc = background['render_ctx']
        opacity = background.get('opacity', self.opacity)
        user_pos = background['user_pos']
        user_color = background['user_color']
        root = App.get_running_app().root
        rc['tex_col_mix'] = root.ids.tex_col_mixer.value if root and root.ids else 0.
        rc['time'] = Clock.get_boottime()
        rc['resolution'] = list(map(float, self.size))
        rc['user_color'] = user_color  # (.9, .5, .6, .9)
        rc['user_pos'] = list(map(float, user_pos))
        rc['opacity'] = opacity
        # rc.ask_update()

    def add_background(self, user_pos, user_color=(), opacity=0.69, shader_code=plasma_hearts_shader_code,
                       last_canvas=None):
        """ add another render context """
        if not user_color:
            root = App.get_running_app().root
            if root:
                ids = root.ids
                user_color = (ids.color_red.value, ids.color_green.value, ids.color_blue.value, ids.color_alpha.value)
            else:
                user_color = (.69, .36, .39, .6)
        # noinspection PyUnresolvedReferences
        import kivy.core.window         # not needed directly, import to ensure creation of window render context

        render_ctx = RenderContext(
            opacity=opacity, use_parent_modelview=True, use_parent_projection=True, use_parent_frag_modelview=True)
        with render_ctx:
            rectangle = Rectangle(pos=self.pos, size=self.size)
        self.compile_fragment_shader(render_ctx, shader_code)
        print("ADDING RENDER CONTEXT OK=", render_ctx.shader.success, user_pos, user_color, opacity)

        background_idx = len(self.backgrounds) if hasattr(self, 'backgrounds') else 0
        if background_idx:
            last_canvas = self.backgrounds[-1]['render_ctx']
        else:
            self.backgrounds = list()
            self.user_pos = user_pos = list((self.center_x, 0))
        if last_canvas:
            # rc.add(last_canvas)
            last_canvas.add(render_ctx)
        self.backgrounds.append(dict(render_ctx=render_ctx, rectangle=rectangle,
                                     user_pos=user_pos, user_color=user_color, opacity=opacity))
        Clock.schedule_interval(partial(self.update_glsl, background_idx), 1 / 30.)

    def compile_fragment_shader(self, render_ctx, value):
        """ set the fragment shader to our source code """
        print("COMPILE FRAGMENT SHADER", self.__class__)
        shader = render_ctx.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed to compile fragment shader')

    def on_opacity(self, _instance, value):
        """ alpha changed """
        print("ON_OPACITY", self.__class__, value)
        for bg in self.backgrounds:
            bg['render_ctx'].opacity = value

    def on_pos(self, _instance, value):
        """ pos """
        print("ON_POS", self.__class__, value)
        for bg in self.backgrounds:
            bg['rectangle'].pos = value

    def on_size(self, _instance, value):
        """ size changed """
        print("ON_SIZE", self.__class__, value)
        for bg in self.backgrounds:
            bg['rectangle'].size = value

    def on_user_pos(self, _instance, value):
        """ user repos """
        print("ON_USER_POS", self.__class__, value)
        self.backgrounds[0]['user_pos'] = value


class ShaderMixinA(ShadersMixin):
    """ shader mixin class """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.canvas is None:
            self.canvas = Canvas(opacity=self.opacity)
        self.add_background(self.user_pos, opacity=self.opacity, last_canvas=self.canvas)


class ShaderMixinB(ShadersMixin):
    """ shader mixin class """
    texture: Any = ObjectProperty()          # frame buffer texture

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_background(self.user_pos, opacity=self.opacity)
        self.canvas = self.backgrounds[0]['render_ctx']
        with self.canvas:
            self.fbo = Fbo(opacity=self.opacity, size=self.size)
            self.fbo_color = Color(1, 1, 1, 1)
            self.fbo_rect = Rectangle()
        with self.fbo:
            ClearColor(0, 0, 0, 0)
            ClearBuffers()

    def add_widget(self, widget, index=0, canvas=None):
        """ add widget """
        c = self.canvas
        self.canvas = self.fbo
        # noinspection PyUnresolvedReferences
        super().add_widget(widget, index=index, canvas=canvas)
        self.canvas = c

    def remove_widget(self, widget):
        """ remove widget """
        c = self.canvas
        self.canvas = self.fbo
        # noinspection PyUnresolvedReferences
        super().remove_widget(widget)
        self.canvas = c

    def on_opacity(self, _instance, value):
        """ alpha """
        super().on_opacity(_instance, value)
        self.fbo.opacity = value

    def on_pos(self, _instance, value):
        """ repos """
        super().on_pos(_instance, value)
        self.fbo_rect.pos = value

    def on_size(self, _instance, value):
        """ resize """
        super().on_size(_instance, value)
        self.fbo.size = value
        self.texture = self.fbo.texture
        self.fbo_rect.size = value

    def on_texture(self, _instance, value):
        """ texture changed """
        print("ON TEXTURE", self.__class__, value)
        self.fbo_rect.texture = value


class ShaderBoxA(BoxLayout, ShaderMixinA):
    """ shader box layout widget """
    def on_touch_down(self, touch):
        """ store user touch pos """
        if self.collide_point(*touch.pos):
            print("CHG BOX A USR POS", self.user_pos, "->", touch.pos)
            self.user_pos = touch.pos
        super().on_touch_down(touch)


class ShaderFloatA(FloatLayout, ShaderMixinA):
    """ shader float layout widget """
    def on_touch_down(self, touch):
        """ store user touch pos """
        if self.collide_point(*touch.pos):
            print("CHG FLOAT A USR POS", self.user_pos, "->", touch.pos)
            self.user_pos = touch.pos
        super().on_touch_down(touch)


class ShaderBoxB(BoxLayout, ShaderMixinB):
    """ shader box layout widget """
    def on_touch_down(self, touch):
        """ store user touch pos """
        if self.collide_point(*touch.pos):
            print("CHG BOX B USR POS", self.user_pos, "->", touch.pos)
            self.user_pos = touch.pos
        super().on_touch_down(touch)


class ShaderFloatB(FloatLayout, ShaderMixinB):
    """ shader float layout widget """
    def on_touch_down(self, touch):
        """ store user touch pos """
        if self.collide_point(*touch.pos):
            print("CHG FLOAT B USR POS", self.user_pos, "->", touch.pos)
            self.user_pos = touch.pos
        super().on_touch_down(touch)


Builder.load_string('''\
<Main>
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: .51
        Slider:
            id: color_red
            orientation: 'vertical'
            value: .9
            max: 1.
        Slider:
            id: color_green
            orientation: 'vertical'
            value: .6
            max: 1.
        Slider:
            id: color_blue
            orientation: 'vertical'
            value: .3
            max: 1.
        Slider:
            id: color_alpha
            orientation: 'vertical'
            value: .9
            max: 1.
    Slider:
        id: tex_col_mixer
        orientation: 'vertical'
        size_hint_x: .51
        value: .12
        max: 1.
        on_value: print("TEX COL MIX VALUE", self.value)
    ShaderBoxA:
    ShaderFloatA:
    ShaderBoxB:
    ShaderFloatB:


<ShaderBoxA>
    orientation: 'vertical'
    Label:
        text: "Box A"
        size_hint_y: None
        height: sp(90)
    TextInput:
        size_hint_y: None
        height: sp(90)
    Button:
        size_hint: None, None
        size: 300, 150
        text: "box A button1"
        on_press: print("BOX A BUTTON1 PRESSED", args); root.add_background(self.center)
    Button:
        opacity: .69
        size_hint: None, None
        size: 300, 150
        text: "box A button2"
        on_press: print("BOX A BUTTON2 PRESSED", args)

<ShaderBoxB>
    orientation: 'vertical'
    Label:
        text: "Box B"
        size_hint_y: None
        height: sp(90)
    TextInput:
        size_hint_y: None
        height: sp(90)
    Button:
        size_hint: None, None
        size: 300, 150
        text: "box B button1"
        on_press: print("BOX B BUTTON1 PRESSED", args); root.add_background(self.center)
    Button:
        opacity: .69
        size_hint: None, None
        size: 300, 150
        text: "box B button2"
        on_press: print("BOX B BUTTON2 PRESSED", args)

<ShaderFloatA>
    Label:
        text: "Float A"
        pos: self.parent.x, self.parent.center_y + sp(210)
        size_hint_y: None
        height: sp(90)
    TextInput:
        pos: self.parent.x, self.parent.center_y + sp(120)
        size_hint_y: None
        height: sp(90)
    Button:
        size_hint: None, None
        size: 210, 150
        center: self.parent.center
        text: "float A button1"
        on_press: print("FLOW A BUTTON1 PRESSED", args); root.add_background(self.center)
    Button:
        opacity: .69
        size_hint: None, None
        size: 300, 150
        pos: self.parent.pos
        text: "float A button2"
        on_press: print("FLOW A BUTTON2 PRESSED", args)

<ShaderFloatB>
    Label:
        text: "Float B"
        pos: self.parent.x, self.parent.center_y + sp(210)
        size_hint_y: None
        height: sp(90)
    TextInput:
        pos: self.parent.x, self.parent.center_y + sp(120)
        size_hint_y: None
        height: sp(90)
    Button:
        size_hint: None, None
        size: 210, 150
        center: self.parent.center
        text: "float B button1"
        on_press: print("FLOW B BUTTON1 PRESSED", args); root.add_background(self.center)
    Button:
        opacity: .69
        size_hint: None, None
        size: 300, 150
        pos: self.parent.pos
        text: "float B button2"
        on_press: print("FLOW B BUTTON2 PRESSED", args)

''')


class Main(BoxLayout):
    """ root layout """
    pass


class PlasmaHeartsShaderApp(App):
    """ shader app """
    def build(self):
        """ build """
        return Main()


if __name__ == '__main__':
    PlasmaHeartsShaderApp().run()
