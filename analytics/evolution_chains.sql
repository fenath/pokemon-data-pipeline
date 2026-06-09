SELECT

    chain_id,

    STRING_AGG(
        species_name,
        ' -> '
        ORDER BY stage
    ) AS evolution_chain

FROM gold.pokemon_evolution

GROUP BY chain_id;
