class Account:

    def __init__(self):
        self.balance = 0.0
        self.history = []

    def outgoing_transfer(self, amount: float) -> None:
        if (amount <= 0 or amount > self.balance):
            return

        self.balance -= amount
        self.history.append(f'-{amount}')
        
    

    def incoming_transfer(self, amount: float):
        if amount <= 0:
            return
        else:
            self.balance += amount
            self.history.append(f'{amount}')

    
