class Account:
    def __init__(self, first_name, last_name, pesel, balance = 0):

        self.first_name = first_name
        self.last_name = last_name
        self.pesel = pesel if len(pesel) == 11 else "Invalid"
        self.balance = balance
