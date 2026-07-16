"""
adzuna_extractor.py

Extrait des offres d'emploi depuis l'API Adzuna (avec pagination)
et les charge en brut (JSON/VARIANT) dans Snowflake, table RAW.JOB_OFFERS.

Usage :
    python adzuna_extractor.py
"""

import os
import time
import json
import requests
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()

# --- Config Adzuna ---
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
COUNTRY = "fr"                 # code pays Adzuna (fr, gb, us, ...)
WHAT = "data analyst"          # mot-clé de recherche
RESULTS_PER_PAGE = 50           # max autorisé par Adzuna
NB_PAGES = 5                    # nombre de pages à récupérer (à ajuster)
SLEEP_BETWEEN_CALLS = 1          # secondes, pour rester correct vis-à-vis de l'API

# --- Config Snowflake ---
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE", "JOB_BOARD_WH")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE", "JOB_BOARD_DB")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "RAW")


def fetch_adzuna_page(page: int) -> list:
    """Récupère une page de résultats depuis l'API Adzuna."""
    url = f"https://api.adzuna.com/v1/api/jobs/{COUNTRY}/search/{page}"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": RESULTS_PER_PAGE,
        "what": WHAT,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()  # lève une exception si erreur HTTP
    data = response.json()
    return data.get("results", [])


def fetch_all_pages(nb_pages: int) -> list:
    """Boucle sur plusieurs pages et concatène les résultats."""
    all_offers = []

    for page in range(1, nb_pages + 1):
        print(f"Récupération de la page {page}/{nb_pages}...")
        try:
            offers = fetch_adzuna_page(page)
        except requests.exceptions.RequestException as e:
            print(f"Erreur lors de la récupération de la page {page} : {e}")
            continue

        if not offers:
            print(f"Plus de résultats à partir de la page {page}, arrêt.")
            break

        all_offers.extend(offers)
        time.sleep(SLEEP_BETWEEN_CALLS)

    print(f"Total récupéré : {len(all_offers)} offres.")
    return all_offers


def load_to_snowflake(offers: list):
    """Charge chaque offre en brut (VARIANT) dans Snowflake."""
    if not offers:
        print("Aucune offre à charger.")
        return

    conn = snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA,
    )

    try:
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO JOB_OFFERS (raw_data)
            SELECT PARSE_JSON(%s)
        """
        for offer in offers:
            cursor.execute(insert_sql, (json.dumps(offer),))

        conn.commit()
        print(f"{len(offers)} offres chargées dans {SNOWFLAKE_DATABASE}.{SNOWFLAKE_SCHEMA}.JOB_OFFERS.")
    finally:
        cursor.close()
        conn.close()


def main():
    offers = fetch_all_pages(NB_PAGES)
    load_to_snowflake(offers)


if __name__ == "__main__":
    main()