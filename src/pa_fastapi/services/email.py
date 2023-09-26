import os

from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pathlib import Path
from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from services.auth import auth

class Settings(ConnectionConfig, BaseSettings):
    load_dotenv()

settings = Settings()
settings.TEMPLATE_FOLDER = Path(__file__).parent / 'templates'
# conf = ConnectionConfig(
#     MAIL_USERNAME="example@meta.ua",
#     MAIL_PASSWORD="secretPassword",
#     MAIL_FROM=EmailStr("example@meta.ua"),
#     MAIL_PORT=465,
#     MAIL_SERVER="smtp.meta.ua",
#     MAIL_FROM_NAME="Desired Name",
#     MAIL_STARTTLS=False,
#     MAIL_SSL_TLS=True,
#     USE_CREDENTIALS=True,
#     VALIDATE_CERTS=True,
#     TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
# )

class Email():
    async def send_email(self, email: EmailStr, username: str, host: str):
        try:
            token_verification = auth.create_email_token({"sub": email})
            message = MessageSchema(
                subject="Confirm your email ",
                recipients=[email],
                template_body={"host": host, "username": username, "token": token_verification},
                subtype=MessageType.html
            )

            fm = FastMail(settings)
            await fm.send_message(message, template_name="email.html")
        except ConnectionErrors as err:
            print(err)

email = Email()

