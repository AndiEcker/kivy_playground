""" references between widgets in kv files

NOTE: using runTouchApp() instead of MyApp().run() doesn't work because then the app variable is not available within kv

"""
from kivy.lang import Builder
from kivy.app import App
from kivy.factory import Factory


Builder.load_string('''
#:import Factory kivy.factory.Factory
#:import Clock kivy.clock.Clock

<FirstWidget@BoxLayout>:
    orientation: 'vertical'
    last_added_widget: root
    last_added_size: root.last_added_widget.size
    on_kv_post: print("First on_kv_post", root.last_added_widget.size)
    #on_kv_applied: print("First on_kv_applied", root.last_added_widget.size)
    Button:
        text: 'click me to add an instance of the second widget'
        on_release:
            root.last_added_widget = Factory.SecondWidget()
            root.add_widget(root.last_added_widget)
            #Clock.schedule_once(lambda _dt: setattr(root, 'last_added_size', root.last_added_widget.size))
            #root.last_added_widget.height-10))          
    TextInput:
        id: txt_inp1
        text: 'text of first widget'
    Label:
        #text: str(root.last_added_widget) + " size=" + str(root.last_added_widget.size)
        text: str(root.last_added_widget) + " siz=" + str(root.last_added_size) + " " + str(root.last_added_widget.size)
        #text: str(root.last_added_widget.size) or root.last_added_widget.size 
        on_kv_post: print("Label on_kv_post", root.last_added_widget.size)
        #on_kv_applied: print("Label on_kv_applied", root.last_added_widget.size)

<SecondWidget@TextInput>:
    id: txt_inp2
    text: app.root.ids.txt_inp1.text
    on_kv_post: print("Second on_kv_post", self.parent.last_added_widget.size if self.parent else "===")
    #on_kv_applied: print("Second on_kv_applied", root.last_added_widget.size)
''')


class MyApp(App):
    """ class of your application """
    def build(self):
        """ method to build the root widget/layout of your app """
        return Factory.FirstWidget()


MyApp().run()
