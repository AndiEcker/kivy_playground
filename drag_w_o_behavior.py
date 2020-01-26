""" adapted from github: https://gist.github.com/anonymous/4edff3bdb5319b1c4b401c418a134aa8
"""
from kivy.base import runTouchApp
from kivy.lang import Builder
# from kivy.properties import ObjectProperty, NumericProperty
from kivy.uix.widget import Widget


class MyDraggable(Widget):
    """ drag-able widget """
    orig_parent = None  # ObjectProperty(allownone=True) - ae: kivy property not needed here
    orig_index = None   # NumericProperty(allownone=True)
    hover_index = None  # NumericProperty(allownone=True)

    def on_touch_down(self, touch):
        """ user touch """
        if not self.collide_point(*touch.pos):
            return False

        parent = self.parent
        if parent:
            self.orig_parent = parent
            self.orig_index = parent.children.index(self)
            self.hover_index = None

            parent.remove_widget(self)
            parent.container.add_widget(self)
            parent.placeholder.size = self.size

            self.center = touch.pos
            touch.grab(self)
            return True

    def on_touch_move(self, touch):
        """ user slides """
        if touch.grab_current is not self:
            return False
        self.center = touch.pos
        op = self.orig_parent
        if op.collide_point(*touch.pos):
            for idx, w in enumerate(op.children):
                if w.collide_point(*touch.pos):
                    self._move_placeholder(idx, w)
                    return True
        self._cleanup_placeholder()
        return True

    def _move_placeholder(self, idx, w):
        op = self.orig_parent
        placeholder = op.placeholder
        if w is placeholder:
            return
        if placeholder.parent:
            placeholder.parent.remove_widget(placeholder)
        if w is not None:
            op.add_widget(placeholder, index=idx)
            self.hover_index = idx
        else:
            self._cleanup_placeholder()
            self.hover_index = None

    def _cleanup_placeholder(self):
        op = self.orig_parent
        php = op.placeholder.parent
        if php:
            php.remove_widget(op.placeholder)

    def on_touch_up(self, touch):
        """ user released finger/mouse button """
        if touch.grab_current is not self:
            return False

        touch.ungrab(self)
        op = self.orig_parent
        if self.hover_index is None:
            op.container.remove_widget(self)
            op.add_widget(self, index=self.orig_index)
        else:
            self._cleanup_placeholder()
            self.parent.remove_widget(self)
            op.add_widget(self, index=self.hover_index)

        self.orig_parent = None
        self.orig_index = None
        self.hover_index = None
        return True


runTouchApp(Builder.load_string('''
#:import random random
#:import F kivy.factory.Factory

<Placeholder@Widget>
    size_hint: None, None
    canvas:
        Color:
            rgba: 1, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size

<MyDraggable>:
    size_hint: None, None
    width: 100 + random.randint(0, 150)
    canvas:
        Color:
            rgba: .8, .8, random.random(), 1
        Rectangle:
            pos: self.pos
            size: self.size

BoxLayout:
    orientation: 'vertical'
    ScrollView:
        FloatLayout:
            id: container
            size_hint_y: None
            height: stack.minimum_height
            StackLayout:
                id: stack
                container: container
                placeholder: F.Placeholder()
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:
                MyDraggable:

    Button:
        size_hint_y: None
        text: "Add more draggable's"
        on_press: [ stack.add_widget(F.MyDraggable()) for i in range(15) ]
'''))
