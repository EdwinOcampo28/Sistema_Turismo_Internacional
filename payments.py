
from card import CardAccount
from utils import format_money

class PaymentProcessor:
    def __init__(self, card_account: CardAccount):
        self.card = card_account
        # track last payments
        self.last_cash_payment = 0.0
        self.last_card_payment = 0.0

    def pay_cash(self, total):
        # request multiples of 1000
        while True:
            try:
                amount = float(input(f"Total a pagar: {format_money(total)}. Ingrese monto en efectivo: "))
            except ValueError:
                print("Ingrese un número válido.")
                continue
            if amount < total:
                print("Monto insuficiente.")
                continue
            if (amount % 1000) != 0:
                print("Ingrese múltiplos de 1000.")
                continue
            self.last_cash_payment = amount
            change = amount - total
            return {"method":"cash", "paid": amount, "change": change}

    def pay_card(self, total):
        attempts = 3
        while attempts > 0:
            user = input("Usuario tarjeta: ").strip()
            pwd = input("Contraseña tarjeta: ").strip()
            if self.card.check_credentials(user, pwd):
                if not self.card.has_limit_for(total):
                    print("Error: supera el cupo limite de la tarjeta.")
                    return {"method":"card", "success": False, "reason": "limit"}
                self.card.charge(total)
                self.last_card_payment = total
                return {"method":"card", "paid": total, "remaining_limit": self.card.limit}
            attempts -= 1
            print(f"Credenciales incorrectas. Intentos restantes: {attempts}")
        print("Cuenta bloqueada.")
        return {"method":"card", "success": False, "reason":"auth"}