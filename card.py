
class CardAccount:
    def __init__(self, user_db="EdwinOcampo", pass_db="Edwin28", limit_amount=30_000_000):
        self.user_db = user_db
        self.pass_db = pass_db
        self.limit = float(limit_amount)

    def check_credentials(self, user, password):
        return user == self.user_db and password == self.pass_db

    def has_limit_for(self, amount):
        return amount <= self.limit

    def charge(self, amount):
        if amount > self.limit:
            raise ValueError("Supera el cupo limite.")
        self.limit -= amount
        return True

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Monto inválido.")
        self.limit += amount
        return self.limit

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Monto inválido.")
        if amount > self.limit:
            raise ValueError("Saldo insuficiente.")
        self.limit -= amount
        return self.limit

    def change_password(self, current, new_pass):
        if current != self.pass_db:
            raise ValueError("Clave actual incorrecta.")
        if len(new_pass) != 4:
            raise ValueError("La nueva clave debe tener 4 dígitos.")
        self.pass_db = new_pass
        return True