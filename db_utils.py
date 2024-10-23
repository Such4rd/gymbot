#En este archivo gestionaremos todo lo relacionado con base de datos
import sqlite3
import conexion as ruta
from datetime import datetime
from collections import defaultdict


# Conexión a la base de datos
def conectar_db():
    return sqlite3.connect(ruta.RUTA)


def inicializar_db(conexion):
    #crear tablas si no existen

    conexion.cursor().execute(
        '''
        CREATE TABLE IF NOT EXISTS grupos_musculares (
        id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_grupo TEXT
        )
        '''
    )

    #Creación de la tabla ejercicios
    conexion.cursor().execute(
        '''
        CREATE TABLE IF NOT EXISTS ejercicios (
        id_ejercicio INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_ejercicio TEXT,
        id_grupo INTEGER,
        id_user TEXT,
        date DATE,
        FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo)
    )
    '''
    )

    #Creación de la tabla entrenamientos
    conexion.cursor().execute(
        '''
        CREATE TABLE IF NOT EXISTS entrenamientos (
        id_entreno TEXT,
        id_user TEXT,
        date DATE,
        coment TEXT,
        PRIMARY KEY (id_entreno)
        )'''
    )

    #Creación de la tabla series
    conexion.cursor().execute(
        '''
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
        )
        '''
    )
#obtenemos grupos musculares
def obtener_grupos_musculares(conexion):
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre_grupo FROM grupos_musculares")
    grupos = cursor.fetchall()

    return [g[0] for g in grupos] 

def obtener_ejercicios_por_grupo(conexion,grupo):
    cursor = conexion.cursor()
    cursor.execute("SELECT nombre_ejercicio FROM ejercicios WHERE id_grupo = (SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?)", (grupo,))
    ejercicios = cursor.fetchall()

    return [e[0] for e in ejercicios]  # Devuelve solo los nombres


def generar_id_entreno(conexion,usuario):
    fecha = datetime.now().strftime('%d%m%Y')  # Formato DíaMesAño
    cursor = conexion.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM ENTRENAMIENTOS WHERE ID_USER = ?",(usuario,)
    )
    # Obtener el resultado de la query
    count = cursor.fetchone()[0]  # El resultado de COUNT(*) está en el primer (y único) elemento de la tupla
    # Cerrar cursor y conexión
    cursor.close()
    # Generar el ID en formato '04082024-usuario-#entreno'
    id_entreno = f"{fecha}-{usuario}-{count + 1}"  # Sumamos 1 para obtener el número de entreno siguiente
    
    return id_entreno

def insertar_ejercicio(conexion, ejercicio, grupo,user,date):
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?", (grupo,))
        result = cursor.fetchone()
        # Suponiendo que tienes una tabla 'grupos_musculares'
        cursor.execute("INSERT INTO ejercicios (nombre_ejercicio, id_grupo, id_user, date) VALUES (?, ?, ?, ?)", 
                    (ejercicio, result[0], user, date ))           
        conexion.commit()
    except:
        print("[!] Problema al insertar ejercicio")

def insertar_grupo(conexion, grupo):
    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO grupos_musculares (nombre_grupo) VALUES (?)", (grupo,))             
        conexion.commit()
    except:
        print("[!] Problema al insertar grupo")

def insertar_entreno(conexion, datos_entreno, user, fecha,id_entreno):

    try:
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO entrenamientos (id_entreno, id_user, date, coment) VALUES (?, ?, ?, ?)", 
                       (id_entreno, user, fecha, ''))

        # Insertar series en la tabla de series
        for registro in datos_entreno:
            grupo = registro['grupo']
            ejercicio = registro['ejercicio']
            for i, (repes, peso) in enumerate(registro['serie'],1):
                cursor.execute("""
                    INSERT INTO series (id_entreno, id_grupo, id_ejercicio, id_serie, repes, peso, coment)
                    VALUES (?, (SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?), 
                    (SELECT id_ejercicio FROM ejercicios WHERE nombre_ejercicio = ?), ?, ?, ?, '')
                """, (id_entreno, grupo, ejercicio, i, repes, peso))
        
        conexion.commit()
    
    except:
        print("[!] Problema al guardar entreno")



def grupo_existe(conexion, grupo):
    """Verifica si el grupo ya existe en la base de datos."""
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM grupos_musculares WHERE nombre_grupo = ?", (grupo,))
    return cursor.fetchone()[0] > 0

def ejercicio_existe(conexion, ejercicio):
    """Verifica si el ejercicio ya existe en la base de datos."""
    cursor = conexion.cursor()
    cursor.execute("SELECT COUNT(*) FROM ejercicios WHERE nombre_ejercicio = ?", (ejercicio,))
    return cursor.fetchone()[0] > 0
    

def obtener_entrenos(conexion, user):
    cursor = conexion.cursor()
    cursor.execute("SELECT id_entreno, date, coment  FROM entrenamientos WHERE id_user = ?", (user,))
    entrenos = cursor.fetchall()

    return [e for e in entrenos]

def load_entreno(conexion, id_entreno):
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT gm.nombre_grupo, e.nombre_ejercicio, s.repes, s.peso
        FROM series s
        JOIN grupos_musculares gm ON s.id_grupo = gm.id_grupo
        JOIN ejercicios e ON s.id_ejercicio = e.id_ejercicio
        WHERE s.id_entreno = ?
    """, (id_entreno,))
    
    
    entreno_bd = cursor.fetchall()

    # Crear un diccionario para agrupar por 'grupo' y 'ejercicio'
    agrupados = defaultdict(lambda: {'grupo': '', 'ejercicio': '', 'serie': []})

# Recorrer los registros para agruparlos
    for grupo, ejercicio, serie, peso in entreno_bd:
        key = (grupo, ejercicio)  # Llave para identificar un grupo/ejercicio
        if agrupados[key]['grupo'] == '':  # Si no existe el grupo/ejercicio, inicializamos
            agrupados[key]['grupo'] = grupo
            agrupados[key]['ejercicio'] = ejercicio
        # Añadir la serie y el peso a la lista
        agrupados[key]['serie'].append((str(serie), str(peso)))

# Convertir a una lista de diccionarios
    resultado = list(agrupados.values())
    
    return resultado
