CREATE SCHEMA IF NOT EXISTS gold;

CREATE OR REPLACE TABLE gold.pokemon_fraquezas AS
WITH types AS (
  SELECT distinct(source) AS source 
  FROM `silver.pkm_type_relations`
), base_dmg AS (
  SELECT a.pokemon_id, 
    a.type_name as pokemon_type, 
    b.source as attacker,
    COALESCE(c.damage_multiplier, 1.0) AS dmg_mult
  FROM `silver.pokemon_types` a
  CROSS JOIN types b
  LEFT JOIN `silver.pkm_type_relations` c 
    on (b.source = c.source AND a.type_name = c.target)
)
SELECT a.pokemon_id,
  attacker,
  -- Truque do LOG/EXP para multiplicar os valores de dmg_mult do tipo 1 e tipo 2
  CASE 
    WHEN MIN(dmg_mult) = 0.0 THEN 0.0
    ELSE ROUND(EXP(SUM(LN(NULLIF(dmg_mult, 0.0)))), 2)
  END AS final_damage_multiplier
  FROM base_dmg a
GROUP BY pokemon_id, attacker
ORDER BY pokemon_id, attacker;

CREATE OR REPLACE TABLE gold.pokemon_complete AS
WITH bst AS (
    SELECT
        pokemon_id,
        SUM(base_stat) AS bst
    FROM silver.pokemon_stats
    GROUP BY pokemon_id
),
types AS (
    SELECT
        pokemon_id,
        MAX(CASE
            WHEN slot = 1 THEN type_name
        END) AS primary_type,
        MAX(CASE
            WHEN slot = 2 THEN type_name
        END) AS secondary_type
    FROM silver.pokemon_types
    GROUP BY pokemon_id
)
SELECT
    s.pokemon_id,
    s.species_name,
    s.generation,
    s.color,
    s.shape,
    s.habitat,
    d.height,
    d.weight,
    d.base_experience,
    t.primary_type,
    t.secondary_type,
    b.bst
FROM silver.pokemon_species s
LEFT JOIN silver.pokemon_details d
ON s.pokemon_id = d.pokemon_id
LEFT JOIN bst b
ON s.pokemon_id = b.pokemon_id
LEFT JOIN types t
ON s.pokemon_id = t.pokemon_id;

CREATE OR REPLACE TABLE gold.pokemon_evolution AS
WITH RECURSIVE evolution_stage AS (
    -- Forma base
    SELECT
        ec.chain_id,
        ec.from_pokemon AS pokemon_id,
        0 AS stage
    FROM silver.evolution_chains ec
    WHERE ec.from_pokemon NOT IN (
        SELECT to_pokemon
        FROM silver.evolution_chains
        WHERE to_pokemon IS NOT NULL
    )
    UNION ALL
    -- Evoluções seguintes
    SELECT
        ec.chain_id,
        ec.to_pokemon,
        es.stage + 1
    FROM evolution_stage es
    JOIN silver.evolution_chains ec
      ON es.pokemon_id = ec.from_pokemon
)
SELECT
    es.chain_id,
    es.pokemon_id,
    ps.species_name,
    es.stage
FROM evolution_stage es
  LEFT JOIN silver.pokemon_species ps
    ON es.pokemon_id = ps.pokemon_id
ORDER BY
    chain_id,
    stage,
    pokemon_id;

CREATE OR REPLACE TABLE gold.pokemon_stats_pivot AS

SELECT

    ps.pokemon_id,

    pc.species_name,

    MAX(CASE
        WHEN stat_name = 'hp'
        THEN base_stat
    END) AS hp,

    MAX(CASE
        WHEN stat_name = 'attack'
        THEN base_stat
    END) AS attack,

    MAX(CASE
        WHEN stat_name = 'defense'
        THEN base_stat
    END) AS defense,

    MAX(CASE
        WHEN stat_name = 'special-attack'
        THEN base_stat
    END) AS special_attack,

    MAX(CASE
        WHEN stat_name = 'special-defense'
        THEN base_stat
    END) AS special_defense,

    MAX(CASE
        WHEN stat_name = 'speed'
        THEN base_stat
    END) AS speed,

    SUM(base_stat) AS bst

FROM silver.pokemon_stats ps

LEFT JOIN gold.pokemon_complete pc
    ON ps.pokemon_id = pc.pokemon_id

GROUP BY
    ps.pokemon_id,
    pc.species_name;
