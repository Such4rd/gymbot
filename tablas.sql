-- SQLite
-- Creación de la tabla usuarios
--CREATE TABLE usuarios (
--    id_user INTEGER PRIMARY KEY,
--    username TEXT,
--   nombre TEXT,
--    email TEXT
--);

-- Creación de la tabla grupos_musculares
CREATE TABLE IF NOT EXISTS grupos_musculares (
    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_grupo TEXT
);

-- Creación de la tabla ejercicios
CREATE TABLE IF NOT EXISTS ejercicios (
    id_ejercicio INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_ejercicio TEXT,
    id_grupo INTEGER,
    id_user INTEGER,
    date DATE,
    FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo)
);

-- Creación de la tabla entrenamientos
CREATE TABLE IF NOT EXISTS entrenamientos (
    id_entreno TEXT,
    id_user TEXT,
    date DATE,
    coment TEXT,
    PRIMARY KEY (id_entreno)
);

-- Creación de la tabla series
CREATE TABLE IF NOT EXISTS series (
    id_entreno TEXT,
    id_grupo INTEGER,
    id_ejercicio INTEGER,
    id_serie INTEGER,
    repes INTEGER,
    peso REAL,
    coment TEXT,
    PRIMARY KEY (id_entreno, id_grupo, id_ejercicio, id_serie),
    FOREIGN KEY (id_entreno) REFERENCES entrenamientos(id_entreno),
    FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo),
    FOREIGN KEY (id_ejercicio) REFERENCES ejercicios(id_ejercicio)
);