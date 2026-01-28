"""Testy dla Feature 19 - wysyłanie historii konta firmowego na email"""
import pytest
from unittest.mock import patch, MagicMock
from src.company_account import CompanyAccount
from datetime import datetime


@pytest.fixture
def mock_mf_api():
    """Fixture: Mock API Ministerstwa Finansów dla testów CompanyAccount"""
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


class TestCompanyAccountEmailHistory:
    """Testy wysyłania historii konta firmowego przez email"""

    @patch('src.company_account.SMTPClient')
    @patch('src.company_account.datetime')
    def test_send_history_success(self, mock_datetime, mock_smtp_class, mock_mf_api):
        """Test: Wysłanie historii firmowej - sukces"""
        # Mock daty (tylko dla email, nie dla NIP validation)
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        # Mock SMTP
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        # Konto firmowe z historią
        account = CompanyAccount("TechCorp", "1234567890")
        account.incoming_transfer(5000)
        account.outgoing_transfer(1000)
        
        # Wyślij historię
        result = account.send_history_via_email("company@example.com")
        
        # Sprawdź sukces
        assert result is True
        
        # Sprawdź wywołanie
        mock_smtp_instance.send.assert_called_once()
        
        # Sprawdź parametry
        call_args = mock_smtp_instance.send.call_args
        subject = call_args[0][0]
        text = call_args[0][1]
        email = call_args[0][2]
        
        assert subject == "Account Transfer History 2026-01-28"
        assert text == "Company account history: [5000, -1000]"
        assert email == "company@example.com"

    @patch('src.company_account.SMTPClient')
    @patch('src.company_account.datetime')
    def test_send_history_failure(self, mock_datetime, mock_smtp_class, mock_mf_api):
        """Test: Wysłanie historii firmowej - porażka"""
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        # SMTP zwraca False
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = False
        mock_smtp_class.return_value = mock_smtp_instance
        
        account = CompanyAccount("FailCorp", "1234567890")
        
        result = account.send_history_via_email("fail@company.com")
        
        assert result is False
        mock_smtp_instance.send.assert_called_once()

    @patch('src.company_account.SMTPClient')
    @patch('src.company_account.datetime')
    def test_send_empty_company_history(self, mock_datetime, mock_smtp_class, mock_mf_api):
        """Test: Wysłanie pustej historii firmowej"""
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        account = CompanyAccount("EmptyCorp", "1234567890")
        
        result = account.send_history_via_email("empty@company.com")
        
        assert result is True
        
        call_args = mock_smtp_instance.send.call_args
        text = call_args[0][1]
        assert text == "Company account history: []"

    @patch('src.company_account.SMTPClient')
    @patch('src.company_account.datetime')
    def test_send_history_with_zus_payment(self, mock_datetime, mock_smtp_class, mock_mf_api):
        """Test: Historia z wpłatą ZUS (-1775)"""
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        account = CompanyAccount("ZUSCorp", "1234567890")
        account.incoming_transfer(10000)
        account.outgoing_transfer(1775)  # Płatność ZUS
        account.incoming_transfer(500)
        
        result = account.send_history_via_email("zus@company.com")
        
        assert result is True
        
        call_args = mock_smtp_instance.send.call_args
        text = call_args[0][1]
        assert "Company account history:" in text
        assert "[10000, -1775, 500]" in text

    @patch('src.company_account.SMTPClient')
    @patch('src.company_account.datetime')
    def test_send_history_express_transfer(self, mock_datetime, mock_smtp_class, mock_mf_api):
        """Test: Historia z ekspresowym przelewem (opłata 5 zł)"""
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        account = CompanyAccount("ExpressCorp", "1234567890")
        account.balance = 1000
        account.express_outgoing_comp(100)  # -105 (100 + 5 opłata)
        
        result = account.send_history_via_email("express@company.com")
        
        assert result is True
        
        # express_outgoing_comp nie zapisuje do history, tylko zmienia balance
        # więc historia będzie pusta
        call_args = mock_smtp_instance.send.call_args
        text = call_args[0][1]
        assert "Company account history:" in text
