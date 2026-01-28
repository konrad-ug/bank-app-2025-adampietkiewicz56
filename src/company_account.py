from src.account import Account

class CompanyAccount(Account):
    def __init__(self, company_name, nip):
        super().__init__()
        self.company_name = company_name
        self.nip = nip if len(nip) == 10 else "Invalid"

    def express_outgoing_comp(self, amount):
        fee = 5.0
        total_amount = amount + fee
        if (amount > 0 and total_amount <= self.balance + fee):
            self.balance -= total_amount

    def _has_sufficient_balance(self, amount: float) -> bool:
        """Sprawdza czy saldo >= 2x kwota kredytu"""
        return self.balance >= 2 * amount

    def _has_zus_payment(self) -> bool:
        """Sprawdza czy w historii jest wpłata do ZUS (-1775)"""
        return -1775 in self.history

    def take_loan(self, amount: float) -> bool:
        """Składa wniosek o kredyt firmowy"""
        if self._has_sufficient_balance(amount) and self._has_zus_payment():
            self.balance += amount
            return True
        return False