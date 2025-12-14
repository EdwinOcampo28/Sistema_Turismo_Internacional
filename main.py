
from utils import ask_int, ask_bool, ask_float, format_money, current_date_time_str, rnd_invoice_number
from card import CardAccount
from payments import PaymentProcessor
from flights import FlightsSection
from packages import PackagesSection

def main():
    print("="*30)
    print("BIENVENIDO A LA AGENCIA DE VIAJES")
    print("="*30)
    nombre = input("Ingrese su nombre: ").strip()
    apellido = input("Ingrese su apellido: ").strip()

    # validar cedula 4 digitos
    while True:
        try:
            cedula = int(input("Ingrese los ultimos 4 digitos de su cedula (1000-9999): "))
            if 1000 <= cedula <= 9999:
                break
            print("Debe tener 4 digitos (1000-9999).")
        except ValueError:
            print("Ingrese números solamente.")

    # inicializaciones
    card = CardAccount()
    payments = PaymentProcessor(card)

    # Vuelos locales
    flights = FlightsSection()
    while True:
        cont = flights.show_menu_and_add()
        if not cont:
            break

    print("Resumen vuelos acumulados:", format_money(flights.total))
    is_holiday = ask_bool("¿Hoy es festivo?")
    flights_summary = flights.compute_adjusted_total(is_holiday)
    print("\n--- FACTURA VUELOS LOCALES ---")
    print("Subtotal vuelos:", format_money(flights_summary['subtotal']))
    print("Aumento festivo:", format_money(flights_summary['aumento']))
    print("Descuento:", format_money(flights_summary['descuento']))
    print("IVA (19%):", format_money(flights_summary['iva']))
    print("Total a pagar vuelos:", format_money(flights_summary['final']))

    # elegir metodo de pago vuelos
    print("\nMetodo de pago - Vuelos")
    print("1. Efectivo")
    print("2. Tarjeta Credito")
    m = ask_int("Seleccione metodo: ", 1, 2)
    pago_vuelos_info = None
    if m == 1:
        pago_vuelos_info = payments.pay_cash(flights_summary['final'])
    else:
        pago_vuelos_info = payments.pay_card(flights_summary['final'])

    # Paquetes internacionales
    packages = PackagesSection()
    # vuelos (paquete), hospedaje, comida, actividades
    while True:
        print("\nSeleccionar parte del paquete (vuelo/hospedaje/comida/actividad):")
        print("1. Vuelo Internacional")
        print("2. Hospedaje")
        print("3. Comida")
        print("4. Actividades")
        print("5. SALIR")
        sel = ask_int("Opción: ", 1, 5)
        if sel == 5:
            break
        if sel == 1:
            packages.select_from(packages.flight_options, "Vuelo")
        elif sel == 2:
            packages.select_from(packages.lodging_options, "Hospedaje")
        elif sel == 3:
            packages.select_from(packages.food_options, "Comida")
        elif sel == 4:
            packages.select_from(packages.activity_options, "Actividad")

    print("Resumen paquetes acumulados:", format_money(packages.total))
    is_weekend = ask_bool("¿Es fin de semana?")
    salary = ask_float("Cual es su salario mensual: ", 0)
    save_pct = ask_float("Que porcentaje desea ahorrar (%): ", 0)
    save_monthly = salary * (save_pct / 100.0) if save_pct > 0 else 0
    months_needed = (packages.total / save_monthly) if save_monthly > 0 else float('inf')

    packages_summary = packages.compute_adjusted_total(is_weekend)
    print("\n--- FACTURA PAQUETES INTERNACIONALES ---")
    print("Subtotal paquetes:", format_money(packages_summary['subtotal']))
    print("Aumento fin de semana:", format_money(packages_summary['aumento']))
    print("Descuento:", format_money(packages_summary['descuento']))
    print("IVA (19%):", format_money(packages_summary['iva']))
    print("Total a pagar paquetes:", format_money(packages_summary['final']))
    print(f"Meses necesarios ahorrando {save_pct}%: {months_needed if months_needed != float('inf') else 'No aplicable (ahorro 0)'}")

    # metodo de pago paquetes
    print("\nMetodo de pago - Paquetes")
    print("1. Efectivo")
    print("2. Tarjeta Credito")
    m2 = ask_int("Seleccione metodo: ", 1, 2)
    pago_paquetes_info = None
    if m2 == 1:
        pago_paquetes_info = payments.pay_cash(packages_summary['final'])
    else:
        pago_paquetes_info = payments.pay_card(packages_summary['final'])

    # imprimir factura final
    print("\n" + "="*30)
    print("FACTURA")
    print(f"Cliente: {nombre} {apellido} | CC ultimos 4 digitos: {cedula}")
    print("Numero factura:", rnd_invoice_number())
    print("Fecha y hora:", current_date_time_str())
    print("- Vuelos total:", format_money(flights_summary['final']))
    print("- Paquetes total:", format_money(packages_summary['final']))
    total_to_pay = flights_summary['final'] + packages_summary['final']
    print("TOTAL GENERAL (Vuelos + Paquetes):", format_money(total_to_pay))
    print("="*30)
    print("Gracias por usar nuestro servicio.")

if __name__ == '__main__':
    main()