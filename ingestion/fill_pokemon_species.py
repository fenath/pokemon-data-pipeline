import sys
import json
import os
import datetime

from google.oauth2 import service_account
from google.cloud import bigquery
import duckdb
import pandas as pd
import requests

from local_lambda.helpers import ParamParser

GCP = requests.get(
        "http://localhost:8004/api/variables/GCP_PROJECT_CREDENTIALS/value"
        ).json()["value"]

PROJECT_ID = requests.get(
        "http://localhost:8004/api/variables/GCP_PROJECT_ID/value"
        ).json()["value"]

credentials = (
        service_account.Credentials
        .from_service_account_info(
            GCP
            )
        )
client = bigquery.Client(project=PROJECT_ID, credentials=credentials)

query_job = client.query("""
             SELECT id
             FROM bronze.pokemons p
             WHERE (
               NOT EXISTS (SELECT 1 FROM bronze.pokemon_species d 
               WHERE d.pokemon_id = p.id)
             )
             -- Garante que estamos pegando a URL mais recente de cada Pokémon na tabela bronze
             QUALIFY ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY p.fetched_at DESC) = 1
             LIMIT 5
             """).result()

print(query_job)
now = datetime.datetime.now()
species_url = lambda id: f"https://pokeapi.co/api/v2/pokemon-species/{id}"
responses = {
        row.id:
        requests.get(species_url(row.id)).json()
        for row in query_job
        }

df = (
        pd.DataFrame([{
            "pokemon_id": id,
            "species_name": res['name'],
            "evolution_chain_url": res['evolution_chain']['url'],
            "color": res['color']['name'],
            "shape": res['shape']['name'],
            "habitat": res.get('habitat', {}).get('name', ''),
            "generation": res['generation']['name'],
            "fetched_at": now
            }
            for id, res in responses.items()
            ])
        )

job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
        )

try:
    print(f"adicionando {len(df)} resultados em bronze.pokemon_species")
    load_job = client.load_table_from_dataframe(
            df,
            f"{PROJECT_ID}.bronze.pokemon_species",
            job_config=job_config
            )
    load_job.result()
    if load_job.errors:
        print(f"Erros ao enviar pokemon_species:")
        print(load_job.errors)
        sys.exit(1)
    print(f"Feito")
except Exception as e:
    print("Erro ao processar carregamento")
    print(f"Tabela: pokemon_species")
    print(e)

print("Detalhes adicionados com sucesso!")
