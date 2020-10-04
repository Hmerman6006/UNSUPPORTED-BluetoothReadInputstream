from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.utils import platform
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from views.popscroll import PopScroll, PopScrollBut, PopDialog, PopSnackbar, PopDialogWithAction
from helpers import BluetoothHelper

import threading
import re

if platform == 'android':
    import jnius
    from jnius import autoclass

    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
    BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
    InputStreamReader = autoclass('java.io.InputStreamReader')
    BufferedReader = autoclass('java.io.BufferedReader')
    UUID = autoclass('java.util.UUID')
    Stream = autoclass('org.kivy.android.ReadStream')

class RootLay(FloatLayout):
    this = ObjectProperty(None)  # App objec
    recv_stream = ObjectProperty(None)
    send_stream = ObjectProperty(None)
    stream = ObjectProperty(None)
    rfsocket = ObjectProperty(None)
    device = ObjectProperty(None)
    scale_output = StringProperty('\n->: No Input\n->: See Devices \n->: Connect')
    weigh_tick = ObjectProperty(None)
    the_weight = NumericProperty()  # Weigh time numerical
    weigh_tme = NumericProperty()  # Weigh time numerical
    bconnect_thread = ObjectProperty(None)  # Bluetooth connect thread
    blue_conn = BooleanProperty(False)
    blue_info = StringProperty('')
    dev_list = ListProperty()
    _is_modal_open = BooleanProperty(False)  # Modalview function
    pop = ObjectProperty(None)
    dialog = ObjectProperty(None)
    snackbar = ObjectProperty(None)
    dialog_with_action = ObjectProperty(None)
    background_color = ListProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device = None
        self.this = App.get_running_app()
        self.dev_list = []
        self.stream = Stream()
        Window.bind(on_keyboard=self.handle_key)
        Clock.schedule_once(self.setup_menu)  # delay until ids are available
    def setup_menu(self, dt):
        self.pop = PopScroll()
        self.snackbar = PopSnackbar()
        self.dialog_with_action = PopDialogWithAction()
        self.dialog = PopDialog()
    def handle_key(self, window, key, *args):
        if key == 27:
            if self.ids._screen_manager.current == 'home':
                self.this.stop()
            return True
    def get_socket_stream(self, name):
        defaultCharBufferSize = 8192
        getUuid = self.this.config.get('bluetoothsettings', 'optionsbluetuuid')
        getEncode = self.this.config.get('bluetoothsettings', 'optionsbluetencoding')
        try:
            blueAdapt = BluetoothAdapter.getDefaultAdapter()
            if self.rfsocket is not None:
                if self.rfsocket.connected:
                    recv_stream = self.rfsocket.getInputStream()
                    send_stream = self.rfsocket.getOutputStream()
                else:
                    self.rfsocket = self.device.createRfcommSocketToServiceRecord(UUID.fromString(getUuid))
                    if self.get_port_connect():
                        recv_stream = self.rfsocket.getInputStream()
                        send_stream = self.rfsocket.getOutputStream()
            else:
                if blueAdapt is not None:
                    if blueAdapt.isEnabled():
                        paired_devices = blueAdapt.getBondedDevices().toArray()
                        self.rfsocket = None
                        for self.device in paired_devices:
                            if self.device.getName() == name:
                                if self.device.bluetoothEnabled:
                                    self.rfsocket = self.device.createRfcommSocketToServiceRecord(
                                        UUID.fromString(getUuid))
                                    if self.rfsocket is not None:
                                        if self.get_port_connect():
                                            recv_stream = self.rfsocket.getInputStream()
                                            send_stream = self.rfsocket.getOutputStream()
                                            break
                                        else:
                                            self.blue_info = '[b]Bluetooth connection failed[/b]'
                    else:
                        self.blue_info = '[b]Bluetooth not enabled[/b]'
            if recv_stream is not None and send_stream is not None:
                return recv_stream, send_stream
            else:
                return False, False
        except UnboundLocalError as e:
            return False, False
        except TypeError as e:
            return False, False

    def get_port_connect(self):
        try:
            if self.rfsocket.port <= 0:
                self.rfsocket = self.device.createRfcommSocket(1)
                if self.rfsocket.connected is False:
                    self.rfsocket.connect()
            else:
                if self.rfsocket.connected is False:
                    self.rfsocket.connect()
            if self.rfsocket.connected is True:
                self.blue_info = '[b]Connected[/b]'
                return True
            else:
                return False
        except jnius.jnius.JavaException as e:
            self.blue_info = '[b]Cannot connect to socket[/b]'
            self.cancel_scale()

    def GetBSerial(self):
        try:
            getDevname = self.this.config.get('bluetoothsettings', 'stringbluedevname')
            self.recv_stream, self.send_stream = self.get_socket_stream(getDevname)

            if self.rfsocket is None or self.recv_stream == False:
                if not self.blue_info == '[b]Error[/b]':
                    self.blue_info = '[b]Bluetooth connection failed[/b]'
                    self.cancel_scale()
            elif not self.rfsocket.connected:
                if not self.blue_info == '[b]Error[/b]':
                    self.blue_info = '[b]Bluetooth connection failed[/b]'
            else:
                self.weight_ticker()
                self.scale_output = ''
        except jnius.jnius.JavaException as e:
            self.blue_info = '[b]Error[/b]'
            self.cancel_scale()

    def GetInput(self):
        try:
            input = ''
            if self.rfsocket.connected is True and self.recv_stream is not None:
                if self.weigh_tme > 0:
                    input = self.stream.readstream(self.recv_stream)
                    self.scale_output = self.scale_output + '\n->: ' + input
                    self.weigh_tme -= 1
                    self.weigh_tick()
                else:
                    self.weight_ticker()
            else:
                self.GetBSerial()
        except jnius.jnius.JavaException as e:
            self.blue_info = '[b]Error[/b]'
            self.cancel_scale()
        except ValueError as e:
            pass

    def weight_ticker(self):
        self.weigh_tme = 1000
        self.weigh_tick = Clock.create_trigger(lambda dt: self.GetInput(), 0)
        self.weigh_tick()

    def bluetooth_thread(self):
        is_enabled = False
        is_enabled = BluetoothHelper().check_bluetooth_enabled()
        if is_enabled:
            if platform == 'android':
                self.bconnect_thread = threading.Thread(target=self.GetBSerial)
                self.bconnect_thread.start()
        else:
            self.dialog_with_action.open_popup_dialog('Enable bluetooth', 'bluetooth', 'info')

    #Disconnect gracefully
    def cancel_scale(self):
        if self.bconnect_thread is not None:
            if self.bconnect_thread.isAlive():
                self.bconnect_thread._stop()
        if self.weigh_tick is not None:
            self.weigh_tick.cancel()
        if self.send_stream is not None:
            self.send_stream.close()
        if self.recv_stream is not None:
            self.recv_stream.close()
        if self.rfsocket is not None:
            if self.rfsocket.connected:
                self.rfsocket.close()
        self.blue_info = ''
        self.scale_output = self.scale_output + '\n->: Disconnected'

    def get_devices(self):
        dev_list = []
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        if len(paired_devices) > 0:
            for dev in paired_devices:
                if dev != None:
                    dev_list.append(dev.getName())
        else:
            self.scale_output = '\n->: No devices paired\n' + self.scale_output
        return dev_list
