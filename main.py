
from kivy.core.window import Window
# Window.borderless = False
import kivy
kivy.require("1.11.1")

from kivymd.app import MDApp
from kivy.core.text import LabelBase
from views.indexui import RootLay
from helpers import BluetoothHelper
from kivy.utils import platform
from settings.settingsjson import bluetooth_settings_json

Window.softinput_mode = 'below_target'
LabelBase.register(name='Arial', fn_regular='res/fonts/ArialUnicodeMS.ttf')

class MainApp(MDApp):
    def build(self):
        self.title = "Bluetooth Input Reader"
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.primary_hue = "400"
        self.icon = '/res/images/poolleaf_16619.png'
        self.use_kivy_settings = False

    def build_config(self, config):
        config.setdefaults('bluetoothsettings', {
            'stringbluedevname': 'MI301CP-4069',
            'optionsbluetuuid': '00001101-0000-1000-8000-00805f9b34fb',
            'optionsbluetencoding': 'LATIN-1'})

    def build_settings(self, settings):
        settings.add_json_panel('Bluetooth Settings',
                                self.config,
                                data=bluetooth_settings_json)
    def on_start(self):
        BluetoothHelper().run()
        if platform == 'android':
            self.root.dev_list = self.root.get_devices()

    def on_pause(self):
        return True

    def on_stop(self):
        self.root.cancel_scale()
        return True

MainApp().run()
