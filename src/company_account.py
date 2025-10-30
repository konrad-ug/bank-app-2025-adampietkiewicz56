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

