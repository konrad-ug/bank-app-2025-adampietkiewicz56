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


class TestTransfers:

    def test_outgoing_transfer(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 100.0

        account.outgoing_transfer(50.0)
        assert account.balance == 50.0

    def test_outgoing_transfer_exceeding_balance(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0

        account.outgoing_transfer(50.0)
        assert account.balance == 30.0

    def test_incoming_transfer_negative_amount(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0
        account.incoming_transfer(-20.0)
        assert account.balance == 30.0

    def test_incoming_transfer_correct_amount(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 30.0
        account.incoming_transfer(20.0)
        assert account.balance == 50.0

    def test_incoming_transfer_correct_amount_company(self, mock_mf_api):
        account = CompanyAccount("Firma", "1234567890")
        account.balance = 100.0
        account.incoming_transfer(20.0)
        assert account.balance == 120.0
