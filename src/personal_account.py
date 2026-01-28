from src.account import Account
from smtp.smtp import SMTPClient
from datetime import datetime


class PersonalAccount(Account):
    def __init__(self, first_name, last_name, pesel, promo_code=None):
        super().__init__()
        self.first_name = first_name
        self.last_name = last_name
        self.pesel = pesel if len(pesel) == 11 else "Invalid"
        self.promo_code = promo_code

        self.apply_promo()

    def apply_promo(self):
        if self.pesel == "Invalid":
            return

        yy = int(self.pesel[0:2])
        mm = int(self.pesel[2:4])

        if yy <= 60 and (1 <= mm <= 12):
            return

        if self.promo_code and self.promo_code.startswith("PROM_"):
            self.balance += 50.0

    def express_outgoing_pers(self, amount: float) -> None:
        fee = 1.0
        total = amount + fee

        # sprawdź, czy środki są wystarczające i kwota dodatnia
        if amount <= 0 or total > self.balance:
            return

        # najpierw wykonaj zwykły przelew (zapisze "-50.0" w historii)
        self.outgoing_transfer(amount)

        # potem pobierz opłatę (zapisze "-1.0" w historii)
        self.outgoing_transfer(fee)

    def _has_last_three_deposits(self) -> bool:
        """Sprawdza czy ostatnie 3 transakcje to wpłaty."""
        if len(self.history) < 3:
            return False
        return all(amount > 0 for amount in self.history[-3:])
    
    def _has_positive_balance_from_last_five(self, loan_amount: float) -> bool:
        """Sprawdza czy suma ostatnich 5 transakcji > kwota kredytu."""
        if len(self.history) < 5:
            return False
        return sum(self.history[-5:]) > loan_amount
    
    def submit_for_loan(self, amount: float) -> bool:
        """Składa wniosek o kredyt."""
        if self._has_last_three_deposits() or self._has_positive_balance_from_last_five(amount):
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
        text = f"Personal account history: {self.history}"
        
        # Wyślij email przez SMTP client
        smtp_client = SMTPClient()
        return smtp_client.send(subject, text, email_address)
    
    def to_dict(self):
        """Konwertuje konto do słownika dla MongoDB"""
        return {
            "type": "personal",
            "first_name": self.first_name,
            "last_name": self.last_name,
            "pesel": self.pesel,
            "balance": self.balance,
            "history": self.history,
            "promo_code": self.promo_code
        }
    
    @staticmethod
    def from_dict(data):
        """Tworzy PersonalAccount z słownika"""
        account = PersonalAccount(
            first_name=data["first_name"],
            last_name=data["last_name"],
            pesel=data["pesel"],
            promo_code=data.get("promo_code")
        )
        # Nadpisz balance i history (bez wywoływania apply_promo ponownie)
        account.balance = data["balance"]
        account.history = data["history"]
        return account
