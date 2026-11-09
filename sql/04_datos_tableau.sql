USE creator_roi;

-- Datos para Tableau utilizando las tablas relacionadas
SELECT
    p.Influencer_ID AS id_creador,
    p.Influencer_Name AS creador,
    cat.categoria,
    ci.ciudad,
    i.idioma,
    p.Followers AS seguidores,
    CASE
        WHEN p.Followers <= 100000 THEN 'Hasta 100.000'
        WHEN p.Followers <= 1000000 THEN '100.001 a 1 millón'
        ELSE 'Más de 1 millón'
    END AS grupo_seguidores,
    p.Average_Views_Per_Content AS visualizaciones_medias,
    p.Engagement_Rate_Percent AS engagement_pct,
    p.Price_Per_Reel_EUR AS precio_reel_eur
FROM perfiles AS p
INNER JOIN categorias AS cat
    ON p.categoria_id = cat.categoria_id
INNER JOIN ciudades AS ci
    ON p.ciudad_id = ci.ciudad_id
INNER JOIN idiomas AS i
    ON p.idioma_id = i.idioma_id
ORDER BY p.Influencer_ID;