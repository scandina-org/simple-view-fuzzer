import os
import time
from xml.dom.minidom import Element
import uiautomator2 as u2
from choice import select_index_from_list, select_key_from_map
from ui_manager import UIManager
import sys
import click


WORD_FILES_DIR = "wordfiles"


def main():
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
            for field_resource, word_file in selected_pairs:
                print(f"Fuzzing {field_resource.attrib['resource-id']}")
                field = ui_manager.get_ui_from_resource(field_resource)
                with open(word_file, 'r') as wf:
                    lines = wf.readlines()
                    for line in lines:
                        fuzz(field, button, line)
                print("===============================================")
        except Exception as e:
            print(e)
            if isinstance(e, u2.SessionBrokenError):
                print("application crashed")
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


def fuzz(field, button, word):
    field.send_keys(word)
    button.click()
    field.clear_text()


def list_word_files(withFullPath=False):
    return os.listdir(WORD_FILES_DIR) if not withFullPath else [os.path.join(WORD_FILES_DIR, path) for path in os.listdir(WORD_FILES_DIR)]


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
            wordfiles, f"Select a word file to fuzz input {selected_field.attrib['resource-id']}")]
        selected_pairs.append((selected_field, selected_wordfile))
        decision = select_key_from_map(
            decisionMap, "Do you want to continue[c] or add more inputs to fuzz[a]?")
    button = resources[select_index_from_list(
        choices, "Type in a number to select a submit button")]
    return selected_pairs, button


if __name__ == "__main__":
    main()
