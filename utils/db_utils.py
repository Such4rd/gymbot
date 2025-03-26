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


def crear_tabla_grupos_musculares():
    conexion = conectar_db()
    cursor = conexion.cursor()
    try:
        sql = '''
        CREATE TABLE IF NOT EXISTS grupos_musculares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_grupo TEXT NOT NULL
        )
        '''
        cursor.execute(sql)
        conexion.commit()
        logger.info("Tabla 'grupos_musculares' creada con éxito.")
    except sqlite3.Error as e:
        logger.error(f"Error al crear la tabla: {e}")
    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()       
def listar_tablas():
    conexion = None
    try:
        # Conectar a la base de datos
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        # Ejecutar la consulta para obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablas = cursor.fetchall()

        logger.info(f"Consulta ejecutada con éxito. Se obtuvieron {len(tablas)} tablas.")
        
        # Extraer y devolver una lista con los nombres de las tablas
        result = [tabla[0] for tabla in tablas]
        logger.info(f"Tablas encontradas: {result}")
        
        return result
    
    except Exception as e:
        logger.error(f"[!] Error al obtener las tablas: {e}")
        return []  # Retorna una lista vacía en caso de error
    finally:
        # Cerrar la conexión manualmente
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


def mejor_marca(grupo, ejercicio):
    """Devuelve el peso máximo y las repeticiones correspondientes para un ejercicio y grupo muscular a través de todos los entrenamientos."""
    conexion = None
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        
        # Consulta para obtener todas las series de un ejercicio y grupo muscular en todos los entrenamientos
        cursor.execute("""
            SELECT s.repes, s.peso
            FROM series s
            JOIN grupos_musculares gm ON s.id_grupo = gm.id_grupo
            JOIN ejercicios e ON s.id_ejercicio = e.id_ejercicio
            WHERE gm.nombre_grupo = ? AND e.nombre_ejercicio = ?
        """, (grupo, ejercicio))
        
        # Recuperamos todas las repeticiones y pesos de las series
        series = cursor.fetchall()
        
        # Si no hay registros, devolvemos None o un mensaje adecuado
        if not series:
            return None
        
        # Encontramos la mejor marca (peso máximo) y las repeticiones correspondientes
        mejor_serie = max(series, key=lambda x: x[1])  # max por el peso (segundo elemento)
        repes_maximas, mejor_peso = mejor_serie
        
        return repes_maximas, mejor_peso
    
    except Exception as e:
        print(f"[!] Error al obtener la mejor marca: {e}")
        return None
    
    finally:
        if conexion:
            conexion.close()