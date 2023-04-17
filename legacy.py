from xml.dom.minidom import Element
import uiautomator2 as u2
import xml.etree.ElementTree as ET
import subprocess

APP_NAME = "com.example.empty"

def get_substring_after_last_equal(input_string):
    if "=" in input_string:
        return input_string.rsplit("=", 1)[-1]
    else:
        return ""
def init_apk(path: str):
    device = u2.connect()
    old_packages = subprocess.check_output(args=["adb","shell","pm","list","packages","-f"]).decode().split("\n")
    device.app_install(path)
    new_packages = subprocess.check_output(args=["adb","shell","pm","list","packages","-f"]).decode().split("\n")
    latest_packages = [pkg_name for pkg_name in new_packages if pkg_name not in old_packages]
    if len(latest_packages) < 1:
        raise Exception("Failed to install apk")
    latest_package_name = get_substring_after_last_equal(latest_packages[0])
    return device,latest_package_name


