USE creator_roi;

-- Comparar la oferta de perfiles y las tarifas por categoría
SELECT
    Category AS categoria,
    COUNT(*) AS numero_perfiles,
    ROUND(AVG(Followers), 0) AS seguidores_medios,
    ROUND(AVG(Average_Views_Per_Content), 0) AS visualizaciones_medias,
    ROUND(AVG(Engagement_Rate_Percent), 2) AS engagement_medio_pct,
    ROUND(AVG(Price_Per_Reel_EUR), 2) AS precio_medio_reel_eur
FROM creadores
GROUP BY Category
ORDER BY numero_perfiles DESC;

-- Comparar categorías dentro de cada grupo de seguidores
SELECT
    Category AS categoria,
    CASE
        WHEN Followers <= 100000 THEN 'Hasta 100.000'
        WHEN Followers <= 1000000 THEN '100.001 a 1 millón'
        ELSE 'Más de 1 millón'
    END AS grupo_seguidores,
    COUNT(*) AS numero_perfiles,
    ROUND(AVG(Followers), 0) AS seguidores_medios,
    ROUND(AVG(Average_Views_Per_Content), 0) AS visualizaciones_medias,
    ROUND(AVG(Price_Per_Reel_EUR), 2) AS precio_medio_reel_eur
FROM creadores
GROUP BY Category, grupo_seguidores
ORDER BY Category, MIN(Followers);

-- Selección inicial para una campaña de belleza
-- Presupuesto máximo por creador: 300 € por reel
SELECT
    Influencer_ID,
    Influencer_Name AS creador,
    City AS ciudad,
    Language AS idioma,
    Followers AS seguidores,
    Average_Views_Per_Content AS visualizaciones_medias,
    Engagement_Rate_Percent AS engagement_pct,
    ROUND(Price_Per_Reel_EUR, 2) AS precio_reel_eur
FROM creadores
WHERE Category = 'Beauty'
    AND Followers BETWEEN 10000 AND 100000
    AND Price_Per_Reel_EUR <= 300
ORDER BY Average_Views_Per_Content DESC, Influencer_ID
LIMIT 20;

-- Tamaño de la selección y rango de tarifas
SELECT
    COUNT(*) AS candidatos_disponibles_en_dataset,
    ROUND(MIN(Price_Per_Reel_EUR), 2) AS tarifa_minima_eur,
    ROUND(AVG(Price_Per_Reel_EUR), 2) AS tarifa_media_eur,
    ROUND(MAX(Price_Per_Reel_EUR), 2) AS tarifa_maxima_eur
FROM creadores
WHERE Category = 'Beauty'
    AND Followers BETWEEN 10000 AND 100000
    AND Price_Per_Reel_EUR <= 300;