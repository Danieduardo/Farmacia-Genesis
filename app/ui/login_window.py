"""
Ventana de Login — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QFrame, QMessageBox, QSpacerItem, QSizePolicy
)

# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QTimer

# pyrefly: ignore [missing-import]
from PySide6.QtGui import QFont, QIcon

from app.config import COLORS, APP_NAME, APP_SUBTITLE
from app.services.auth_service import AuthService


class LoginWindow(QWidget):
    """Ventana de login con diseño moderno dark mode."""

    login_success = Signal(dict)  # Emite los datos del usuario al hacer login

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} — Iniciar Sesión")
        self.setFixedSize(480, 620)
        self.setStyleSheet(f"background-color: {COLORS['bg_dark']};")
        self._setup_ui()

    def _setup_ui(self):
        """Construye la interfaz del login."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── Contenedor centrado ───
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)
        center_layout.setContentsMargins(50, 40, 50, 40)
        center_layout.setSpacing(8)
        center_layout.setAlignment(Qt.AlignCenter)

        # ─── Ícono/Logo ───
        logo_label = QLabel("⚕")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(f"""
            font-size: 56px;
            color: {COLORS['secondary']};
            background: transparent;
            padding: 10px;
        """)
        center_layout.addWidget(logo_label)

        # ─── Nombre de la farmacia ───
        brand_label = QLabel(APP_NAME)
        brand_label.setAlignment(Qt.AlignCenter)
        brand_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['primary']};
            background: transparent;
            margin-top: 4px;
        """)
        center_layout.addWidget(brand_label)

        # ─── Subtítulo ───
        sub_label = QLabel(APP_SUBTITLE)
        sub_label.setAlignment(Qt.AlignCenter)
        sub_label.setStyleSheet(f"""
            font-size: 13px;
            color: {COLORS['text_secondary']};
            background: transparent;
            margin-bottom: 24px;
        """)
        center_layout.addWidget(sub_label)

        # ─── Card de login ───
        login_card = QFrame()
        login_card.setProperty("class", "login-card")
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(16)

        # Título del card
        login_title = QLabel("Iniciar Sesión")
        login_title.setAlignment(Qt.AlignCenter)
        login_title.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            background: transparent;
            margin-bottom: 8px;
        """)
        card_layout.addWidget(login_title)

        # ─── Campo: Usuario ───
        user_label = QLabel("👤  Usuario")
        user_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            background: transparent;
            font-weight: bold;
        """)
        card_layout.addWidget(user_label)

        self.input_user = QLineEdit()
        self.input_user.setPlaceholderText("Ingrese su usuario")
        self.input_user.setMinimumHeight(42)
        card_layout.addWidget(self.input_user)

        # ─── Campo: Contraseña ───
        pass_label = QLabel("🔒  Contraseña")
        pass_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['text_secondary']};
            background: transparent;
            font-weight: bold;
        """)
        card_layout.addWidget(pass_label)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Ingrese su contraseña")
        self.input_password.setEchoMode(QLineEdit.Password)
        self.input_password.setMinimumHeight(42)
        self.input_password.returnPressed.connect(self._do_login)
        card_layout.addWidget(self.input_password)

        # ─── Mensaje de error ───
        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"""
            color: {COLORS['danger']};
            font-size: 12px;
            background: transparent;
            min-height: 20px;
        """)
        self.error_label.hide()
        card_layout.addWidget(self.error_label)

        # ─── Botón Login ───
        card_layout.addSpacerItem(QSpacerItem(0, 8, QSizePolicy.Minimum, QSizePolicy.Fixed))

        self.btn_login = QPushButton("  Ingresar al Sistema")
        self.btn_login.setMinimumHeight(46)
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                font-weight: bold;
                padding: 12px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: #A83232;
            }}
        """)
        self.btn_login.clicked.connect(self._do_login)
        card_layout.addWidget(self.btn_login)

        center_layout.addWidget(login_card)

        # ─── Espaciador inferior ───
        center_layout.addStretch()

        main_layout.addWidget(center_widget)

    def _do_login(self):
        """Procesa el intento de login."""
        username = self.input_user.text().strip()
        password = self.input_password.text().strip()

        if not username or not password:
            self._show_error("Por favor ingrese usuario y contraseña")
            return

        self.btn_login.setEnabled(False)
        self.btn_login.setText("  Verificando...")

        # Usar QTimer para no bloquear la UI
        QTimer.singleShot(100, lambda: self._verify_credentials(username, password))

    def _verify_credentials(self, username, password):
        """Verifica las credenciales contra la base de datos."""
        try:
            user = AuthService.login(username, password)

            if user:
                self.login_success.emit(user)
            else:
                self._show_error("Usuario o contraseña incorrectos")
        except Exception as e:
            self._show_error(f"Error de conexión: {str(e)[:60]}")
        finally:
            self.btn_login.setEnabled(True)
            self.btn_login.setText("  Ingresar al Sistema")

    def _show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.error_label.setText(message)
        self.error_label.show()

        # Efecto de "shake" en el card
        QTimer.singleShot(3000, lambda: self.error_label.hide())

    def clear_fields(self):
        """Limpia los campos del formulario."""
        self.input_user.clear()
        self.input_password.clear()
        self.error_label.hide()
        self.input_user.setFocus()
