import click


def select_key_from_map(map: "dict[str,str]", message):
    prompt = '\n'.join(f'{k}) {v}' for i, (k, v) in enumerate(map.items()))
    prompt = prompt + f"\n{message}"
    key = ""
    while key not in map:
        key = click.prompt(prompt, type=str, show_choices=True)
        if key in map:
            click.echo(f"You selected {map[key]}.")
            return key


def select_index_from_list(arr: list, message: str):
    prompt = '\n'.join(f'{i+1}) {c}' for i, c in enumerate(arr))
    index = -1
    while index < 0:
        prompt = prompt + f"\n{message}"
        index = click.prompt(prompt, type=int, show_choices=True)
        if (index < 0 or index > len(arr)):
            click.echo("You did not select anything.")
            index = -1
        else:
            click.echo(f"You selected {arr[index-1]}.")
        return index
