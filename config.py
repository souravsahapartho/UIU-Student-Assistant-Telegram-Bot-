import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    admin_ids_str = os.getenv("ADMIN_USER_IDS", "")
    ADMIN_USER_IDS = [
        int(id.strip()) for id in admin_ids_str.split(",") if id.strip().isdigit()
    ]

    DEFAULT_CREDIT_FEE = 6500
    DEFAULT_TRIMESTER_FEE = 10000
    DEFAULT_OTHER_FEES = 0
    DEFAULT_MINIMUM_PAYMENT = 20000

    DEFAULT_SCHOLARSHIP_CREDIT_LIMIT = 13
    DEFAULT_SCHOLARSHIP_GPA_THRESHOLD = 3.50
    DEFAULT_PROBATION_THRESHOLD = 2.00

    DEFAULT_FIRST_RETAKE_DISCOUNT_PERCENT = 50

    INSTALLMENT_1_PERCENT = 0.40
    INSTALLMENT_2_PERCENT = 0.30
    INSTALLMENT_3_PERCENT = 0.30

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is missing in .env file! Please add it.")
