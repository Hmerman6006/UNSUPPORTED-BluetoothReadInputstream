from kivy.app import App
from kivy.utils import platform

#Helper classes to add permissions and enable hardware on_start
class BluetoothHelper():
    def run(self):
        this = App.get_running_app()
        if platform == 'android':
            from android.permissions import request_permissions, Permission, request_permissions
            def callback(permission, results):
                if all(res for res in results):
                    pass
                else:
                    pass

            request_permissions([Permission.BLUETOOTH, Permission.BLUETOOTH_ADMIN], callback)

    def check_bluetooth_enabled(self):
        this = App.get_running_app()
        if platform == 'android':
            import jnius
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            blueAdapt = BluetoothAdapter.getDefaultAdapter()

            if blueAdapt is not None:
                if blueAdapt.isEnabled():
                    return True
                else:
                    return False
            else:
                print('Dialog popup to inform')
                this.root.dialog.open_popup_dialog('Enable Bluetooth and pair devices', 'info')
                return False
        else:
            return False

    def enable_bluetooth(self, *args):
        this = App.get_running_app()
        if platform == 'android':
            import jnius
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            blueAdapt = BluetoothAdapter.getDefaultAdapter()

            blueAdapt.enable()
        this.root.dialog_with_action.remove_action_button()