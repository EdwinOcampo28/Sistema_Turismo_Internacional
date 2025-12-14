
import datetime
import random

def ask_int(prompt, min_value=None, max_value=None):
    while True:
        try:
            v = int(input(prompt))
            if min_value is not None and v < min_value:
                print(f"Error: debe ser >= {min_value}")
                continue
            if max_value is not None and v > max_value:
                print(f"Error: debe ser <= {max_value}")
                continue
            return v
        except ValueError:
            print("Error: ingrese un número entero válido.")

def ask_float(prompt, min_value=None):
    while True:
        try:
            v = float(input(prompt))
            if min_value is not None and v < min_value:
                print(f"Error: debe ser >= {min_value}")
                continue
            return v
        except ValueError:
            print("Error: ingrese un número válido.")

def ask_bool(prompt):
    while True:
        s = input(prompt + " (s/n): ").strip().lower()
        if s in ('s','si','y','yes'):
            return True
        if s in ('n','no'):
            return False
        print("Respuesta inválida. Use 's' o 'n'.")

def format_money(value):
    return f"$ {value:,.0f}"

def current_date_time_str():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

def rnd_invoice_number():
    return random.randint(100000, 999999)