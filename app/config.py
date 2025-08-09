import os
from pathlib import Path
from dotenv import load_dotenv

# Charge .env depuis la racine du projet, peu importe où est lancé le script
BASE_DIR = Path(__file__).resolve().parent.parent 
load_dotenv(dotenv_path=BASE_DIR / ".env")

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# print(
#     f"DB_NAME={DB_NAME}, DB_USER={DB_USER}, DB_PASSWORD={DB_PASSWORD}, DB_HOST={DB_HOST}, DB_PORT={DB_PORT}"
# )

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
