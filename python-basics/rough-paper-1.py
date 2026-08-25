from typing import Protocol

class SmsSender(Protocol):
    def sendSms(self, message:str) -> None: ...
    def bulkSms(self, recipient_list: list[str], message: str) -> bool: ...

def sendSingleSms(sender: SmsSender, message: str):
    sender.sendSms(message=message)

def sendGroupSms(sender: SmsSender, recipient_list: list[str], message: str):
    sender.bulkSms(recipient_list=recipient_list, message=message)
    

class InternationalSms:
    def sendSms(self, message: str):
        print(f"Messeage sent: {message}")
        
    def bulkSms(self, recipient_list: list[str], message: str):
            for item in recipient_list:
                print(f"Message sent to {item}: {message}")

class NationalSms:
    def sendSms(self, message: str):
        print(f"Messeage sent: {message}")
        
    def bulkSms(self, recipient_list: list[str], message: str):
        for item in recipient_list:
            print(f"Message sent to {item}: {message}")

sendSingleSms(InternationalSms(), "Welcome to global")
sendGroupSms(NationalSms(), ["Global", "Khalti", "esewa", "Barclys"], "Your account has been renewed.")