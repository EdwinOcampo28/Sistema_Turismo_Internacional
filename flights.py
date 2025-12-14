
from utils import format_money, ask_int

class FlightOption:
    def __init__(self, code, name, price):
        self.code = code
        self.name = name
        self.price = float(price)

class FlightsSection:
    def __init__(self):
        self.options = [
            FlightOption(1, "Santa Marta", 330000),
            FlightOption(2, "Cartagena", 250000),
            FlightOption(3, "Bogota", 180000),
            FlightOption(4, "Bucaramanga", 150000),
        ]
        self.total = 0.0
        self.subtotals = []

    def show_menu_and_add(self):
        print("=== MENU DE DESTINOS (NACIONALES) ===")
        for opt in self.options:
            print(f"{opt.code}. {opt.name} ({format_money(opt.price)})")
        print("5. SALIR")
        choice = ask_int("Ingrese una opcion: ", 1, 5)
        if choice == 5:
            return False
        opt = next(filter(lambda o: o.code==choice, self.options))
        qty = ask_int(f"Cuántas personas para {opt.name}? ", 1)
        subtotal = opt.price * qty
        self.subtotals.append((opt, qty, subtotal))
        self.total += subtotal
        print(f"Subtotal agregado: {format_money(subtotal)} | Total vuelos: {format_money(self.total)}")
        return True

    def compute_adjusted_total(self, is_holiday=False):
        aumento = self.total * 0.15 if is_holiday else 0
        total_ajustado = self.total + aumento
        # descuentos por tramos
        tasa = 0.0
        if total_ajustado > 3_000_000:
            tasa = 0.30
        elif total_ajustado > 2_000_000:
            tasa = 0.20
        elif total_ajustado > 1_000_000:
            tasa = 0.10
        descuento = total_ajustado * tasa
        base_despues = total_ajustado - descuento
        iva = base_despues * 0.19
        final = base_despues + iva
        return {
            "subtotal": self.total,
            "aumento": aumento,
            "total_ajustado": total_ajustado,
            "descuento": descuento,
            "base_despues": base_despues,
            "iva": iva,
            "final": final
        }