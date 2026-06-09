import sys
import datetime
import requests
import pandas as pd

from google.oauth2 import service_account
from google.cloud import bigquery

# ===========================================
# Configuração GCP
# ===========================================

GCP = requests.get(
    "http://localhost:8004/api/variables/GCP_PROJECT_CREDENTIALS/value"
).json()["value"]

PROJECT_ID = requests.get(
    "http://localhost:8004/api/variables/GCP_PROJECT_ID/value"
).json()["value"]

credentials = service_account.Credentials.from_service_account_info(GCP)

client = bigquery.Client(
    project=PROJECT_ID,
    credentials=credentials,
)

# ===========================================
# Mapeamento species_name -> pokemon_id
# ===========================================

pokemon_df = client.query("""
SELECT
    pokemon_id,
    species_name
FROM bronze.pokemon_species
""").to_dataframe()

pokemon_map = {
    row.species_name: row.pokemon_id
    for _, row in pokemon_df.iterrows()
}

# ===========================================
# Busca evolution chains ainda não carregadas
# ===========================================

query = """
SELECT DISTINCT evolution_chain_url AS url

FROM bronze.pokemon_species p

WHERE NOT EXISTS (

    SELECT 1

    FROM bronze.evolution_chains e

    WHERE p.evolution_chain_url =
        CONCAT(
            'https://pokeapi.co/api/v2/evolution-chain/',
            CAST(e.chain_id AS STRING),
            '/'
        )

)
"""

rows = client.query(query).result()

records = []

fetched_at = datetime.datetime.utcnow()

# ===========================================
# Função recursiva
# ===========================================


def walk(chain_id, node):

    from_name = node["species"]["name"]

    from_pokemon = pokemon_map.get(from_name)

    for child in node["evolves_to"]:

        to_name = child["species"]["name"]

        to_pokemon = pokemon_map.get(to_name)

        details = {}

        if child["evolution_details"]:
            details = child["evolution_details"][0]

        trigger = None

        if details.get("trigger"):
            trigger = details["trigger"]["name"]

        records.append(
            {
                "chain_id": chain_id,
                "from_pokemon": from_pokemon,
                "to_pokemon": to_pokemon,
                "min_level": details.get("min_level"),
                "trigger": trigger,
                "fetched_at": fetched_at,
            }
        )

        walk(
            chain_id,
            child,
        )


# ===========================================
# Processa todas as evolution chains
# ===========================================

for row in rows:

    url = row.url

    print(f"Processando {url}")

    response = requests.get(url)

    if response.status_code != 200:

        print(f"Erro ao buscar {url}")

        continue

    data = response.json()

    walk(
        data["id"],
        data["chain"],
    )

# ===========================================
# Salva no BigQuery
# ===========================================

if len(records) == 0:

    print("Nenhuma evolution chain encontrada.")

    sys.exit(0)

df = pd.DataFrame(records)

job_config = bigquery.LoadJobConfig(
    write_disposition="WRITE_APPEND"
)

load_job = client.load_table_from_dataframe(
    df,
    f"{PROJECT_ID}.bronze.evolution_chains",
    job_config=job_config,
)

load_job.result()

if load_job.errors:

    print(load_job.errors)

    sys.exit(1)

print(f"{len(df)} relações de evolução inseridas com sucesso.")

