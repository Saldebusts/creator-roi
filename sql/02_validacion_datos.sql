USE creator_roi;

-- Comprobar perfiles, categorías y ciudades
SELECT
    COUNT(*) AS total_perfiles,
    COUNT(DISTINCT Influencer_ID) AS perfiles_unicos,
    COUNT(DISTINCT Category) AS categorias,
    COUNT(DISTINCT City) AS ciudades
FROM creadores;

-- Confirmar que solo hay perfiles de Instagram
SELECT
    Platform,
    COUNT(*) AS total_perfiles
FROM creadores
GROUP BY Platform;

-- Revisar valores ausentes y precios no válidos
SELECT
    SUM(Followers IS NULL) AS seguidores_ausentes,
    SUM(Price_Per_Reel_EUR IS NULL) AS precios_ausentes,
    SUM(Price_Per_Reel_EUR <= 0) AS precios_no_validos
FROM creadores;

-- Comparar las tarifas con el análisis de Python
SELECT
    ROUND(MIN(Price_Per_Reel_EUR), 2) AS precio_minimo_eur,
    ROUND(AVG(Price_Per_Reel_EUR), 2) AS precio_medio_eur,
    ROUND(MAX(Price_Per_Reel_EUR), 2) AS precio_maximo_eur
FROM creadores;