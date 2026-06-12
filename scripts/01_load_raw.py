import pandas as pd
import mysql.connector
import logging
import os
from dotenv import load_dotenv

# ── Logging setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s — %(levelname)s — %(message)s'
)
logger = logging.getLogger(__name__)

# ── Config (no hardcoded credentials) ───────────────────────────────────────
load_dotenv()

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'elsa_raw')
}

DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'ELSA_Raw_Messy.xlsx')

def load_raw_data():
    # ── Load Excel ───────────────────────────────────────────────────────────
    logger.info("Reading Excel file...")
    df = pd.read_excel(DATA_PATH, dtype=str)
    df = df.where(pd.notnull(df), None)
    logger.info(f"Loaded {len(df)} rows and {len(df.columns)} columns from Excel")

    # ── Connect to MySQL ─────────────────────────────────────────────────────
    logger.info("Connecting to MySQL...")
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    logger.info("Connection successful")

    # ── Insert rows ──────────────────────────────────────────────────────────
    cols = ','.join(df.columns)
    placeholders = ','.join(['%s'] * len(df.columns))
    sql = f'INSERT INTO marketing_raw ({cols}) VALUES ({placeholders})'

    success = 0
    failed = 0

    for idx, row in df.iterrows():
        try:
            cursor.execute(sql, tuple(row))
            success += 1
        except Exception as e:
            logger.warning(f"Row {idx} failed: {e}")
            failed += 1

    conn.commit()
    cursor.close()
    conn.close()

    logger.info(f"Done — {success} rows inserted, {failed} rows failed")

if __name__ == '__main__':
    load_raw_data()