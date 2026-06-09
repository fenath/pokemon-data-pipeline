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
        "http://localhost:8000/api/variables/GCP_PROJECT_CREDENTIALS/value"
        ).json()["value"]

PROJECT_ID = requests.get(
        "http://localhost:8000/api/variables/GCP_PROJECT_ID/value"
        ).json()["value"]

credentials = (
        service_account.Credentials
        .from_service_account_info(
            GCP
            )
        )

types = requests.get("https://pokeapi.co/api/v2/type?limit=50").json()
df = pd.DataFrame(types["results"])
con = duckdb.connect(":memory:")

df = con.sql("""
    SELECT UNNEST(df) FROM df
""").df()

client = bigquery.Client(project=PROJECT_ID, credentials=credentials)
job = client.query("""
    SELECT source from bronze.pkm_type_relations group by source 
""").result()

df_gcp = job.to_dataframe()


to_fetch = con.sql("""
    SELECT df.* 
    FROM df 
    WHERE 
        NOT EXISTS (
            SELECT 1 
            FROM df_gcp 
            WHERE df_gcp.source = df.name
        )
    LIMIT 5
""")

if to_fetch.to_df().empty:
    print("Todas as relações foram preenchidas")
    sys.exit()

now = datetime.datetime.now()
results = []
responses = {} # source : response
mult_labels = {
    "double_damage_to": 2.0,
    "half_damage_to": 0.5,
    "no_damage_to": 0.0
}

for idx, row in to_fetch.to_df().iterrows():
    responses[row["name"]] = requests.get(row["url"]).json()

for poke_type, resp in responses.items():
    has_relations = False
    for label, mult in mult_labels.items():
        for relation in resp["damage_relations"][label]:
            has_relations = True
            results.append({
                "source": poke_type,
                "target": relation["name"],
                "damage_multiplier": mult,
                "fetched_at": now,
            })
    # Previne looping infinito nas buscas
    # gera uma unica relação com target = 'none'
    if not has_relations:
        results.append({
                "source": poke_type,
                "target": 'none',
                "damage_multiplier": 1.0,
                "fetched_at": now,
            })


df_result = pd.DataFrame(results)
if df_result.empty:
    print("Resultado vazio, não será preciso enviar ao BigQuery")
    sys.exit()

try:
    print("Enviando dados para o BigQuery")
    job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND"
            )
    load_job = client.load_table_from_dataframe(
            df_result,
            f"{PROJECT_ID}.bronze.pkm_type_relations",
            job_config=job_config     
            )
    load_job.result()
    if load_job.errors:
        print(f"Erros ao enviar pkm_type_relations:")
        print(load_job.errors)
    print(f"Feito")
except Exception as e:
    print("Erro ao processar carregamento")
    print(e)
