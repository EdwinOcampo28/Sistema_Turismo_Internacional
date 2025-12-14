
from utils import ask_int

def menu_select(prompt, options):
    print("="*40)
    print(prompt)
    for i, opt in enumerate(options, start=1):
        print(f"{i}. {opt}")
    print("="*40)
    choice = ask_int("Ingrese una opción: ", 1, len(options))
    return choice