from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class TestExpressTransfers:

    def test_express_outgoing_pers(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0
        account.express_outgoing_pers(50.0)
        assert account.balance == 49.0

    def test_express_outgoing_comp(self):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.express_outgoing_comp(50.0)
        assert account.balance == 45.0
    
    def test_express_outgoing_comp_negative_amount(self):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.express_outgoing_comp(-10.0)
        assert account.balance == 100.0  # brak zmiany

    def test_express_outgoing_comp_insufficient_funds(self):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 40.0
        account.express_outgoing_comp(50.0)
        assert account.balance == 40.0  # brak zmiany