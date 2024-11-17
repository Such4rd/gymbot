#En este archivo gestionaremos todo lo relacionado con base de datos
import sqlite3
from  .database import RUTA
from datetime import datetime
from collections import defaultdict
import os
import logging

# Configurar logger
logger = logging.getLogger(__name__)

def conectar_db():

    
    try:
        logger.info("Conectando a la base de datos...")
        conexion = sqlite3.connect(RUTA)
        logger.info("Conexión exitosa a la base de datos.")
        return conexion
    except Exception as e:
        logger.error(f"Error al conectar a la base de datos: {e}")
        raise  # Lanza el error para que sea manejado más arriba)
"""
def inicializar_db():
    # Crear tablas si no existen
    try:
        # Usamos 'with' para manejar automáticamente el cursor
        with conectar_db().cursor() as cursor:
            # Creación de la tabla grupos_musculares
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS grupos_musculares (
                    id_grupo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_grupo TEXT
                )
            ''')

            # Creación de la tabla ejercicios
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ejercicios (
                    id_ejercicio INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre_ejercicio TEXT,
                    id_grupo INTEGER,
                    id_user TEXT,
                    date DATE,
                    FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo)
                )
            ''')

            # Creación de la tabla entrenamientos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS entrenamientos (
                    id_entreno TEXT,
                    id_user TEXT,
                    date DATE,
                    coment TEXT,
                    PRIMARY KEY (id_entreno)
                )
            ''')

            # Creación de la tabla series
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS series (
                    id_entreno TEXT,
                    id_grupo INTEGER,
                    id_ejercicio INTEGER,
                    id_serie INTEGER,
                    repes INTEGER,
                    peso REAL,
                    coment TEXT,
                    PRIMARY KEY (id_entreno, uid_grupo, id_ejercicio, id_serie),
                    FOREIGN KEY (id_entreno) REFERENCES entrenamientos(id_entreno),
                    FOREIGN KEY (id_grupo) REFERENCES grupos_musculares(id_grupo),
                    FOREIGN KEY (id_ejercicio) REFERENCES ejercicios(id_ejercicio)
                )
            ''')

        print("Base de datos inicializada correctamente.")

    except Exception as e:
        print(f"[!] Error al inicializar la base de datos: {e}")
#obtenemos grupos musculares

"""

def obtener_grupos_musculares():
    conexion = None
    try:
        # Conectar a la base de datos
        conexion = conectar_db()
        cursor = conexion.cursor()  # Crear el cursor manualmente

        logger.info("Conexión y cursor obtenidos con éxito.")
        
        # Ejecutar la consulta
        cursor.execute("SELECT nombre_grupo FROM grupos_musculares")
        grupos = cursor.fetchall()

        logger.info(f"Consulta ejecutada con éxito. Se obtuvieron {len(grupos)} grupos musculares.")
        
        # Extraer y devolver una lista de los nombres de los grupos musculares
        result = [g[0] for g in grupos]
        logger.info(f"Grupos musculares retornados: {result}")
        
        return result
    
    except Exception as e:
        logger.error(f"[!] Error al obtener grupos musculares: {e}")
        return []  # Retorna una lista vacía en caso de error
    finally:
        # Cerrar el cursor y la conexión manualmente
        if conexion:
            conexion.close()
          
          
def obtener_ejercicios_por_grupo(grupo):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT nombre_ejercicio FROM ejercicios WHERE id_grupo = (SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?)", (grupo,))
        ejercicios = cursor.fetchall()
        
        return [e[0] for e in ejercicios]
    
    except Exception as e:
        print(f"[!] Error al obtener ejercicios: {e}")
        return []
    
    finally:
        if conexion:
            conexion.close()


def generar_id_entreno(usuario):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        fecha = datetime.now().strftime('%d%m%Y')
        cursor.execute("SELECT COUNT(*) FROM entrenamientos WHERE id_user = ?", (usuario,))
        count = cursor.fetchone()[0]
        
        return f"{fecha}-{usuario}-{count + 1}"
    
    except Exception as e:
        print(f"[!] Error al generar ID de entrenamiento: {e}")
        return ""
    
    finally:
        if conexion:
            conexion.close()


