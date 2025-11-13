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

    def express_outgoing_pers(self, amount: float) -> None:
        fee = 1.0
        total = amount + fee

        # sprawdź, czy środki są wystarczające i kwota dodatnia
        if amount <= 0 or total > self.balance:
            return

        # najpierw wykonaj zwykły przelew (zapisze "-50.0" w historii)
        self.outgoing_transfer(amount)

        # potem pobierz opłatę (zapisze "-1.0" w historii)
        self.outgoing_transfer(fee)

    def submit_for_loan(self, amount):
        def one():
            return len(self.history) >= 3 and all(float(x) > 0 for x in self.history[-3:])
                
        
        def two():
            return len(self.history) >= 5 and sum(float(x) for x in self.history[-5:]) > amount
                

        approved = one() or two()

        if approved:
            self.balance += amount

        return approved
    
        


