class Account:

    def __init__(self):
        self.balance = 0.0

    def outgoing_transfer(self, amount):
        if amount <= 0 or amount > self.balance:
            return

        self.balance -= amount
        
    

    def incoming_transfer(self, amount):
        if amount <= 0:
            return
        else:
            self.balance += amount

    
