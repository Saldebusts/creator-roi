-- Base de datos del proyecto CreatorROI
CREATE DATABASE IF NOT EXISTS creator_roi
CHARACTER SET utf8mb4;

-- Seleccionar la base de datos
USE creator_roi;

-- Una fila por creador de Instagram
CREATE TABLE IF NOT EXISTS creadores (
    Influencer_ID VARCHAR(20) PRIMARY KEY,
    Influencer_Name VARCHAR(255),
    Platform VARCHAR(30),
    Category VARCHAR(100),
    City VARCHAR(100),
    Language VARCHAR(50),
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
    Available_For_Collaboration VARCHAR(10),
    Price_Per_Reel_EUR DECIMAL(15, 6),
    Price_Per_Story_EUR DECIMAL(15, 6)
);

-- Comprobar la estructura
DESCRIBE creadores;

-- Comprobar cuántos perfiles se han importado
SELECT COUNT(*) AS total_perfiles
FROM creator_roi.creadores;