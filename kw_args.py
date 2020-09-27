""" use kwargs for to initialize attribute/property of a sub-class of kivy EventDispatcher/Widget
"""
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.widget import Widget


print("1st CASE - only declare kivy property in kv file/string")

Builder.load_string('''
<KvPropWidget@Widget>:
    kv_prop: None 
''')

try:
    wid = Factory.KvPropWidget(kv_prop='test')
    print("  WOW: kivy now does allow to set attributes via __init__ without declaration as kivy class property")
    print(f"  kv_prop={wid.kv_prop}")
    assert wid.kv_prop == 'test'
except TypeError as ex:
    print(" ERR: widget attribute cannot be set via __init__ (property has to be declared explicitly in python class)")
    print(f"    TypeError EXCEPTION: {ex}")


print("2nd CASE - declare kivy property in python class")


class ClassPropWidget(Widget):
    """ widget class

    declaring a kivy property in widget class explicitly (could also be done after Builder.load_string())
    will implicitly set the value of the property/instance-attribute without the need of a __init__ method.

    """
    kv_prop = StringProperty()


# NOTE: re-declaring the super class (with @Widget) in kv string underneath will break the instance attribute assignment
Builder.load_string('''
<ClassPropWidget>:
    kv_prop: None 
''')

try:
    wid = Factory.ClassPropWidget(kv_prop='test')
    assert wid.kv_prop == 'test'
    print(f"  OK: kv_prop=={wid.kv_prop}")
except TypeError as ex:
    print("  ERR: widget attribute cannot be set via __init__ (property has to be declared explicitly in python class)")
    print(f"    TypeError EXCEPTION: {ex}")


print("3rd CASE - assign StringProperty() to kivy property in kv file/string")

Builder.load_string('''
<StrPropWidget@Widget>:
    kv_prop: StringProperty()
''')

try:
    wid = Factory.StrPropWidget(kv_prop='test')
    print("  WOW: kivy now does allow to set attributes via __init__ without declaration as kivy class property")
    print(f"  kv_prop={wid.kv_prop}")
    assert wid.kv_prop == 'test'
except TypeError as ex:
    print("  ERR: widget attribute cannot be set via __init__ (property has to be declared explicitly in python class)")
    print(f"    TypeError EXCEPTION: {ex}")
