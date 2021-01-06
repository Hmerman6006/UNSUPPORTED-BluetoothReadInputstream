from kivy.app import App
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty, StringProperty, NumericProperty, BooleanProperty, ListProperty
from kivy.utils import platform
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from views.popscroll import PopScroll, PopScrollBut, PopDialog, PopSnackbar, PopDialogWithAction
from helpers import BluetoothHelper

import threading, time
import re

if platform == 'android':
    import jnius
    from jnius import autoclass
    from android import activity
    from android.broadcast import BroadcastReceiver

    Intent = autoclass('android.content.Intent')
    IntentFilter = autoclass('android.content.IntentFilter')
    Context = autoclass('android.content.Context')
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
    bconnect_thread = None  # Bluetooth connect thread
    bcheck_thread = None  # Bluetooth check connect thread
    blue_info = StringProperty('')
    dev_list = ListProperty()
    _is_modal_open = BooleanProperty(False)  # Modalview function
    pop = ObjectProperty(None)
    intent_bltooth = ObjectProperty(None)
    dialog = ObjectProperty(None)
    snackbar = ObjectProperty(None)
    dialog_with_action = ObjectProperty(None)
    background_color = ListProperty()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.device = None
        self.this = App.get_running_app()
        self.dev_list = []
        self._alive = False
        self._check = False
        self.num = 0 #number used to timeout if not updated
        Window.bind(on_keyboard=self.handle_key)
        if platform == 'android':
            self.stream = Stream()
        Clock.schedule_once(self.setup_menu)  # delay until ids are available
    def setup_menu(self, dt):
        self.pop = PopScroll()
        self.snackbar = PopSnackbar()
        self.dialog_with_action = PopDialogWithAction()
        self.dialog = PopDialog()
        if platform == 'android':
            is_enabled = BluetoothHelper().check_bluetooth_enabled()
            if is_enabled:
                self.ids.is_bluetooth.text = 'ON'
                self.get_devices()
            else:
                self.ids.is_bluetooth.text = 'OFF'

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
                                    self.scale_output = self.scale_output + '\n->: Connecting RfcommSocket'
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
                if not self.rfsocket.connected:
                    self.rfsocket.connect()
                    self.scale_output = self.scale_output + '\n->: Connecting port 1'
            else:
                if not self.rfsocket.connected:
                    self.rfsocket.connect()
                    self.scale_output + '\n->: Connecting port 1'
            if self.rfsocket.connected:
                self.blue_info = '[b]Connected[/b]'
                self.scale_output = self.scale_output + '\n->: Connected port 1'
                return True
            else:
                return False
        except jnius.jnius.JavaException as e:
            self.blue_info = '[b]Cannot connect to socket[/b]'
            self.cancel_scale()

    def GetBSerial(self):
        try:
            getDevname = self.ids.dev_button.text
            self.recv_stream, self.send_stream = self.get_socket_stream(getDevname)

            if self.rfsocket is None or self.recv_stream == False:
                if not self.blue_info == '[b]Error[/b]':
                    self.blue_info = '[b]Bluetooth connection failed[/b]'
                    self.scale_output = self.scale_output + '\n->: Connecting stream fail'
                    self.cancel_scale()
            elif not self.rfsocket.connected:
                if not self.blue_info == '[b]Error[/b]':
                    self.blue_info = '[b]Bluetooth connection failed[/b]'
                    self.scale_output =  self.scale_output + '\n->: Connecting bluetooth fail'
            else:
                self.start_bluetooth_thread()
                self.scale_output = ''
        except jnius.jnius.JavaException as e:
            self.blue_info = '[b]Error[/b]'
            self.cancel_scale()

    # main threaded function to read inputstream
    def GetTheInput(self, n):
        try:
            while( self._alive and self.rfsocket.connected and self.recv_stream is not None ):
                input = ''
                self.num = n
                self.ids.stable_output.text = 'Running..'
                input = self.stream.readstream(self.recv_stream)
                self.scale_output = self.scale_output + '\n->: ' + input
            self._check = False
        except jnius.jnius.JavaException as e:
            self.blue_info = '[b]Error[/b]'
            self.scale_output = self.scale_output + '\n->: Error: Connection lost'
            self.cancel_scale()
        except ValueError as e:
            pass

    def start_bluetooth_thread(self):
        self._alive = True
        if self.bconnect_thread is None:
            self.bconnect_thread = threading.Thread(target=self.GetTheInput, args=(10,))
            self.ids.stable_output.text = 'Starting..'
            self.bconnect_thread.start()
        self.start_thread_check()

    def start_thread_check(self):
        self._check = True
        if self.bcheck_thread is None:
            self.bcheck_thread = threading.Thread(target=self.run_timeout, args=(10,))
            self.bcheck_thread.start()

    # threaded function to check Rfcomm connection
    def run_timeout(self, n):
        self.num = n
        while ( self._check and self.num > 0 ):
            if self.rfsocket.connected and self.recv_stream is not None:
                self.num -= 1
            else:
                self.num -= self.num
            if self.bconnect_thread is not None:
                if self.bconnect_thread.is_alive():
                    pass
                else:
                    self.num -= self.num
                    self.scale_output = self.scale_output + '\n->: Thread died'
            if self.num <= 5:
                self.ids.stable_output.text = 'Timeout in ' + str(self.num) + ' sec'
            time.sleep(1)
        self.ids.stable_output.text = 'Disconnecting..'
        self.cancel_scale()

    def bluetooth_thread(self):
        is_enabled = False
        is_enabled = BluetoothHelper().check_bluetooth_enabled()
        if is_enabled:
            if platform == 'android':
                self.GetBSerial()
        else:
            self.dialog_with_action.open_popup_dialog('Enable bluetooth', 'bluetooth', 'info')

    #Disconnect gracefully
    def cancel_scale(self):
        if self.send_stream is not None and self.send_stream:
            self.send_stream.close()
            self.scale_output = self.scale_output + '\n->: Close connection output stream'
        if self.recv_stream is not None and self.recv_stream:
            self.recv_stream.close()
            self.scale_output = self.scale_output + '\n->: Close connection input stream'
        if self.rfsocket is not None:
            if self.rfsocket.connected:
                self.rfsocket.close()
                self.scale_output = self.scale_output + '\n->: Close Rfcomm connection'
        self._alive = False
        self._check = False
        self.num = 0
        self.bconnect_thread = None
        self.bcheck_thread = None
        self.scale_output = self.scale_output + '\n->: Threads is stopped'
        self.blue_info = ''
        self.scale_output = self.scale_output + '\n->: Disconnected'
        self.ids.stable_output.text = 'Disconnected'

    def get_devices(self):
        dev_list = []
        paired_devices = BluetoothAdapter.getDefaultAdapter().getBondedDevices().toArray()
        if len(paired_devices) > 0:
            for dev in paired_devices:
                if dev != None:
                    dev_list.append(dev.getName())
        else:
            self.scale_output = '\n->: No devices paired\n' + self.scale_output
        self.dev_list = dev_list
