"""Testy dla Feature 19 - wysyłanie historii konta na email"""
import pytest
from unittest.mock import patch, MagicMock
from src.personal_account import PersonalAccount
from datetime import datetime


class TestPersonalAccountEmailHistory:
    """Testy wysyłania historii konta osobistego przez email"""

    @patch('src.personal_account.SMTPClient')
    @patch('src.personal_account.datetime')
    def test_send_history_success(self, mock_datetime, mock_smtp_class):
        """Test: Wysłanie historii - sukces (zwraca True)"""
        # Mock daty
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        # Mock SMTP client
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        # Utwórz konto z historią
        account = PersonalAccount("John", "Doe", "12345678901")
        account.incoming_transfer(100)
        account.outgoing_transfer(50)
        
        # Wyślij historię
        result = account.send_history_via_email("test@example.com")
        
        # Sprawdź czy sukces
        assert result is True
        
        # Sprawdź czy metoda send została wywołana raz
        mock_smtp_instance.send.assert_called_once()
        
        # Sprawdź parametry wywołania
        call_args = mock_smtp_instance.send.call_args
        subject = call_args[0][0]
        text = call_args[0][1]
        email = call_args[0][2]
        
        assert subject == "Account Transfer History 2026-01-28"
        assert text == "Personal account history: [100, -50]"
        assert email == "test@example.com"

    @patch('src.personal_account.SMTPClient')
    @patch('src.personal_account.datetime')
    def test_send_history_failure(self, mock_datetime, mock_smtp_class):
        """Test: Wysłanie historii - porażka (zwraca False)"""
        # Mock daty
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        # Mock SMTP client - zwraca False
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = False
        mock_smtp_class.return_value = mock_smtp_instance
        
        # Utwórz konto
        account = PersonalAccount("Jane", "Smith", "98765432109")
        
        # Wyślij historię
        result = account.send_history_via_email("fail@example.com")
        
        # Sprawdź czy porażka
        assert result is False
        
        # Sprawdź czy metoda została wywołana
        mock_smtp_instance.send.assert_called_once()

    @patch('src.personal_account.SMTPClient')
    @patch('src.personal_account.datetime')
    def test_send_empty_history(self, mock_datetime, mock_smtp_class):
        """Test: Wysłanie pustej historii"""
        # Mock daty
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        # Mock SMTP
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        # Konto bez transakcji
        account = PersonalAccount("Alice", "Wonder", "11122233344")
        
        result = account.send_history_via_email("empty@example.com")
        
        assert result is True
        
        # Sprawdź treść - pusta lista
        call_args = mock_smtp_instance.send.call_args
        text = call_args[0][1]
        assert text == "Personal account history: []"

    @patch('src.personal_account.SMTPClient')
    @patch('src.personal_account.datetime')
    def test_send_history_with_multiple_transactions(self, mock_datetime, mock_smtp_class):
        """Test: Wysłanie historii z wieloma transakcjami"""
        mock_datetime.now.return_value.strftime.return_value = "2026-01-28"
        
        mock_smtp_instance = MagicMock()
        mock_smtp_instance.send.return_value = True
        mock_smtp_class.return_value = mock_smtp_instance
        
        # Konto z wieloma transakcjami
        account = PersonalAccount("Bob", "Builder", "55566677788")
        account.incoming_transfer(500)
        account.outgoing_transfer(100)
        account.incoming_transfer(200)
        account.express_outgoing_pers(50)  # -50 i -1 (opłata)
        
        result = account.send_history_via_email("multi@example.com")
        
        assert result is True
        
        # Sprawdź historię
        call_args = mock_smtp_instance.send.call_args
        text = call_args[0][1]
        assert "Personal account history:" in text
        assert "[500, -100, 200, -50, -1.0]" in text
