"""SMTP Client for sending emails"""


class SMTPClient:
    """Client for sending emails via SMTP server"""
    
    def send(self, subject: str, text: str, email_address: str) -> bool:
        """
        Sends email via SMTP
        
        Args:
            subject: Email subject
            text: Email body/content
            email_address: Recipient email address
            
        Returns:
            True if sending succeeded, False otherwise
        """
        # tutaj byłby kod odpowiedzialny za wysłanie maila
        # return True jezeli wyslanie sie powiodło
        # return False jezeli wyslanie sie nie powiodło
        return False
