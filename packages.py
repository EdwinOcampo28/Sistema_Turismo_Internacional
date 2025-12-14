
from utils import format_money, ask_int

class PackageOption:
    def __init__(self, code, name, price):
        self.code = code
        self.name = name
        self.price = float(price)

class PackagesSection:
    def __init__(self):
        self.flight_options = [
            PackageOption(1, "Mexico", 1200000),
            PackageOption(2, "Canada", 1500000),
            PackageOption(3, "Estados Unidos", 2000000),
            PackageOption(4, "Brasil", 900000),
        ]
        self.lodging_options = [
            PackageOption(1, "Estandar", 130000),
            PackageOption(2, "Superior", 170000),
            PackageOption(3, "Lujo", 200000),
            PackageOption(4, "Economico", 90000),
        ]
        self.food_options = [
            PackageOption(1, "Basico", 50000),
            PackageOption(2, "Plus", 80000),
            PackageOption(3, "Premium", 110000),
            PackageOption(4, "Economico", 40000),
        ]
        self.activity_options = [
            PackageOption(1, "Basicas", 170000),
            PackageOption(2, "Aventura", 230000),
            PackageOption(3, "Tours", 270000),
            PackageOption(4, "Economicas", 100000),
        ]
        self.total = 0.0
        self.items = []

    def select_from(self, options, label):
        print(f"--- {label} ---")
        for o in options:
            print(f"{o.code}. {o.name} ({format_money(o.price)})")
        print("5. SALIR")
        choice = ask_int("Ingrese una opcion: ", 1, 5)
        if choice == 5:
            return None
        opt = next(filter(lambda x: x.code==choice, options))
        qty = ask_int(f"Cuántas personas para {opt.name}? ", 1)
        subtotal = opt.price * qty
        self.items.append((label, opt, qty, subtotal))
        self.total += subtotal
        print(f"Agregado {label} -> {opt.name}: {format_money(subtotal)} | Total paquetes: {format_money(self.total)}")
        return True

    def compute_adjusted_total(self, is_weekend=False):
        aumento = self.total * 0.15 if is_weekend else 0
        total_ajustado = self.total + aumento
        tasa = 0.0
        if total_ajustado > 20_000_000:
            tasa = 0.30
        elif total_ajustado > 15_000_000:
            tasa = 0.20
        elif total_ajustado > 10_000_000:
            tasa = 0.10
        descuento = total_ajustado * tasa
        subtotal_con_descuento = total_ajustado - descuento
        iva = subtotal_con_descuento * 0.19
        final = subtotal_con_descuento + iva
        return {
            "subtotal": self.total,
            "aumento": aumento,
            "total_ajustado": total_ajustado,
            "descuento": descuento,
            "subtotal_con_descuento": subtotal_con_descuento,
            "iva": iva,
            "final": final
        }