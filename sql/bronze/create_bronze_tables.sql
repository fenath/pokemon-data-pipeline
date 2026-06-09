CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.pokemon_details (
    pokemon_id INT64,
    height INT64,
    weight INT64,
    base_experience INT64,
    raw_json STRING,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.pokemon_types (
    pokemon_id INT64,
    type_name STRING,
    slot INT64,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.pokemon_stats (
    pokemon_id INT64,
    stat_name STRING,
    base_stat INT64,
    effort INT64,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.pokemon_abilities (
    pokemon_id INT64,
    ability_name STRING,
    is_hidden BOOLEAN,
    slot INT64,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.pokemon_moves (
    pokemon_id INT64,
    move_name STRING,
    learn_method STRING,
    level_learned_at INT64,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.pokemon_species (
    pokemon_id INT64,
    species_name STRING,
    evolution_chain_url STRING,
    color STRING,
    shape STRING,
    habitat STRING,
    generation STRING,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.evolution_chains (
    chain_id INT64,
    from_pokemon INT64,
    to_pokemon INT64,
    min_level INT64,
    trigger STRING,
    fetched_at TIMESTAMP
)
PARTITION BY DATE(fetched_at);

CREATE TABLE IF NOT EXISTS bronze.pkm_type_relations (
    source STRING,
    target STRING,
    damage_multiplier FLOAT64,
    fetched_at TIMESTAMP
);

