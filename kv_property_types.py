""" based on Elliot Garbus example - posted in email from 21-Jul-2020 18:53 """
from kivy.app import App
from kivy.lang import Builder

kv = """
<MyBox@BoxLayout>:
    id: box_id
    prop_text: 'Test text'
    prop_number: 1.23
    prop_int: 1
    prop_list: 1, 2, 3, 4
    prop_dict1: {'a': 1}
    prop_dict2: dict(b=2)
    prop_widget: button_id
    prop_parent1: button_id.parent
    Button:
        id: button_id
        text: 'Print types'
        on_release: 
            print(f'type(prop_text):    {type(root.prop_text)}')
            print(f'type(prop_number):  {type(root.prop_number)}')
            print(f'type(prop_int):     {type(root.prop_int)}')
            print(f'type(prop_list):    {type(root.prop_list)}')
            print(f'type(prop_dict1):   {type(root.prop_dict1)}')
            print(f'type(prop_dict2):   {type(root.prop_dict2)}')
            print(f'type(prop_widget):  {type(root.prop_widget)}')
            print(f'type(prop_button):  {type(button_id)}')
            print(f'type(prop_parent1):  {type(root.prop_parent1)}')
            print(f'type(prop_parent2):  {type(button_id.parent)}')

MyBox:

"""


class PropTypeApp(App):
    """ app """
    def build(self):
        """ build """
        return Builder.load_string(kv)


PropTypeApp().run()
