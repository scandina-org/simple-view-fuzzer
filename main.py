import asyncio
import io
import os
import time
from xml.dom.minidom import Element
import uiautomator2 as u2
from choice import select_index_from_list, select_key_from_map
from ui_manager import UIManager
import sys


WORD_FILES_DIR = "wordfiles"


def main():
    if len(sys.argv) <= 1:
        print("Empty package name")
        return
    package_name = sys.argv[1]
    ui_manager = UIManager(package_name)
    _STATE = "RUNNING"
    time.sleep(1)
    while _STATE == "RUNNING":
        resources = ui_manager.get_page_resources()
        word_files = list_word_files()
        selected_pairs, selected_button = select_resource(
            resources, word_files)
        try:
            button = ui_manager.get_ui_from_resource(
                selected_button)
            field_word_pairs = []
            for field_resource, word_file in selected_pairs:
                field = ui_manager.get_ui_from_resource(field_resource)
                word_stream = open(word_file,'r')
                field_word_pairs.append((field,word_stream))
            fuzz_pairwise(ui_manager,field_word_pairs,button)
        except Exception as e:
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print("Application Crash")
            print(e)
        finally:
            choices = {
                'q': "Quit",
                'r': 'Retry',
                'b': 'Go back'
            }
            decision = select_key_from_map(choices, "Please enter")
            if decision == 'q':
                ui_manager.device.app_stop(package_name)
                _STATE = "STOP"
            elif decision == "r":
                continue
            elif decision == 'b':
                ui_manager.go_back()
                continue


def fuzz_pairwise(ui,pairs,button):
    emptyLineCount = 0
    while emptyLineCount < len(pairs):
        emptyLineCount = 0
        for field,word_stream in pairs:
            line = word_stream.readline()
            if not line:
                emptyLineCount += 1
            else:
                print(f"Fuzzing {field.info['resourceName']} with: {line}")
                field.send_keys(line)
        button.click()
        errors = ui.get_error_log()
        if (len(errors) > 0):
            for err in errors: print(err)
        else:
            print("No error found.")
        print("===================================================\n")

def list_word_files():
    return [os.path.join(WORD_FILES_DIR, path) for path in os.listdir(WORD_FILES_DIR)]


def select_resource(resources: Element, wordfiles: list):
    decision = ""
    selected_pairs = []
    choices = [r.attrib['resource-id'] for r in resources]

    decisionMap = {
        "c": "Continue",
        "a": "Add more inputs"
    }
    while not decision or decision == "a":
        selected_field = resources[select_index_from_list(
            choices, "Type in a number to select an input field to fuzz")]
        selected_wordfile = wordfiles[select_index_from_list(
            [os.path.basename(f) for f in wordfiles], f"Select a word file to fuzz input {selected_field.attrib['resource-id']}")]
        selected_pairs.append((selected_field, selected_wordfile))
        decision = select_key_from_map(
            decisionMap, "Do you want to continue[c] or add more inputs to fuzz[a]?")
    button = resources[select_index_from_list(
        choices, "Type in a number to select a submit button")]
    return selected_pairs, button


if __name__ == "__main__":
    main()
