import requests
import json
from datetime import datetime

import pandas as pd
import duckdb
from google.cloud import bigquery
from google.oauth2 import service_account

from local_lambda.helpers import ParamParser

params = ParamParser()

PROJECT_ID = params.get("GCP_PROJECT_ID")
DATASET_ID = 'bronze'
TABLE_ID = 'pokemon_skills'

FULL_TABLE_ID = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

credentials = (
        service_account.Credentials
        .from_service_account_info(
                params.get_json("GCP_PROJECT_CREDENTIALS")
            )
        )
client = bigquery.Client(project=PROJECT_ID, credentials=credentials)

query_job = client.query("""
             SELECT url
             FROM bronze.pokemons p
             WHERE (
               -- Checa se o Pokémon está faltando em QUALQUER uma das tabelas de destino
               NOT EXISTS (SELECT 1 FROM bronze.pokemon_details d WHERE d.pokemon_id = p.id)
               OR NOT EXISTS (SELECT 1 FROM bronze.pokemon_types t WHERE t.pokemon_id = p.id)
               OR NOT EXISTS (SELECT 1 FROM bronze.pokemon_stats s WHERE s.pokemon_id = p.id)
               OR NOT EXISTS (SELECT 1 FROM bronze.pokemon_abilities a WHERE a.pokemon_id = p.id)
               OR NOT EXISTS (SELECT 1 FROM bronze.pokemon_moves m WHERE m.pokemon_id = p.id)
             )
             -- Garante que estamos pegando a URL mais recente de cada Pokémon na tabela bronze
             QUALIFY ROW_NUMBER() OVER (PARTITION BY p.id ORDER BY p.fetched_at DESC) = 1
             LIMIT 5
             """).result()

print(query_job)

to_append = []
types_to_append = []
stats_to_append = []
abilities_to_append = []
moves_to_append = []
now = datetime.now()

def parse_moves(list_append: list, response, now):
    df_res = pd.DataFrame([response])
    with duckdb.connect() as con:
        df = con.sql("""
            SELECT id AS pokemon_id, 
              m.move.name AS move_name,
              details.move_learn_method.name AS learn_method,
              details.level_learned_at AS level_learned_at
            FROM df_res,
              UNNEST(moves) AS t1(m),
              UNNEST(m.version_group_details) AS t2(details)
                     """).df()
        for _, row in df.iterrows():
            list_append.append({ **row.to_dict(), "fetched_at": now })

print("Buscando informacoes na API")
for row in query_job:
    res = requests.get(row.url)
    res = res.json()
    types = res.get("types")
    stats = res.get("stats")
    abilities = res.get("abilities")
    moves = res.get("moves")
    to_append.append({
        "pokemon_id": res.get("id"),
        "height": res.get("height"),
        "weight": res.get("weight"),
        "base_experience": res.get("base_experience"),
        "raw_json": json.dumps(res),
        "fetched_at": now
        })
    for tp in types:
        types_to_append.append({
            "pokemon_id": res.get("id"),
            "type_name": tp.get("type").get("name"),
            "slot": tp.get("slot"),
            "fetched_at": now,
            })
    for st in stats:
        stats_to_append.append({
            "pokemon_id": res.get("id"),
            "stat_name": st.get("stat").get("name"),
            "base_stat": st.get("base_stat"),
            "effort": st.get("effort"),
            "fetched_at": now,
            })
    for ab in abilities:
        abilities_to_append.append({
            "pokemon_id": res.get("id"),
            "ability_name": ab.get("ability").get("name"),
            "is_hidden": ab.get("is_hidden"),
            "slot": ab.get("slot"),
            "fetched_at": now,
            })
    parse_moves(moves_to_append, res, now)

job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
        )
for tbl, rows in {
        "pokemon_details": to_append,
        "pokemon_types": types_to_append,
        "pokemon_stats": stats_to_append,
        "pokemon_abilities": abilities_to_append,
        "pokemon_moves": moves_to_append
        }.items():

    try:
        print(f"adicionando {len(rows)} resultados em {tbl}")
        load_job = client.load_table_from_dataframe(
                pd.DataFrame(rows),
                f"{PROJECT_ID}.bronze.{tbl}",
                job_config=job_config
                )
        load_job.result()
        if load_job.errors:
            print(f"Erros ao enviar {tbl}:")
            print(load_job.errors)
            break
        print(f"Feito")
    except Exception as e:
        print("Erro ao processar carregamento")
        print(f"Tabela: {tbl}")
        print(e)

print("Detalhes adicionados com sucesso!")

