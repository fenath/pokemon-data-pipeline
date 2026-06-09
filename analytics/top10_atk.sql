SELECT
    species_name,
    attack
FROM gold.pokemon_stats_pivot
ORDER BY attack DESC
LIMIT 10;
