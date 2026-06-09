CREATE SCHEMA IF NOT EXISTS silver;

-- 1. SILVER.POKEMON_DETAILS
CREATE OR REPLACE TABLE silver.pokemon_details
PARTITION BY DATE(fetched_at)
AS
SELECT 
    pokemon_id,
    height,
    weight,
    base_experience,
    raw_json,
    fetched_at
FROM `bronze.pokemon_details`
QUALIFY ROW_NUMBER() OVER (PARTITION BY pokemon_id ORDER BY fetched_at DESC) = 1;

-- 2. SILVER.POKEMON_TYPES
CREATE OR REPLACE TABLE silver.pokemon_types
PARTITION BY DATE(fetched_at)
AS
SELECT 
    pokemon_id,
    type_name,
    slot,
    fetched_at
FROM `bronze.pokemon_types`
QUALIFY ROW_NUMBER() OVER (PARTITION BY pokemon_id, type_name ORDER BY fetched_at DESC) = 1;

-- 3. SILVER.POKEMON_STATS
CREATE OR REPLACE TABLE silver.pokemon_stats
PARTITION BY DATE(fetched_at)
AS
SELECT 
    pokemon_id,
    stat_name,
    base_stat,
    effort,
    fetched_at
FROM `bronze.pokemon_stats`
QUALIFY ROW_NUMBER() OVER (PARTITION BY pokemon_id, stat_name ORDER BY fetched_at DESC) = 1;

-- 4. SILVER.POKEMON_ABILITIES
CREATE OR REPLACE TABLE silver.pokemon_abilities
PARTITION BY DATE(fetched_at)
AS
SELECT 
    pokemon_id,
    ability_name,
    is_hidden,
    slot,
    fetched_at
FROM `bronze.pokemon_abilities`
QUALIFY ROW_NUMBER() OVER (PARTITION BY pokemon_id, ability_name ORDER BY fetched_at DESC) = 1;

-- 5. SILVER.POKEMON_MOVES
CREATE OR REPLACE TABLE silver.pokemon_moves
PARTITION BY DATE(fetched_at)
AS
SELECT 
    pokemon_id,
    move_name,
    learn_method,
    level_learned_at,
    fetched_at
FROM `bronze.pokemon_moves`
QUALIFY ROW_NUMBER() OVER (PARTITION BY pokemon_id, move_name, learn_method, level_learned_at ORDER BY fetched_at DESC) = 1;

-- 6. SILVER.POKEMON_SPECIES
CREATE OR REPLACE TABLE silver.pokemon_species
PARTITION BY DATE(fetched_at)
AS
SELECT 
    pokemon_id,
    species_name,
    evolution_chain_url,
    color,
    shape,
    habitat,
    generation,
    fetched_at
FROM `bronze.pokemon_species`
QUALIFY ROW_NUMBER() OVER (PARTITION BY pokemon_id ORDER BY fetched_at DESC) = 1;

-- 7. SILVER.EVOLUTION_CHAINS
CREATE OR REPLACE TABLE silver.evolution_chains
PARTITION BY DATE(fetched_at)
AS
SELECT 
    chain_id,
    from_pokemon,
    to_pokemon,
    min_level,
    trigger,
    fetched_at
FROM `bronze.evolution_chains`
-- Aqui a partição da regra de negócio olha para a chave da cadeia de evolução combinada com os pokemons envolvidos
QUALIFY ROW_NUMBER() OVER (PARTITION BY chain_id, from_pokemon, to_pokemon ORDER BY fetched_at DESC) = 1;

-- 8. SILVER.PKM_TYPE_RELATIONS (Tabela não-particionada, replicando a origem)
CREATE OR REPLACE TABLE silver.pkm_type_relations AS
SELECT 
    source,
    target,
    damage_multiplier,
    fetched_at
FROM `bronze.pkm_type_relations`
-- Como não possui pokemon_id, a unicidade se dá pela relação de tipos (Ex: Fire -> Water)
QUALIFY ROW_NUMBER() OVER (PARTITION BY source, target ORDER BY fetched_at DESC) = 1;
