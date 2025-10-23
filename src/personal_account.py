from src.account import Account

class PersonalAccount(Account):
    def __init__(self, first_name, last_name, pesel, promo_code=None):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.pesel = pesel if len(pesel) == 11 else "Invalid"
        self.promo_code = promo_code

        self.apply_promo()

    def apply_promo(self):
        if self.pesel == "Invalid":
            return

        yy = int(self.pesel[0:2])
        mm = int(self.pesel[2:4])

        if yy <= 60 and (1 <= mm <= 12):
            return

        if self.promo_code and self.promo_code.startswith("PROM_"):
            self.balance += 50.0



