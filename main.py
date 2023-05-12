import asyncio
import io
import os
import time
from typing import IO
from xml.dom.minidom import Element
import uiautomator2 as u2
from choice import select_index_from_list, select_key_from_map
from ui_manager import UIManager
import sys
from androguard.core.bytecodes import apk
from colorify import *
import subprocess
import pandas as pd


WORD_FILES_DIR = "wordfiles"
if sys.platform == 'win32':
    init_colorify()

def main():
    if len(sys.argv) <= 1:
        print("Empty package name")
        return
    package_name = sys.argv[1]
    if package_name[-4:] == ".apk":
        a = apk.APK(package_name)
        subprocess.run(['adb', 'install', package_name])
        package_name = a.get_package()
    _STATE = "RUNNING"
    time.sleep(1)

    print("Welcome to Simple View Fuzzer")
    print("type " + colorify("help", C.orange) + " to get started")
    ui_manager = UIManager(package_name)

    print(colorify(f"Found Running Application: {package_name}", C.green))
    while _STATE == "RUNNING":
        resources = ui_manager.get_page_package_resource()
        command = input("Please Enter your command:")

        command_args = command.split(" ")

        if command_args[0].lower() == "fuzz":
            if "-b" in command_args and "-w" in command_args and "-f" in command_args:
                options = get_fuzz_options(command_args)
                try:
                    fields = [resources[int(i)] for i in options['field_indx']]
                    button = resources[int(options['button_indx'][0])]
                    wordfile = open(options['wordlist'], 'r')
                except Exception as e:
                    print(e)
                    print("Invalid command, check " +
                          colorify('help', C.orange))
                    continue
                try:
                    fuzz(ui_manager, fields, button, wordfile, "--go-back" in command_args, "--real-time" in command_args)
                    print("\nFuzzing succeed with no crash.")
                    res = pd.read_csv('result.csv')
                    print(colorify("Logs Count", C.yellow))
                    print(res.to_string(index=False) + "\n")
                except u2.exceptions.UiObjectNotFoundError as e:
                    print(
                        colorify("Cannot interact with selected user interface", C.red))
                    print("Application may have crashed.")
                    print("type 'launch' to relaunch the package.")
                    res = pd.read_csv('result.csv')
                    print(colorify("Logs Count", C.yellow))
                    print(res.to_string(index=False) + "\n")
                    continue
                    
                    

            else:
                print("Invalid command, check " + colorify('help', C.orange))

        elif command_args[0].lower() == "exit":
            print(colorify("Bye!", C.red))
            return

        elif command_args[0].lower() == "list":
            resources = ui_manager.get_page_package_resource()
            for i in range(len(resources)):
                re = resources[i]
                print(f"{i}) {re.attrib['resource-id']}")
            # print list of fuzzable field resource id

        elif command_args[0].lower() == "help":
            print_help_text()
        elif command_args[0].lower() == "launch":
            ui_manager.reconnect_session()
        else:
            print("Unknown command. How about we start with " +
                  colorify('help', C.orange))


def get_fuzz_options(args):
    button_inputs = []
    field_inputs = []
    if "-b" in args and "-w" in args and "-f" in args:
        b_index = args.index("-b")
        w_index = args.index("-w")
        f_index = args.index("-f")
        temp_button_inputs = args[b_index + 1:]
        if b_index == max(b_index, w_index, f_index):
            button_inputs = temp_button_inputs
        else:
            next_index = None
            for i, item in enumerate(temp_button_inputs):
                if item.startswith("-"):
                    next_index = i
                    break
            button_inputs = temp_button_inputs[:next_index]

        temp_field_inputs = args[f_index + 1:]
        if f_index == max(b_index, w_index, f_index):
            field_inputs = args[f_index + 1:]
        else:
            next_index = None
            for i, item in enumerate(temp_field_inputs):
                if item.startswith("-"):
                    next_index = i
                    break
            field_inputs = temp_field_inputs[:next_index]

        wordlist_inputs = args[w_index + 1]
        # print({"wordlist": wordlist_inputs,
        #       "button_indx": button_inputs, "field_indx": field_inputs})
        return {"wordlist": wordlist_inputs, "button_indx": button_inputs, "field_indx": field_inputs}


def fuzz(ui: UIManager, fields, button, wordfile: IO, isGoBack, isRealTime):
    words = wordfile.readlines()

    total_headers = ['input', 'info_logs', 'debug_logs', 'error_logs', 'warning_logs', 'fatal_logs']
    csv_row = ','.join(map(str, total_headers))

    with open('result.csv', mode='w') as file:
        file.write(csv_row + '\n')
        
    old_logs = ui.get_error_log()

    if isRealTime:
        print('\t'.join(total_headers))

    for word in words:
        formatted_word = word.rstrip('\r\n')
        for field in fields:
            field_ui = ui.get_ui_from_resource(field)
            # print(
            #     f"Filling {field_ui.info['resourceName']} with: {formatted_word}\n")
            field_ui.clear_text()
            field_ui.send_keys(formatted_word)
        # print(f"Fuzzing selected fields with {formatted_word}\n")
        button_ui = ui.get_ui_from_resource(button)
        button_ui.click()   
        logs = ui.get_error_log()
        result = [int(x) - int(y) for x, y in zip(logs, old_logs)]
        old_logs = logs[:]
        logs.insert(0, formatted_word)
        result.insert(0, formatted_word)

        csv_row = ','.join(map(str, result))
        with open('result.csv', mode='a') as file:
            file.write(csv_row + '\n')

        if isGoBack:
            ui.go_back()

def list_word_files():
    return [os.path.join(WORD_FILES_DIR, path) for path in os.listdir(WORD_FILES_DIR)]


def print_help_text():
    print(colorify("\nlist", C.cyan) +
          "\n\tget all available fuzzable fields in the current page along with the action button")
    print(colorify("\nfuzz -f [fields] -w [wordlist] -b [button] (--go-back)", C.cyan) +
          "\n\tfuzz through all the specified fields with the wordlist")
    print("\n\tfor example: fuzz -f 1 2 -w ./dummies.txt -b 3")
    print("\tThis command will fuzz through the the first and second fields from the 'list' command with the 'dummies.txt' wordlist and uses the the third element from the 'list' command as a submit button")
    print(colorify("\nlaunch", C.cyan))
    print("\n\tlaunch or relaunch target package")

    print(colorify("\nhelp", C.cyan) + "\n\twhat you are seeing")
    print(colorify("\nexit", C.cyan) + "\n\tquit this tool")


if __name__ == "__main__":
    main()
