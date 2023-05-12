from queue import Empty, Queue
import select
import subprocess
from threading import Thread
import time
from xml.dom.minidom import Element
import xml.etree.ElementTree as ET
import uiautomator2 as u2
from uiautomator2 import Direction
import signal


class UIManager:
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.device = u2.connect()
        self.session = self.device.session(package_name, attach=True)

    def reconnect_session(self):
        self.session = self.device.session(self.package_name, attach=True)

    def get_page_resources(self) -> "list[Element]":

        # Get the layout hierarchy
        hierarchy_xml = self.session.dump_hierarchy()

        # Parse the XML hierarchy
        root = ET.fromstring(hierarchy_xml)

        # Loop through each node in the XML tree
        resources = []
        for node in root.iter():
            # Check if the node has a "resource-id" attribute
            if 'resource-id' in node.attrib:
                # Check if the attribute value is not empty
                if node.attrib['resource-id']:
                    # Yield Resource id
                    resources.append(node)
        return resources

    def get_page_package_resource(self):
        return [node for node in self.get_page_resources() if self.package_name in node.attrib['resource-id']]

    def is_text_suggestion_on(self):
        resources = self.get_page_resources()
        bad_rid = ["android:id/suggestionWindowContainer",
                   "android:id/addToDictionaryButton"]
        for node in resources:
            rid = node.attrib['resource-id']
            if rid in bad_rid:
                return True
        return False

    def get_clickable_resources(self, resources: "list[Element]") -> "list[Element]":
        result = []
        for res in resources:
            attrib = res.attrib
            if attrib['resource-id'] and attrib['clickable'] == 'true' and attrib['enabled'] == 'true':
                result.append(res)
        return result

    def get_ui_from_resource(self, resource: Element):
        return self.session(resourceId=resource.attrib['resource-id'])

    def go_back(self):
        if (self.device.device_info['version'].isnumeric() and int(self.device.device_info['version']) < 12):
            self.device.press("back")
        else:
            self.device.swipe_ext(Direction.HORIZ_FORWARD)

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line.decode().strip())
        out.close()

    def run_command(self, command, timeout=3):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout.decode(), stderr.decode()
        except subprocess.TimeoutExpired:
            process.send_signal(signal.SIGTERM)  # Send SIGTERM signal to terminate the process
            try:
                stdout, stderr = process.communicate()
                return stdout.decode(), stderr.decode()
            except:
                return None, None  # Return None for stdout and stderr when an error occurs during the second communicate()

    def run_command(self, command, timeout=1):
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=timeout)
            return stdout.decode(), stderr.decode()
        except subprocess.TimeoutExpired:
            process.send_signal(signal.SIGTERM)  # Send SIGTERM signal to terminate the process
            try:
                stdout, stderr = process.communicate()
                return stdout.decode(), stderr.decode()
            except:
                return None, None  # Return None for stdout and stderr when an error occurs during the second communicate()

    def get_error_log(self):
        process_id = self.session._pidof_app(self.package_name)
        i_args = ['adb', 'shell', 'logcat', '*:I', '-b',
                'main,crash', '--pid', str(process_id)]
        d_args = ['adb', 'shell', 'logcat', '*:D', '-b',
                'main,crash', '--pid', str(process_id)]
        e_args = ['adb', 'shell', 'logcat', '*:E', '-b',
                'main,crash', '--pid', str(process_id)]
        w_args = ['adb', 'shell', 'logcat', '*:W', '-b',
                'main,crash', '--pid', str(process_id)]
        f_args = ['adb', 'shell', 'logcat', '*:F', '-b',
                'main,crash', '--pid', str(process_id)]
        commands = [i_args, d_args, e_args, w_args, f_args]

        line_counts = []
        for command in commands:
            output, _ = self.run_command(command, timeout=1)
            with open('logs.txt', mode='a') as file:
                file.write(output + '\n\n')
            line_count = len(output.splitlines())
            line_counts.append(line_count)

        return line_counts
