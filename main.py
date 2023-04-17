import time
import uiautomator2 as u2
from ui_manager import UIManager
import sys
import click

from word_fuzzer import WordFuzzer

def main():
    package_name= sys.argv[1]
    word_file = sys.argv[2]
    ui_manager = UIManager(package_name)
    fuzzer = WordFuzzer()
    _STATE = "RUNNING"
    time.sleep(1)
    while _STATE == "RUNNING":
        resources = ui_manager.get_page_resources()
        selected_field = select_resource(resources,"Type in a number to select an input field to fuzz")
        selected_button = select_resource(resources,"Type in a number to select a submit button")
        try:
            if (selected_field is not None and selected_button is not None):
                with open(word_file,'r') as wf:
                    lines = wf.readlines()
                    for line in lines:
                        field = ui_manager.get_ui_by_resource_id(selected_field.attrib['resource-id'])
                        button = ui_manager.get_ui_by_resource_id(selected_button.attrib['resource-id'])
                        fuzzer.fuzz(field,button,line)
            print("===============================================")  
        except Exception as e:
            print(e)
            if isinstance(e,u2.SessionBrokenError):
                print("application crashed")
                print(e)
        finally:
            choices = {
                'q':"Quit",
                'c':'Continue',
                'b': 'Go back'
            }
            selected = None
            while (selected is None):
                selected = select_keys(choices,"Please enter")
            if selected == 'Quit':
                ui_manager.device.app_stop(package_name)
                _STATE = "STOP"
            elif selected == "Continue":
                continue
            elif selected == 'Go back':
                ui_manager.go_back()
                continue

def select_keys(map: dict[str,str],message):
    prompt = '\n'.join(f'{k}) {v}' for i, (k,v) in enumerate(map.items()))

    prompt = prompt + f"\n{message}"
    key = click.prompt(prompt,type=str,show_choices=True)
    print(key)
    if key in map:
        res = map[key]
        click.echo(f"You selected {map[key]}.")
        return res
    return None
        
def select_resource(resources: list,message: str):
    prompt = '\n'.join(f'{i+1}) {c.attrib["resource-id"]}' for i, c in enumerate(resources))

    prompt = prompt + f"\n{message}"
    index = click.prompt(prompt,type=int,show_choices=True)
    if (index < 0 or index > len(resources)):
        click.echo("You did not select anything.")
        resource = None
    else:
        resource = resources[index-1]
        click.echo(f"You selected {resource.attrib['resource-id']}.")
    return resource

if __name__ == "__main__":
    main()
