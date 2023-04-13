from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
import os
from pathlib import Path
import smtplib
from typing import Dict, List, Any

from auction import Auction
from user import User


class AuctionEmailNotifier:
    def __init__(self) -> None:
        self.__smtp_host = 'smtp.gmail.com'
        self.__smtp_port = 587
        self.__smtp_email = self.__get_environment_variable('auction_email_notifier_email')
        self.__smtp_email_password = self.__get_environment_variable('auction_email_notifier_email_password')
    
    def __get_environment_variable(self, name: str) -> str:
        value = os.environ.get(name)
        if not value:
            raise Exception(f"Undefined environment variable: '{name}'.")

        return value

    def send_email_notification(self, user: User, auctions: List[Auction]) -> None:
        message = MIMEMultipart()
        message['from'] = 'Auction Tracker'
        message['to'] = user.email
        message['subject'] = 'My Auctions'
        body = self.__create_body(user, auctions)        
        message.attach(MIMEText(body, 'html'))
        self.__send_email(message)
    
    @staticmethod
    def __create_body(user: User, auction: List[Auction]) -> str:
        template = Template(Path('template.html').read_text())
        auction_table_headers = Auction.get_auction_fields()
        auction_table_rows = [a.get_auction_data() for a in auctions]
        body_template_data = {
            'user': user.name,
            'auction_table_headers': auction_table_headers,
            'auction_table_rows': auction_table_rows
        }
        
        return template.render(body_template_data)

    def __send_email(self, message: MIMEMultipart) -> None:
        with smtplib.SMTP(host=self.__smtp_host, port=self.__smtp_port) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(self.__smtp_email, self.__smtp_email_password)
            smtp.send_message(message)
            print('Email sent...')


if __name__ == '__main__':
    user = User(name='Bob', email='changeme@bogus.com')
    auctions = [
        Auction(year=2020, make='Toyota', model='Camry', mileage=12345, url='google.ca'),
        Auction(year=2020, make='Honda', model='X', mileage=54321, url='google.ca')
    ]

    auction_email_notifier = AuctionEmailNotifier()
    auction_email_notifier.send_email_notification(user, auctions)
