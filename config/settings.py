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
SMS_COST_NPR = 0.6  # Updated: direct NTC rate (Sparrow resells at 1.4-1.5)

SPARROW_TOKEN = os.getenv("SPARROW_TOKEN")
SPARROW_SENDER_ID = os.getenv("SPARROW_SENDER_ID")

# NTC SMS Alert — credentials provided by NTC after contract signing
# Contact: vas@ntc.net.np | Leave blank until credentials are received
NTC_TOKEN = os.getenv("NTC_TOKEN")
NTC_SENDER_ID = os.getenv("NTC_SENDER_ID")