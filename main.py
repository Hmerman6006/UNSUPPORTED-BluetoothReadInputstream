
from kivy.core.window import Window
# Window.borderless = False
import kivy
kivy.require("1.11.1")

from kivymd.app import MDApp
from kivy.core.text import LabelBase
from views.indexui import RootLay
from helpers import BluetoothHelper
from kivy.utils import platform
from kivy.properties import ObjectProperty
from settings.settingsjson import bluetooth_settings_json

Window.softinput_mode = 'below_target'
LabelBase.register(name='Arial', fn_regular='res/fonts/ArialUnicodeMS.ttf')

if platform == 'android':
    import jnius
    from jnius import autoclass
    from android import activity
    from android.broadcast import BroadcastReceiver

    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
'''
:::::::::::::::: Adywizard 2020/12/13, Sunday at 19:24 on Discord ::::::::::::::::::
For broadcast receiver on bluetooth, amend file --
/.buildozer/android/platform/python-for-android/pythonforandroid/recipes/android/src/android/broadcast.py
def _expand_partial_name(partial_name):
            if '.' in partial_name:
                return partial_name  # Its actually a full dotted name
            else:
                name = 'ACTION_{}'.format(partial_name.upper())

                if hasattr(Intent, name):
                    return getattr(Intent, name)
                elif hasattr(BluetoothAdapter, name):
                    return getattr(BluetoothAdapter, name)
                else:
                    raise Exception('The intent {} doesnt exist'.format(name))

        # resolve actions/categories first
        Intent = autoclass('android.content.Intent')
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
'''
class MainApp(MDApp):
    def build(self):
        self.title = "Bluetooth Input Reader"
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.primary_hue = "400"
        self.icon = '/res/images/poolleaf_16619.png'
        self.use_kivy_settings = False
        self.br = None
        self.br_strt = False
        if platform == 'android':
            self.br = BroadcastReceiver(self.on_broadcast, actions=['state_changed'])

    def build_config(self, config):
        config.setdefaults('bluetoothsettings', {
            'optionsbluetuuid': '00001101-0000-1000-8000-00805f9b34fb',
            'optionsbluetencoding': 'LATIN-1'})

    def build_settings(self, settings):
        settings.add_json_panel('Bluetooth Settings',
                                self.config,
                                data=bluetooth_settings_json)
    def on_start(self):
        BluetoothHelper().run()

    def start_broadcats(self):
        if self.br and not self.br_strt:
            self.br.start()
            self.br_strt = True

    def stop_broadcats(self):
        if self.br and self.br_strt:
            self.br.stop()
            self.br_strt = False

    def on_broadcast(self, context, intent):
        listen = intent.getAction()
        state = None
        if listen == BluetoothAdapter.ACTION_STATE_CHANGED:
            state = intent.getIntExtra(
                BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR)
        if state == BluetoothAdapter.STATE_ON:
            self.root.ids.is_bluetooth.text = 'ON'
            self.root.get_devices()
        elif BluetoothAdapter.STATE_OFF:
            self.root.ids.is_bluetooth.text = 'OFF'
    def on_pause(self):
        self.stop_broadcats()
        self.root.cancel_scale()
        return True

    def on_stop(self):
        self.stop_broadcats()
        self.root.cancel_scale()
        return True

    def on_resume(self):
        self.br = BroadcastReceiver(self.on_broadcast, actions=['state_changed'])
        self.start_broadcats()
        return True

MainApp().run()
