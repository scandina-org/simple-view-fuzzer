
import json
import sys
import subprocess
from colorify import *
from androguard.core.bytecodes import apk
from ui_manager import UIManager
import uiautomator2 as u2

instance = {}

def load(apk_filename):
    if apk_filename[-4:] == ".apk":
        try:
            a = apk.APK(apk_filename)
            package_name = a.get_package()
            subprocess.run(['adb', 'install', apk_filename])
            instance = {'file_name': apk_filename, 'package_name': package_name}
            instance_json = json.dumps(instance)
            ui_manager = UIManager(package_name)

            with open('instance.json', 'w') as file:
                file.write(instance_json)
            ui_manager.reconnect_session()
            print("instance loaded")

        except Exception as e:
            print("Error loading apk to emulator")
            
    else:
        print()

def list():
    print("first run might take a while")
    instance = ""
    with open('instance.json', 'r') as file:
        instance = json.load(file)

    ui_manager = UIManager(instance['package_name'])

    resources = ui_manager.get_page_package_resource()

    resource_dict = {}
    for i in range(len(resources)):
        re = resources[i]
        print(f"{i}) {re.attrib['resource-id']}")
        resource_dict[i] = re.attrib['resource-id']
        
    instance['resources'] = resource_dict
    instance_json = json.dumps(instance)

    with open('instance.json', 'w') as file:
        file.write(instance_json)


if sys.platform == 'win32':
    init_colorify()


if len(sys.argv) < 2:
    print("Try running ./python svf.py help")

if sys.argv[1].lower() == 'help':
    print("help here")

elif sys.argv[1].lower() == 'load':
    apk_filename = sys.argv[2]
    load(apk_filename)

elif sys.argv[1].lower() == 'list':
    list()