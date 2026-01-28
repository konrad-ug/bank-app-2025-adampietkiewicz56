import pytest
from unittest.mock import patch, MagicMock
from src.personal_account import PersonalAccount
from src.company_account import CompanyAccount


@pytest.fixture
def mock_mf_api():
    """Fixture: Mock API Ministerstwa Finansów"""
    with patch('src.company_account.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "subject": {"statusVat": "Czynny", "nip": "1234567890"}
            }
        }
        mock_response.text = '{"result": {"subject": {"statusVat": "Czynny"}}}'
        mock_get.return_value = mock_response
        yield mock_get


class TestExpressTransfers:

    def test_express_outgoing_pers(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0
        account.express_outgoing_pers(50.0)
        assert account.balance == 49.0

    def test_express_outgoing_pers_insufficient_funds(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 40.0
        account.express_outgoing_pers(50.0)
        assert account.balance == 40.0  # brak zmiany

    def test_express_outgoing_comp(self, mock_mf_api):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.express_outgoing_comp(50.0)
        assert account.balance == 45.0
    
    def test_express_outgoing_comp_negative_amount(self, mock_mf_api):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.express_outgoing_comp(-10.0)
        assert account.balance == 100.0  # brak zmiany

    def test_express_outgoing_comp_insufficient_funds(self, mock_mf_api):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 40.0
        account.express_outgoing_comp(50.0)
        assert account.balance == 40.0  # brak zmiany