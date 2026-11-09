USE creator_roi;

-- Cada categoría tendrá un identificador único
CREATE TABLE categorias (
    categoria_id INT AUTO_INCREMENT PRIMARY KEY,
    categoria VARCHAR(100) NOT NULL UNIQUE
);

-- Cada ciudad tendrá un identificador único
CREATE TABLE ciudades (
    ciudad_id INT AUTO_INCREMENT PRIMARY KEY,
    ciudad VARCHAR(100) NOT NULL UNIQUE
);

-- Cada idioma tendrá un identificador único
CREATE TABLE idiomas (
    idioma_id INT AUTO_INCREMENT PRIMARY KEY,
    idioma VARCHAR(50) NOT NULL UNIQUE
);

-- Cargar cada categoría una sola vez
INSERT INTO categorias (categoria)
SELECT DISTINCT Category
FROM creadores
ORDER BY Category;

-- Cargar cada ciudad una sola vez
INSERT INTO ciudades (ciudad)
SELECT DISTINCT City
FROM creadores
ORDER BY City;

-- Cargar cada idioma una sola vez
INSERT INTO idiomas (idioma)
SELECT DISTINCT Language
FROM creadores
ORDER BY Language;


SELECT 'Categorías' AS tabla, COUNT(*) AS total
FROM categorias

UNION ALL

SELECT 'Ciudades', COUNT(*)
FROM ciudades

UNION ALL

SELECT 'Idiomas', COUNT(*)
FROM idiomas;

-- Tabla principal de perfiles
CREATE TABLE perfiles (
    Influencer_ID VARCHAR(20) PRIMARY KEY,
    Influencer_Name VARCHAR(255),

    categoria_id INT NOT NULL,
    ciudad_id INT NOT NULL,
    idioma_id INT NOT NULL,

    Followers INT,
    Average_Likes INT,
    Average_Comments INT,
    Average_Shares INT,
    Average_Saves INT,
    Number_of_Posts_Analyzed INT,
    Average_Views_Per_Content BIGINT,
    Engagement_Rate_Percent DECIMAL(8, 4),

    Price_Per_Reel_INR BIGINT,
    Price_Per_Story_INR BIGINT,
    Price_Per_Reel_EUR DECIMAL(15, 6),
    Price_Per_Story_EUR DECIMAL(15, 6),

    FOREIGN KEY (categoria_id)
        REFERENCES categorias(categoria_id),

    FOREIGN KEY (ciudad_id)
        REFERENCES ciudades(ciudad_id),

    FOREIGN KEY (idioma_id)
        REFERENCES idiomas(idioma_id)
);

-- Revisar las columnas de la nueva tabla
DESCRIBE perfiles;


-- Cargar los perfiles con los identificadores de sus categorías,
-- ciudades e idiomas
INSERT INTO perfiles (
    Influencer_ID,
    Influencer_Name,
    categoria_id,
    ciudad_id,
    idioma_id,
    Followers,
    Average_Likes,
    Average_Comments,
    Average_Shares,
    Average_Saves,
    Number_of_Posts_Analyzed,
    Average_Views_Per_Content,
    Engagement_Rate_Percent,
    Price_Per_Reel_INR,
    Price_Per_Story_INR,
    Price_Per_Reel_EUR,
    Price_Per_Story_EUR
)
SELECT
    c.Influencer_ID,
    c.Influencer_Name,
    cat.categoria_id,
    ci.ciudad_id,
    i.idioma_id,
    c.Followers,
    c.Average_Likes,
    c.Average_Comments,
    c.Average_Shares,
    c.Average_Saves,
    c.Number_of_Posts_Analyzed,
    c.Average_Views_Per_Content,
    c.Engagement_Rate_Percent,
    c.Price_Per_Reel_INR,
    c.Price_Per_Story_INR,
    c.Price_Per_Reel_EUR,
    c.Price_Per_Story_EUR
FROM creadores AS c
INNER JOIN categorias AS cat
    ON c.Category = cat.categoria
INNER JOIN ciudades AS ci
    ON c.City = ci.ciudad
INNER JOIN idiomas AS i
    ON c.Language = i.idioma;

    
-- Confirmar que se han cargado todos los perfiles
SELECT COUNT(*) AS total_perfiles
FROM perfiles;

-- Recuperar los nombres mediante las relaciones
SELECT
    p.Influencer_ID,
    p.Influencer_Name AS creador,
    cat.categoria,
    ci.ciudad,
    i.idioma,
    ROUND(p.Price_Per_Reel_EUR, 2) AS precio_reel_eur
FROM perfiles AS p
INNER JOIN categorias AS cat
    ON p.categoria_id = cat.categoria_id
INNER JOIN ciudades AS ci
    ON p.ciudad_id = ci.ciudad_id
INNER JOIN idiomas AS i
    ON p.idioma_id = i.idioma_id
ORDER BY p.Influencer_ID
LIMIT 5;

-- Comprobar el caso comercial con las tablas relacionadas
SELECT
    COUNT(*) AS perfiles_que_cumplen_filtros,
    ROUND(MIN(p.Price_Per_Reel_EUR), 2) AS tarifa_minima_eur,
    ROUND(AVG(p.Price_Per_Reel_EUR), 2) AS tarifa_media_eur,
    ROUND(MAX(p.Price_Per_Reel_EUR), 2) AS tarifa_maxima_eur
FROM perfiles AS p
INNER JOIN categorias AS cat
    ON p.categoria_id = cat.categoria_id
WHERE cat.categoria = 'Beauty'
    AND p.Followers BETWEEN 10000 AND 100000
    AND p.Price_Per_Reel_EUR <= 300;