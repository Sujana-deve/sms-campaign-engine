from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'port': os.getenv('DB_PORT'),
    'dbname': os.getenv('DB_NAME')
}

GATEWAY_MODE = os.getenv('GATEWAY_MODE', 'simulate')
SMS_RATE_LIMIT = 5
SMS_COST_NPR = 1.5

SPARROW_TOKEN = os.getenv("SPARROW_TOKEN")
SPARROW_SENDER_ID = os.getenv("SPARROW_SENDER_ID")