def insertar_ejercicio(ejercicio, grupo, user, date):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?", (grupo,))
        result = cursor.fetchone()
        
        cursor.execute("INSERT INTO ejercicios (nombre_ejercicio, id_grupo, id_user, date) VALUES (?, ?, ?, ?)", 
                       (ejercicio, result[0], user, date))
        conexion.commit()
    
    except Exception as e:
        print(f"[!] Problema al insertar ejercicio: {e}")
    
    finally:
        if conexion:
            conexion.close()


def insertar_grupo(grupo):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("INSERT INTO grupos_musculares (nombre_grupo) VALUES (?)", (grupo,))
        conexion.commit()
    
    except Exception as e:
        print(f"[!] Problema al insertar grupo: {e}")
    
    finally:
        if conexion:
            conexion.close()


def insertar_entreno(datos_entreno, user, fecha, id_entreno):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("INSERT INTO entrenamientos (id_entreno, id_user, date, coment) VALUES (?, ?, ?, ?)", 
                       (id_entreno, user, fecha, ''))
        
        for registro in datos_entreno:
            grupo = registro['grupo']
            ejercicio = registro['ejercicio']
            for i, (repes, peso, coment) in enumerate(registro['serie'], 1):
                cursor.execute("""
                    INSERT INTO series (id_entreno, id_grupo, id_ejercicio, id_serie, repes, peso, coment)
                    VALUES (?, (SELECT id_grupo FROM grupos_musculares WHERE nombre_grupo = ?), 
                    (SELECT id_ejercicio FROM ejercicios WHERE nombre_ejercicio = ?), ?, ?, ?, ?)
                """, (id_entreno, grupo, ejercicio, i, repes, peso, coment))
        
        conexion.commit()
    
    except Exception as e:
        print(f"[!] Problema al guardar entrenamiento: {e}")
    
    finally:
        if conexion:
            conexion.close()


def grupo_existe(grupo):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM grupos_musculares WHERE nombre_grupo = ?", (grupo,))
        return cursor.fetchone()[0] > 0
    
    except Exception as e:
        print(f"[!] Error al verificar existencia de grupo: {e}")
        return False
    
    finally:
        if conexion:
            conexion.close()


def ejercicio_existe(ejercicio):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM ejercicios WHERE nombre_ejercicio = ?", (ejercicio,))
        return cursor.fetchone()[0] > 0
    
    except Exception as e:
        print(f"[!] Error al verificar existencia de ejercicio: {e}")
        return False
    
    finally:
        if conexion:
            conexion.close()


def obtener_entrenos(user):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("SELECT id_entreno, date, coment FROM entrenamientos WHERE id_user = ?", (user,))
        entrenos = cursor.fetchall()
        
        return [e for e in entrenos]
    
    except Exception as e:
        print(f"[!] Error al obtener entrenos: {e}")
        return []
    
    finally:
        if conexion:
            conexion.close()


def load_entreno(id_entreno):
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        cursor.execute("""
            SELECT gm.nombre_grupo, e.nombre_ejercicio, s.repes, s.peso, s.coment
            FROM series s
            JOIN grupos_musculares gm ON s.id_grupo = gm.id_grupo
            JOIN ejercicios e ON s.id_ejercicio = e.id_ejercicio
            WHERE s.id_entreno = ?
        """, (id_entreno,))
        
        entreno_bd = cursor.fetchall()
        agrupados = defaultdict(lambda: {'grupo': '', 'ejercicio': '', 'serie': []})
        
        for grupo, ejercicio, serie, peso, coment in entreno_bd:
            key = (grupo, ejercicio)
            if agrupados[key]['grupo'] == '':
                agrupados[key]['grupo'] = grupo
                agrupados[key]['ejercicio'] = ejercicio
            agrupados[key]['serie'].append((str(serie), str(peso), str(coment)))
        
        return list(agrupados.values())
    
    except Exception as e:
        print(f"[!] Error al cargar el entrenamiento: {e}")
        return []
    
    finally:
        if conexion:
            conexion.close()


