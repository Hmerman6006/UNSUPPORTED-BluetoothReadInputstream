## Kivy app that reads the Inputstream via Bluetooth
The [Kivy](https://kivy.org/doc/stable/) and [KivyMD](https://kivymd.readthedocs.io/en/latest/) app uses existing OS Api to read the string output from bluetooth device. 

_*So far only platform implemented for is android_

###### Directory tree MVC:
```
main.py, main.kv, helpers.py -----
                          |_/views directory contains root and other view .kv
                          |_/settings directory contains settingsjson.py and other configs
                          |_/res contains external java, images and fonts
```

### OS Android
> Implements java class stored in external file that uses `io.Inputstream` and `io.BufferedReader`
  to read Input until end of line `ascii 10 ('\n') or 13 ('\r'`).
> For use of `BroadcastReceiver` you needs to amend the following file -- 
> * `/.buildozer/android/platform/python-for-android/pythonforandroid/recipes/android/src/android/broadcast.py`, 
> by adding the code below after first build.

**BROADCASTRECEIVER CODE:**
```
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
```

###### Compile:
1. build with [buildozer](https://buildozer.readthedocs.io/en/latest/) command `buildozer android debug deploy`.
1. after amending above mentioned file run `buildozer android clean`.
1. run build command again.

###### Packages:
> kivy, kivymd, plyer, android (see buildozer.spec) <br />
> *uses widgets of kivymd where possible due to `TypeError: argument of type 'module' is not iterable` if
> widgets are not loaded in App class.

###### External java:
`buildozer.spec` list of Java files to add section points to: <br />
        `android.add_src = %(source.dir)s/res/ext_java/*.java`

###### Permissions:
* INTERNET,BLUETOOTH,BLUETOOTH_ADMIN, ACCESS_COARSE_LOCATION, ACCESS_FINE_LOCATION 
  
###### Something to look at:
1. Sometimes UI freezes if cannot find connection. **SOLVED** 
1. Handle bluetooth device sudden power off or disconnection. **SOLVED**
1. .gif presplash not having animated loading effect.
1. BroadcastReceiver does not start if initialised in class scope and bluetooth is already ON.
1. Maybe test thread for connection to RfcommSocket.

###### Solved:
1. UI does not freeze when connection is suddenly lost due to Threads on bluetooth RfcommSocket connection.
1. Added BroadcastReceiver to check Bluetooth state on.

##### NOTES:
> Cleaned up code.  Tested and no problems yet.
> BroadcastReceiver is implemented only if bluetooth is off `on_start`.  Need to implement `on_pause` and `on_resume`, but only once resolving BroadcastReceiver scope issue.

###### Tested with following versions:
* Python 3.6.9
* Kivy 1.11.1
* KivyMD 0.1.4
* Android 7.1.2 on Zebra TC25
