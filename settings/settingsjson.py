import json

bluetooth_settings_json = json.dumps([
	{'type': 'title',
	'title': 'Settings for Bluetooth'},
	{'type': 'string',
	'title': 'Bluetooth Device Name',
	'desc': 'Set bluetooth device name',
	'section': 'bluetoothsettings',
	'key': 'stringbluedevname'},
	{'type': 'options',
	'title': 'Uuid',
	'desc': 'Choose uuid',
	'section': 'bluetoothsettings',
	'key': 'optionsbluetuuid',
	'options': ['00001101-0000-1000-8000-00805f9b34fb','00000000-0000-1000-8000-00805f9b34fb']},
	{'type': 'options',
	'title': 'Type Encoding',
	'desc': 'Choose encoding',
	'section': 'bluetoothsettings',
	'key': 'optionsbluetencoding',
	'options': ['LATIN-1','UTF-8','UTF-16','US-ASCII']}])