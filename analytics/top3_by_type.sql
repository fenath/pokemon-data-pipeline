SELECT *

FROM (

    SELECT

        species_name,

        primary_type,

        bst,

        DENSE_RANK() OVER (

            PARTITION BY primary_type

            ORDER BY bst DESC

        ) AS ranking

    FROM gold.pokemon_complete

)

WHERE ranking <= 3;
