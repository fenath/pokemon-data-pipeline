SELECT

    c.species_name,

    f.attacker

FROM gold.pokemon_fraquezas f

JOIN gold.pokemon_complete c

ON f.pokemon_id = c.pokemon_id

WHERE final_damage_multiplier = 4;
