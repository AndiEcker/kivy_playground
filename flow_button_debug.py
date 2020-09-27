""" FlowButton debug app """
from kivy.lang import Builder
from kivy.factory import Factory

from ae.gui_app import id_of_flow
from ae.kivy_app import FlowButton, KivyMainApp


Builder.load_string("""\
<Main@BoxLayout>:
    orientation: 'vertical'
    HelpToggler:        # needed for to run kivy_app
        size_hint: 1, 1
    FlowButton:
        text: "FBOri - Original FlowButton"
        tap_flow_id: id_of_flow('action', 'fb_ori_main')
        tap_kwargs: dict(kwarg1="FBOri tap_kwargs declared in kv Main rule")
        on_tap_kwargs: print("FBOri: tap_kwargs changed in kv Main rule  ", args)
    FBInh:
        text: "Inherited FlowButton (text set in kv Main rule)"
        tap_flow_id: id_of_flow('action', 'fb_inh_main')
        tap_kwargs: dict(kwarg1="FBInh tap_kwargs declared in kv Main rule")
        on_tap_kwargs: print("FBInh: tap_kwargs changed in kv Main rule  ", args)
    FBIn2:
        text: "2 * Inherited FlowButton (text set in kv Main rule)"
        tap_flow_id: id_of_flow('action', 'fb_in2_main')
        tap_kwargs: dict(kwarg1="FBIn2 tap_kwargs declared in kv Main rule")
        on_tap_kwargs: print("FBIn2: tap_kwargs changed in kv Main rule  ", args)

<FBInh>:
    text: "Inherited FlowButton (text set in kv FBInh rule)"
    tap_flow_id: id_of_flow('action', 'fb_inh_rule')
    tap_kwargs: dict(kwarg1='FBInh tap_kwargs declared in kv FBInh rule')
    on_tap_kwargs: print("FBInh.on_tap_kwargs call of kv FBInh rule  ", args)

<FBIn2>:
    text: "2 * Inherited FlowButton (text set in kv FBIn2 rule)"
    tap_flow_id: id_of_flow('action', 'fb_in2_rule')
    tap_kwargs: dict(kwarg1='FBIn2 tap_kwargs declared in kv FBIn2 rule')
    on_tap_kwargs: print("FBIn2.on_tap_kwargs call of kv FBIn2 rule  ", args)
""")


class FBInh(FlowButton):
    """ FlowButton Inherited """
    def __init__(self, **kwargs):
        print("FBInh.__init__ B4 call of super method", kwargs)
        super().__init__(**kwargs)
        print("FBInh.__init__ call of instance method", kwargs)

    def on_tap_kwargs(self, *args):
        """ tap_kwargs changed handler """
        print("FBInh.on_tap_kwargs call of instance method", args)


class FBIn2(FBInh):
    """ FlowButton 2 * Inherited """
    def __init__(self, **kwargs):
        print("FBIn2.__init__ B4 call of super method", kwargs)
        super().__init__(**kwargs)
        print("FBIn2.__init__ call of instance method", kwargs)

    def on_tap_kwargs(self, *args):
        """ tap_kwargs changed handler """
        print("FBIn2.on_tap_kwargs call of instance method", args)


class FlowButtonDebugApp(KivyMainApp):
    """ app """
    def on_fb_ori_main_action(self, flow_id, event_kwargs):
        """ FBOri main tap """
        print("FBOri.on_fb_ori_main_action call", flow_id, event_kwargs)

        print("FBOri_main create new instance")
        wid = FlowButton(text="FBOri - Original FlowButton" + str(len(self.framework_root.children)),
                         tap_flow_id=id_of_flow('action', 'fb_ori_main'),
                         tap_kwargs=dict(kwarg1="FBOri tap_kwargs declared in on_fb_ori_main_action"))
        self.framework_root.add_widget(wid)

    def on_fb_inh_main_action(self, flow_id, event_kwargs):
        """ FBInh main tap """
        print("FBInh.on_fb_inh_main_action call", flow_id, event_kwargs)

        print("FBInh_main create new instance")
        wid = Factory.FBInh(text="FBInh - Inherited FlowButton" + str(len(self.framework_root.children)),
                            tap_flow_id=id_of_flow('action', 'fb_inh_main'),
                            tap_kwargs=dict(kwarg1="FBInh tap_kwargs declared in on_fb_inh_main_action"))
        self.framework_root.add_widget(wid)

    def on_fb_in2_main_action(self, flow_id, event_kwargs):
        """ FBIn2 main tap """
        print("FBIn2.on_fb_in2_main_action call", flow_id, event_kwargs)

        print("FBIn2_main create new instance")
        wid = Factory.FBIn2(text="FBIn2 - 2 * Inherited FlowButton" + str(len(self.framework_root.children)),
                            tap_flow_id=id_of_flow('action', 'fb_in2_main'),
                            tap_kwargs=dict(kwarg1="FBIn2 tap_kwargs declared in on_fb_in2_main_action"))
        self.framework_root.add_widget(wid)

    def on_fb_inh_rule_action(self, flow_id, event_kwargs):
        """ FBInh rule tap """
        print("FBInh.on_fb_inh_rule_action call", flow_id, event_kwargs)

        print("FBInh_rule create new instance")
        wid = Factory.FBInh(text="FBInh - Inherited FlowButton" + str(len(self.framework_root.children)),
                            tap_flow_id=id_of_flow('action', 'fb_inh_rule'),
                            tap_kwargs=dict(kwarg1="FBInh tap_kwargs declared in on_fb_inh_rule_action"))
        self.framework_root.add_widget(wid)

    def on_fb_in2_rule_action(self, flow_id, event_kwargs):
        """ FBIn2 rule tap """
        print("FBIn2.on_fb_in2_rule_action call", flow_id, event_kwargs)

        print("FBIn2_rule create new instance")
        wid = Factory.FBIn2(text="FBIn2 - 2 * Inherited FlowButton" + str(len(self.framework_root.children)),
                            tap_flow_id=id_of_flow('action', 'fb_in2_rule'),
                            tap_kwargs=dict(kwarg1="FBIn2 tap_kwargs declared in on_fb_in2_rule_action"))
        self.framework_root.add_widget(wid)


FlowButtonDebugApp().run_app()
