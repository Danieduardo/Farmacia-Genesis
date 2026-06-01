"""
Pool de conexiones MySQL para Farmacia Génesis.
"""
# pyrefly: ignore [missing-import]
import mysql.connector
# pyrefly: ignore [missing-import]
from mysql.connector import pooling, Error
from app.config import DB_CONFIG


class DatabaseConnection:
    """Maneja un pool de conexiones reutilizables a MySQL."""

    _pool = None

    @classmethod
    def initialize_pool(cls):
        """Crea el pool de conexiones. Llamar una sola vez al inicio."""
        if cls._pool is None:
            try:
                cls._pool = pooling.MySQLConnectionPool(**DB_CONFIG)
                print("[DB] Pool de conexiones creado exitosamente.")
            except Error as e:
                print(f"[DB] Error al crear pool: {e}")
                raise

    @classmethod
    def get_connection(cls):
        """Obtiene una conexión del pool."""
        if cls._pool is None:
            cls.initialize_pool()
        try:
            conn = cls._pool.get_connection()
            return conn
        except Error as e:
            print(f"[DB] Error al obtener conexión: {e}")
            raise

    @classmethod
    def execute_query(cls, query, params=None, fetch_one=False, fetch_all=False):
        """
        Ejecuta una query y opcionalmente retorna resultados.

        Args:
            query: SQL a ejecutar
            params: Parámetros para la query (tupla)
            fetch_one: Si True, retorna un solo resultado
            fetch_all: Si True, retorna todos los resultados

        Returns:
            Resultado(s) si fetch_one/fetch_all, o lastrowid para INSERT
        """
        conn = None
        cursor = None
        try:
            conn = cls.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params)

            if fetch_one:
                result = cursor.fetchone()
                return result
            elif fetch_all:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.lastrowid

        except Error as e:
            if conn:
                conn.rollback()
            print(f"[DB] Error en query: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    @classmethod
    def test_connection(cls):
        """Prueba la conexión a la base de datos."""
        try:
            conn = cls.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            cursor.close()
            conn.close()
            return True, "Conexión exitosa"
        except Error as e:
            return False, str(e)
