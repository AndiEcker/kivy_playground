""" references between widgets in kv files

NOTE: using runTouchApp() instead of MyApp().run() doesn't work because then the app variable is not available within kv

"""
from kivy.lang import Builder
from kivy.app import App
from kivy.factory import Factory


Builder.load_string('''
#:import Factory kivy.factory.Factory

<FirstWidget@BoxLayout>:
    Button:
        text: 'click me to add an instance of the second widget'
        on_release: root.add_widget(Factory.SecondWidget())        
            
    TextInput:
        id: txt_inp1
        text: 'text of first widget'

<SecondWidget@TextInput>:
    id: txt_inp2
    text: app.root.ids.txt_inp1.text
''')


class MyApp(App):
    """ class of your application """
    def build(self):
        """ method to build the root widget/layout of your app """
        return Factory.FirstWidget()


MyApp().run()
