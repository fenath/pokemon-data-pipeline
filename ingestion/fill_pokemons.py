import requests
import sys
import json
import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime


if len(sys.argv) > 1:
    try:
        # O primeiro argumento (sys.argv[1]) é a string JSON com os parâmetros e variáveis
        vars = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        print("Erro ao decodificar os argumentos JSON.")        
        vars = {}
else:
    vars = {}

API_URL = "https://pokeapi.co/api/v2/pokemon/?limit=5000"

# ==========================================
# CONFIG
# ==========================================

PROJECT_ID = vars.get("GCP_PROJECT_ID")
DATASET_ID = "bronze"
TABLE_ID = "pokemons"

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

credentials = service_account.Credentials.from_service_account_info(json.loads(vars["GCP_PROJECT_CREDENTIALS"]))
client = bigquery.Client(project=PROJECT_ID, credentials=credentials)

# ==========================================
# GET POKEAPI
# ==========================================

def main():
    response = requests.get(
            API_URL
            )
    response.raise_for_status()
    now = datetime.now()

    data = response.json()

    # ==========================================
    # TRANSFORMA EM DATAFRAME
    # ==========================================
    rows = []
    for pokemon in data["results"]:
        rows.append({
            "id": pokemon["url"].split("/")[-2],
            "name": pokemon["name"],
            "url": pokemon["url"],
            "fetched_at": now
        })

    df = pd.DataFrame(rows)

    print(df)

    # ==========================================
    # CRIA TABELA STAGING TEMPORÁRIA
    # ==========================================

    staging_table = f"{PROJECT_ID}.{DATASET_ID}.pokemon_staging"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    )

    load_job = client.load_table_from_dataframe(
        df,
        FULL_TABLE_ID,
        job_config=job_config
    )

    load_job.result()

    print("Dados adicionados (Modo: APPEND)")

if __name__ == '__main__':
    main()

