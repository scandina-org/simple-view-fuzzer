from queue import Empty, Queue
import select
import subprocess
from threading import Thread
import time
from xml.dom.minidom import Element
import xml.etree.ElementTree as ET
import uiautomator2 as u2
from uiautomator2 import Direction


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

    def get_error_log(self):
        process_id = self.session._pidof_app(self.package_name)
        args = ['adb', 'shell', 'logcat', '*:E', '-b',
                'main,crash', '--pid', str(process_id)]
        adb_process = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
        errors = []
        q = Queue()
        t = Thread(target=self.enqueue_output, args=(adb_process.stdout, q))
        t.daemon = True  # thread dies with the program
        t.start()
        while len(errors) < 10:
            try:
                line = q.get(timeout=1)  # or q.get(timeout=.1)
            except Empty:
                break
            else:
                errors.append(line)
        adb_process.terminate()
        return errors
