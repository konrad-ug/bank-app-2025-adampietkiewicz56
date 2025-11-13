from src.personal_account import PersonalAccount
from src.account import Account


class TestLoan:
    def test_loan_personal_accept_one(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        account.incoming_transfer(50.0)
        account.incoming_transfer(150.0)
        account.incoming_transfer(250.0)
        account.submit_for_loan(300.0)


        assert account.balance == 900.0
        assert account.submit_for_loan(300.0) == True

    def test_loan_personal_reject_two(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 150.0
        account.outgoing_transfer(50.0)
        account.outgoing_transfer(50.0)
        account.incoming_transfer(50.0)
        account.submit_for_loan(300.0)


        assert account.balance == 100.0
        assert account.submit_for_loan(300.0) == False


    def test_loan_personal_accept_two(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 0.0
        account.incoming_transfer(100.0)
        account.incoming_transfer(100.0)
        account.incoming_transfer(200.0)
        account.incoming_transfer(200.0)
        account.outgoing_transfer(100.0)

        account.submit_for_loan(400.0)


        assert account.balance == 900.0
        assert account.submit_for_loan(300.0) == True

    def test_loan_personal_reject_two(self):
        account = PersonalAccount("Alice", "Johnson", "12345678901")
        account.balance = 0.0
        account.incoming_transfer(100.0)
        account.incoming_transfer(100.0)
        account.incoming_transfer(200.0)
        account.incoming_transfer(200.0)
        account.outgoing_transfer(400.0)
        account.submit_for_loan(400.0)


        assert account.balance == 200
        assert account.submit_for_loan(300.0) == False

        