from src.company_account import CompanyAccount

class TestCompanyAccount:

    def test_company_account_creation(self):
        account = CompanyAccount("Firma", "1234567890")
        assert account.company_name == "Firma"
        assert account.nip == "1234567890"

    def test_invalid_nip(self):  
        account = CompanyAccount("Firma", "123456789")
        assert account.company_name == "Firma"
        assert account.nip == "Invalid"

    