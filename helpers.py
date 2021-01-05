from kivy.app import App
from kivy.utils import platform
from kivy.properties import ObjectProperty, NumericProperty
from kivy.clock import Clock

if platform == 'android':
    import jnius
    from jnius import autoclass
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')

#Helper classes to add permissions and enable hardware on_start
class BluetoothHelper():
    bluet_tick = ObjectProperty(None)
    bluet_tme = NumericProperty()
    def run(self):
        this = App.get_running_app()
        if platform == 'android':
            from android.permissions import request_permissions, Permission, request_permissions
            def callback(permission, results):
                if all(res for res in results):
                    pass
                else:
                    for (i, res) in enumerate(results, start=0):
                        if res:
                            print(permission[i], res)
                        else:
                            print(permission[i], 'no permission')

            request_permissions([Permission.BLUETOOTH, Permission.BLUETOOTH_ADMIN, Permission.ACCESS_COARSE_LOCATION, Permission.ACCESS_FINE_LOCATION], callback)

    def check_bluetooth_enabled(self):
        this = App.get_running_app()
        if platform == 'android':
            blueAdapt = BluetoothAdapter.getDefaultAdapter()

            if blueAdapt is not None:
                if blueAdapt.isEnabled():
                    return True
            # this.root.dialog.open_popup_dialog('Enable Bluetooth and pair devices', 'info')
            this.root.dialog_with_action.open_popup_dialog('Enable bluetooth', 'bluetooth', 'info')
            return False
        else:
            return False

    def enable_bluetooth(self, *args):
        this = App.get_running_app()
        if platform == 'android':
            blueAdapt = BluetoothAdapter.getDefaultAdapter()

            blueAdapt.enable()
        this.root.dialog_with_action.remove_action_button()
        if this.br is not None:
            this.br.start()