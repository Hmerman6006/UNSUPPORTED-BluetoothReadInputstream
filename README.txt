Kivy app that reads the Inputstream via Bluetooth
*So far only platform implemented for is android

Directory tree MVC:
    main.py, main.kv, helpers.py -----
                                      |_/views directory contains root and other view .kv
                                      |_/settings directory contains settingsjson.py and other configs
                                      |_/res contains external java, images and fonts

Android:
    Implements java class stored in external file that uses io.Inputstream and io.BufferedReader
    to read Input until end of line ascii 10 ('\n') or 13 ('\r')

    Compile:
        build with buildozer

    Packages:
        kivy, kivymd, plyer, android (see buildozer.spec)
        *uses minimal widgets of kivymd due to "TypeError: argument of type 'module' is not iterable" if
        widgets are not loaded in App class only use some widgets

    External java:
        buildozer.spec List of Java files to add section points to:
        android.add_src = %(source.dir)s/res/ext_java/*.java

    Permissions:
        INTERNET,BLUETOOTH,BLUETOOTH_ADMIN

    Something to look at:
        Sometimes UI freezes if cannot find connection
        Handle bluetooth device sudden power off or disconnection
        .gif presplash not having animated loading effect
