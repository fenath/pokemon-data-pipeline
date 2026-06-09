SELECT *

FROM (

    SELECT

        species_name,

        generation,

        bst,

        ROW_NUMBER() OVER (

            PARTITION BY generation

            ORDER BY bst DESC

        ) AS rn

    FROM gold.pokemon_complete

)

WHERE rn <= 5;
