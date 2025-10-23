from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


class TestExpressTransfers:

    def test_express_personal_transfer(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0

        account.send_personal_express_transfer(50.0)
        assert account.balance == 49.00

    def test_express_company_transfer(self):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.send_company_express_transfer(50.0)
        assert account.balance == 45.00