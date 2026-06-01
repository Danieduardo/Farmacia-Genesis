"""
Farmacia Génesis — Punto de Entrada Principal
Ejecutar: python3 -m app.main
"""
import sys
import os

# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import QApplication
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QFont

from app.config import APP_NAME
from app.database.connection import DatabaseConnection
from app.services.auth_service import AuthService
from app.ui.login_window import LoginWindow
from app.ui.main_window import MainWindow


class FarmaciaApp:
    """Controlador principal de la aplicación."""

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)

        # Cargar fuente
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)

        # Cargar tema QSS
        self._load_theme()

        # Windows
        self.login_window = None
        self.main_window = None

    def _load_theme(self):
        """Carga el archivo de estilos QSS."""
        qss_path = os.path.join(os.path.dirname(__file__), "assets", "styles", "dark_theme.qss")
        try:
            with open(qss_path, "r", encoding="utf-8") as f:
                self.app.setStyleSheet(f.read())
                print("[UI] Tema cargado correctamente.")
        except FileNotFoundError:
            print(f"[UI] Archivo de tema no encontrado: {qss_path}")

    def _init_database(self):
        """Inicializa la conexión a la base de datos."""
        try:
            DatabaseConnection.initialize_pool()
            success, msg = DatabaseConnection.test_connection()
            if success:
                print(f"[DB] {msg}")
                # Asegurar que existe usuario admin
                AuthService.ensure_admin_exists()
                return True
            else:
                print(f"[DB] Error: {msg}")
                return False
        except Exception as e:
            print(f"[DB] Error de conexión: {e}")
            return False

    def _show_login(self):
        """Muestra la ventana de login."""
        if self.main_window:
            self.main_window.close()
            self.main_window = None

        self.login_window = LoginWindow()
        self.login_window.login_success.connect(self._on_login_success)
        self.login_window.show()

    def _on_login_success(self, user_data: dict):
        """Callback cuando el login es exitoso."""
        print(f"[AUTH] Login exitoso: {user_data['nombre_completo']} ({user_data['rol']})")

        # Cerrar login
        if self.login_window:
            self.login_window.close()
            self.login_window = None

        # Abrir ventana principal
        self.main_window = MainWindow(user_data)
        self.main_window.logout_signal.connect(self._on_logout)
        self.main_window.show()

    def _on_logout(self):
        """Callback cuando el usuario cierra sesión."""
        print("[AUTH] Sesión cerrada.")
        self._show_login()
        if self.login_window:
            self.login_window.clear_fields()

    def run(self):
        """Ejecuta la aplicación."""
        print("=" * 50)
        print(f"  {APP_NAME} — Sistema de Gestión")
        print("=" * 50)

        # Intentar conectar a BD
        if not self._init_database():
            # pyrefly: ignore [missing-import]
            from PySide6.QtWidgets import QMessageBox
            msg = QMessageBox()
            msg.setWindowTitle("Error de Conexión")
            msg.setText(
                "No se pudo conectar a la base de datos MySQL.\n\n"
                "Verifique que:\n"
                "1. MySQL está corriendo\n"
                "2. La base de datos 'farmacia_genesis' existe\n"
                "3. Las credenciales en app/config.py son correctas\n\n"
                "Ejecute el archivo SQL primero:\n"
                "mysql -u root -p < 'base de datos de farmacia.sql'"
            )
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
            sys.exit(1)

        # Mostrar login
        self._show_login()

        # Ejecutar
        sys.exit(self.app.exec())


def main():
    farmacia = FarmaciaApp()
    farmacia.run()


if __name__ == "__main__":
    main()
