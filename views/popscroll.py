from kivy.app import App
from kivy.uix.modalview import ModalView
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.animation import Animation
from views.messager import Messager
from kivy.properties import ListProperty, ObjectProperty, ReferenceListProperty

from helpers import BluetoothHelper

class FlashButton(Button):
    fade_bg = ObjectProperty(None)
    bg_color_down = ListProperty([0.0, 0.0, 0.0, 0.0])
    bg_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    def on_touch_down(self, touch):
        self.bg_color_down = App.get_running_app().theme_cls.bg_light
        self.bg_color = self.background_color
        if touch.is_mouse_scrolling:
            return False
        elif not self.collide_point(touch.x, touch.y):
            return False
        elif self in touch.ud:
            return False
        elif self.disabled:
            return False
        else:
            self.fade_bg = Animation(
                duration=0.5, background_color=self.bg_color_down
            )
            self.fade_bg.start(self)
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.fade_bg.stop_property(self, "background_color")
            Animation(
                duration=0.05, background_color=self.bg_color
            ).start(self)
        return super().on_touch_up(touch)
class PopScrollBut(Button):
    fade_bg = ObjectProperty(None)
    bg_color_down = ListProperty([0.0, 0.0, 0.0, 0.0])
    bg_color = ListProperty([0.0, 0.0, 0.0, 0.0])
    def on_touch_down(self, touch):
        self.bg_color_down = App.get_running_app().theme_cls.bg_light
        self.bg_color = self.background_color
        if touch.is_mouse_scrolling:
            return False
        elif not self.collide_point(touch.x, touch.y):
            return False
        elif self in touch.ud:
            return False
        elif self.disabled:
            return False
        else:
            self.fade_bg = Animation(
                duration=0.5, background_color=self.bg_color_down
            )
            self.fade_bg.start(self)
            return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if touch.grab_current is self:
            self.fade_bg.stop_property(self, "background_color")
            Animation(
                duration=0.05, background_color=self.bg_color
            ).start(self)
        return super().on_touch_up(touch)
class PopScroll(ModalView):
    toast = Messager()
    def get_pop_scroll(self, txt):
        this = App.get_running_app()
        this.root.ids.dev_button.text = txt
        this.root.pop.dismiss()

    def open_pop_scroll_modal(self):
        this = App.get_running_app()
        got = this.root.pop.populate_pop_scroll()  # populate the pop modal
        if got:
            this.root.pop.open()
        else:
            self.toast.messager("No devices available!")

    def populate_pop_scroll(self):
        this = App.get_running_app()
        if this.root.pop is None:
            this.root.pop = PopScroll()
        menu_items = None
        if len(this.root.dev_list) > 0:
            menu_items = [{"text": f"{i}"} for i in this.root.dev_list]
        if menu_items is not None and menu_items is not False:
            self.ids.view_popscroll.data = menu_items
            return True
        else:
            return False

class PopDialog(ModalView):
    def open_popup_dialog(self, txt, info=''):
        # info indicates text colour
        this = App.get_running_app()
        if this.root.dialog is None:
            this.root.dialog = PopDialog()
        if info == 'info':
            this.root.dialog.ids.dialog_messager.color = (0.11, 0.313, 0.60, 1)
        elif info == 'success':
            this.root.dialog.ids.dialog_messager.color = (0.278, 0.443, 0.286, 1)
        elif info == 'warn':
            this.root.dialog.ids.dialog_messager.color = (0.88, 0.0, 0.11, 1)
        else:
            this.root.dialog.ids.dialog_messager.color = (0.1333, 0.1333, 0.1333, 1)
        this.root.dialog.ids.dialog_messager.text = txt
        this.root.dialog.open()

class PopSnackbar(ModalView):
    def open_popup_dialog(self, txt, info=''):
        # info indicates text colour
        this = App.get_running_app()
        if this.root.snackbar is None:
            this.root.snackbar = PopSnackbar()
        if info == 'info':
            this.root.snackbar.ids.snackbar_messager.color = (0.11, 0.313, 0.60, 1)
        elif info == 'success':
            this.root.snackbar.ids.snackbar_messager.color = (0.278, 0.443, 0.286, 1)
        elif info == 'warn':
            this.root.snackbar.ids.snackbar_messager.color = (0.88, 0.0, 0.11, 1)
        else:
            this.root.snackbar.ids.snackbar_messager.color = (0.1333, 0.1333, 0.1333, 1)
        this.root.snackbar.ids.snackbar_messager.text = txt
        this.root.snackbar.open()

    def close_popup_dialog(self):
        self.ids.snackbar_messager.text = ''
        self.dismiss()

class PopDialogWithAction(ModalView):
    Action_Button = ObjectProperty(None)
    Blue = BluetoothHelper()
    def open_popup_dialog(self, txt, action='', info=''):
        # info indicates text colour
        this = App.get_running_app()
        if this.root.dialog_with_action is None:
            this.root.dialog_with_action = PopDialogWithAction()
        if info == 'info':
            this.root.dialog_with_action.ids.dialog_action_messager.color = (0.11, 0.313, 0.60, 1)
        elif info == 'success':
            this.root.dialog_with_action.ids.dialog_action_messager.color = (0.278, 0.443, 0.286, 1)
        elif info == 'warn':
            this.root.dialog_with_action.ids.dialog_action_messager.color = (0.88, 0.0, 0.11, 1)
        else:
            this.root.dialog_with_action.ids.dialog_action_messager.color = (0.1333, 0.1333, 0.1333, 1)
        this.root.dialog_with_action.ids.dialog_action_messager.text = txt

        if action == 'bluetooth':
            self.Action_Button = FlashButton(
                text='Enable Bluetooth',
                pos_hint={'top': 0.32, 'x': 0.65},
                size_hint=[0.3, 0.18],
                color=(0, 0.72, 0.95, 1),
                background_down='',
                on_release=self.Blue.enable_bluetooth
            )
            this.root.dialog_with_action.ids.action_layout.add_widget(self.Action_Button)
            this.root.dialog_with_action.ids.dialog_action_hidden.text = 'blue'
            # this.root.dialog_with_action.ids.dialog_action.text = 'Enable Bluetooth'
            # this.root.dialog_with_action.ids.dialog_action.bind(on_release=BluetoothHelper().enable_bluetooth)
        else:
            # self.Action_Button = FlashButton(
            #     text='Dismiss',
            #     pos_hint={'top': 0.22},
            #     size_hint_y=0.18,
            #     color=(0, 0.72, 0.95, 1),
            #     background_down='',
            #     on_release=self.close_popup_dialog
            # )
            # this.root.dialog_with_action.ids.dialog_action.text = 'Dismiss'
            # this.root.dialog_with_action.ids.dialog_action.bind(on_release=self.close_popup_dialog)
            pass
        this.root.dialog_with_action.open()

    def close_popup_dialog(self, *args):
        if self.ids.dialog_action_hidden.text == 'blue':
            self.ids.action_layout.remove_widget(self.Action_Button)
        self.ids.dialog_action_hidden.text = ''
        self.dismiss()

    def remove_action_button(self):
        self.ids.dialog_action_hidden.text = ''
        this = App.get_running_app()
        this.root.dialog_with_action.ids.action_layout.remove_widget(self.Action_Button)
        this.root.dialog_with_action.dismiss()