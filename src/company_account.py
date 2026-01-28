from src.account import Account
from smtp.smtp import SMTPClient
import requests
import os
from datetime import datetime


class CompanyAccount(Account):
    def __init__(self, company_name, nip):
        super().__init__()
        self.company_name = company_name
        self.nip = nip if len(nip) == 10 else "Invalid"
        
        # Feature 18: Walidacja NIPu - sprawdzenie w API MF
        if len(nip) == 10:  # Tylko dla poprawnej długości
            if not self._validate_nip_with_mf(nip):
                raise ValueError("Company not registered!!")

    def _validate_nip_with_mf(self, nip: str) -> bool:
        """
        Waliduje NIP poprzez API Ministerstwa Finansów
        Zwraca True jeśli statusVat = "Czynny", False inaczej
        """
        try:
            # Pobierz URL z zmiennej środowiskowej (default: test API)
            mf_url = os.getenv("BANK_APP_MF_URL", "https://wl-test.mf.gov.pl")
            
            # Przygotuj datę w formacie YYYY-MM-DD
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Endpoint do sprawdzenia NIPu
            endpoint = f"{mf_url}/api/search/nip/{nip}"
            params = {"date": today}
            
            # Wyślij request
            response = requests.get(endpoint, params=params, timeout=5)
            
            # Wypisz response w logach
            print(f"[MF API Response for NIP {nip}]: {response.text}")
            
            # Sprawdź czy response jest poprawny
            if response.status_code == 200:
                data = response.json()
                # Szukamy result.subject.statusVat: "Czynny"
                if "result" in data and data["result"]:
                    result = data["result"]
                    subject = result.get("subject")
                    
                    # Jeśli subject jest null - NIP nie istnieje
                    if subject is None:
                        return False
                    
                    # Sprawdź statusVat
                    status_vat = subject.get("statusVat", "")
                    return status_vat == "Czynny"
            
            return False
        except Exception as e:
            print(f"[MF API Error for NIP {nip}]: {str(e)}")
            return False

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
    
    def send_history_via_email(self, email_address: str) -> bool:
        """
        Wysyła historię konta na podany adres email (Feature 19)
        
        Args:
            email_address: Adres email odbiorcy
            
        Returns:
            True jeśli wysłanie się powiodło, False w przeciwnym razie
        """
        # Przygotuj datę w formacie YYYY-MM-DD
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Przygotuj temat i treść maila
        subject = f"Account Transfer History {today}"
        text = f"Company account history: {self.history}"
        
        # Wyślij email przez SMTP client
        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)
