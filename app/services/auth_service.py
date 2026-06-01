"""
Servicio de autenticación para Farmacia Génesis.
Maneja login, hashing de contraseñas y gestión de usuarios.
"""
import bcrypt
from datetime import datetime
from app.database.connection import DatabaseConnection


class AuthService:
    """Servicio de autenticación con bcrypt."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Genera un hash bcrypt de la contraseña."""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica una contraseña contra su hash."""
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                password_hash.encode('utf-8')
            )
        except Exception:
            return False

    @classmethod
    def login(cls, username: str, password: str) -> dict | None:
        """
        Intenta autenticar al usuario.

        Returns:
            dict con datos del usuario si es exitoso, None si falla.
        """
        query = """
            SELECT u.id_usuario, u.nombre_usuario, u.password_hash,
                   u.rol, u.nombre_completo, u.activo, u.id_medico
            FROM usuarios u
            WHERE u.nombre_usuario = %s
        """
        user = DatabaseConnection.execute_query(query, (username,), fetch_one=True)

        if user is None:
            return None

        if not user['activo']:
            return None

        if not cls.verify_password(password, user['password_hash']):
            return None

        # Actualizar último acceso
        update_query = """
            UPDATE usuarios SET ultimo_acceso = %s WHERE id_usuario = %s
        """
        DatabaseConnection.execute_query(
            update_query, (datetime.now(), user['id_usuario'])
        )

        # No retornar el hash
        del user['password_hash']
        return user

    @classmethod
    def create_user(cls, nombre_usuario: str, password: str, rol: str,
                    nombre_completo: str, id_medico: int = None) -> int:
        """Crea un nuevo usuario en el sistema."""
        password_hash = cls.hash_password(password)
        query = """
            INSERT INTO usuarios (nombre_usuario, password_hash, rol,
                                  nombre_completo, activo, id_medico)
            VALUES (%s, %s, %s, %s, 1, %s)
        """
        return DatabaseConnection.execute_query(
            query, (nombre_usuario, password_hash, rol, nombre_completo, id_medico)
        )

    @classmethod
    def ensure_admin_exists(cls):
        """
        Verifica que exista al menos un usuario admin.
        Si no existe, crea uno con credenciales por defecto.
        """
        query = "SELECT COUNT(*) as total FROM usuarios WHERE rol = 'admin'"
        result = DatabaseConnection.execute_query(query, fetch_one=True)

        if result and result['total'] == 0:
            cls.create_user(
                nombre_usuario="admin",
                password="admin123",
                rol="admin",
                nombre_completo="Administrador del Sistema"
            )
            print("[AUTH] Usuario admin creado: admin / admin123")
            return True
        return False

    @classmethod
    def change_password(cls, user_id: int, new_password: str):
        """Cambia la contraseña de un usuario."""
        password_hash = cls.hash_password(new_password)
        query = "UPDATE usuarios SET password_hash = %s WHERE id_usuario = %s"
        DatabaseConnection.execute_query(query, (password_hash, user_id))

    @classmethod
    def get_all_users(cls) -> list:
        """Obtiene todos los usuarios (sin hash)."""
        query = """
            SELECT id_usuario, nombre_usuario, rol, nombre_completo,
                   activo, id_medico, fecha_creacion, ultimo_acceso
            FROM usuarios ORDER BY fecha_creacion DESC
        """
        return DatabaseConnection.execute_query(query, fetch_all=True) or []

    @classmethod
    def toggle_user_active(cls, user_id: int, active: bool):
        """Activa o desactiva un usuario."""
        query = "UPDATE usuarios SET activo = %s WHERE id_usuario = %s"
        DatabaseConnection.execute_query(query, (1 if active else 0, user_id))
