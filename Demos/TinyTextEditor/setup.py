from distutils.core import setup
import py2app
import os

plist = dict(
    CFBundleDocumentTypes = [
    dict(
    	CFBundleTypeExtensions = ["txt"],
    	CFBundleTypeName = "Text",
    	CFBundleTypeRole = "Editor",
    	NSDocumentClass = "TinyTextEditorDocument",
    	LSTypeIsPackage = True,
        ),
        ],
	CFBundleIdentifier = "com.typesupply.TinyTextEditor",
	LSMinimumSystemVersion = "10.3.9",
	CFBundleShortVersionString = "1.0.0",
	CFBundleVersion = "1.0.0",
	)

dataFiles = [
		'Resources/English.lproj',
		]

setup(
	data_files=dataFiles,
	app=[dict(script="TinyTextEditor.py", plist=plist)]
	)
