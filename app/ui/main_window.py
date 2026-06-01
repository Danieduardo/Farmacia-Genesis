"""
Ventana Principal con Sidebar — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QStackedWidget, QSpacerItem, QSizePolicy,
    QMessageBox, QScrollArea
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, Signal
# pyrefly: ignore [missing-import]
from PySide6.QtGui import QFont

from app.config import COLORS, APP_NAME, ROLE_ADMIN, ROLE_MEDICO, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT
from app.ui.dashboard_widget import DashboardWidget
from app.ui.pacientes_widget import PacientesWidget
from app.ui.medicos_widget import MedicosWidget
from app.ui.medicamentos_widget import MedicamentosWidget
from app.ui.citas_widget import CitasWidget
from app.ui.consultas_widget import ConsultasWidget
from app.ui.ventas_widget import VentasWidget
from app.ui.compras_widget import ComprasWidget
from app.ui.inventario_widget import InventarioWidget
from app.ui.reportes_widget import ReportesWidget
from app.ui.usuarios_widget import UsuariosWidget


class MainWindow(QMainWindow):
    """Ventana principal con sidebar y contenido dinámico."""

    logout_signal = Signal()

    # Definición del menú: (icono, nombre, widget_class, roles_permitidos)
    MENU_ITEMS = [
        ("🏠", "Dashboard",     DashboardWidget,    [ROLE_ADMIN, ROLE_MEDICO]),
        ("👥", "Pacientes",     PacientesWidget,    [ROLE_ADMIN, ROLE_MEDICO]),
        ("👨‍⚕️", "Médicos",       MedicosWidget,      [ROLE_ADMIN]),
        ("📅", "Citas",         CitasWidget,        [ROLE_ADMIN, ROLE_MEDICO]),
        ("🩺", "Consultas",     ConsultasWidget,    [ROLE_ADMIN, ROLE_MEDICO]),
        ("💊", "Medicamentos",  MedicamentosWidget, [ROLE_ADMIN]),
        ("📦", "Inventario",    InventarioWidget,   [ROLE_ADMIN]),
        ("🛒", "Ventas",        VentasWidget,       [ROLE_ADMIN]),
        ("🏭", "Compras",       ComprasWidget,      [ROLE_ADMIN]),
        ("📋", "Reportes",      ReportesWidget,     [ROLE_ADMIN, ROLE_MEDICO]),
        ("👤", "Usuarios",      UsuariosWidget,     [ROLE_ADMIN]),
    ]

    def __init__(self, user_data: dict):
        super().__init__()
        self.user_data = user_data
        self.current_role = user_data.get('rol', ROLE_MEDICO)
        self.nav_buttons = []

        self.setWindowTitle(f"{APP_NAME} — {user_data.get('nombre_completo', '')}")
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.showMaximized()

        self._setup_ui()
        self._navigate_to(0)  # Dashboard por defecto

    def _setup_ui(self):
        """Construye la interfaz principal."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ─── SIDEBAR ───
        sidebar = self._build_sidebar()
        main_layout.addWidget(sidebar)

        # ─── CONTENIDO PRINCIPAL ───
        self.content_stack = QStackedWidget()
        self.content_stack.setStyleSheet(f"background-color: {COLORS['bg_dark']};")

        # Crear widgets de contenido según rol
        self._widget_map = {}
        for idx, (icon, name, widget_cls, roles) in enumerate(self.MENU_ITEMS):
            if self.current_role in roles:
                try:
                    widget = widget_cls(self.user_data)
                except TypeError:
                    widget = widget_cls()
                self.content_stack.addWidget(widget)
                self._widget_map[name] = self.content_stack.count() - 1

        main_layout.addWidget(self.content_stack, 1)

    def _build_sidebar(self) -> QFrame:
        """Construye el sidebar de navegación."""
        sidebar = QFrame()
        sidebar.setProperty("class", "sidebar")
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_medium']};
                border-right: 1px solid {COLORS['border']};
            }}
        """)

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(4)

        # ─── Logo y marca ───
        logo_label = QLabel("⚕")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(f"""
            font-size: 36px;
            color: {COLORS['secondary']};
            background: transparent;
            padding: 4px;
        """)
        layout.addWidget(logo_label)

        brand = QLabel(APP_NAME)
        brand.setAlignment(Qt.AlignCenter)
        brand.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['primary']};
            background: transparent;
        """)
        layout.addWidget(brand)

        # ─── Info usuario ───
        user_frame = QFrame()
        user_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['bg_light']};
                border-radius: 8px;
                padding: 8px;
                margin-top: 12px;
                margin-bottom: 8px;
            }}
        """)
        user_layout = QVBoxLayout(user_frame)
        user_layout.setContentsMargins(10, 8, 10, 8)
        user_layout.setSpacing(2)

        user_name = QLabel(self.user_data.get('nombre_completo', 'Usuario'))
        user_name.setAlignment(Qt.AlignCenter)
        user_name.setStyleSheet(f"""
            font-size: 13px;
            font-weight: bold;
            color: {COLORS['text_primary']};
            background: transparent;
        """)
        user_name.setWordWrap(True)
        user_layout.addWidget(user_name)

        role_text = "Administrador" if self.current_role == ROLE_ADMIN else "Médico"
        role_color = COLORS['primary'] if self.current_role == ROLE_ADMIN else COLORS['secondary']
        role_label = QLabel(role_text)
        role_label.setAlignment(Qt.AlignCenter)
        role_label.setStyleSheet(f"""
            font-size: 11px;
            font-weight: bold;
            color: {role_color};
            background: transparent;
        """)
        user_layout.addWidget(role_label)

        layout.addWidget(user_frame)

        # ─── Separador ───
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 6px 0;")
        layout.addWidget(sep)

        # ─── Menú de navegación ───
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("background: transparent; border: none;")

        nav_container = QWidget()
        nav_container.setStyleSheet("background: transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(2)

        stack_index = 0
        for idx, (icon, name, widget_cls, roles) in enumerate(self.MENU_ITEMS):
            if self.current_role in roles:
                btn = QPushButton(f"  {icon}  {name}")
                btn.setProperty("class", "nav-item")
                btn.setCursor(Qt.PointingHandCursor)
                btn.setMinimumHeight(38)
                btn.setStyleSheet(self._nav_button_style(False))
                current_stack_index = stack_index
                btn.clicked.connect(lambda checked, i=current_stack_index: self._navigate_to(i))
                nav_layout.addWidget(btn)
                self.nav_buttons.append(btn)
                stack_index += 1

        nav_layout.addStretch()
        scroll_area.setWidget(nav_container)
        layout.addWidget(scroll_area, 1)

        # ─── Separador inferior ───
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        sep2.setStyleSheet(f"background-color: {COLORS['border']}; max-height: 1px; margin: 6px 0;")
        layout.addWidget(sep2)

        # ─── Botón Cerrar Sesión ───
        btn_logout = QPushButton("  🚪  Cerrar Sesión")
        btn_logout.setCursor(Qt.PointingHandCursor)
        btn_logout.setMinimumHeight(38)
        btn_logout.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS['danger']};
                border: 1px solid {COLORS['danger']};
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: rgba(239, 68, 68, 0.15);
            }}
        """)
        btn_logout.clicked.connect(self._confirm_logout)
        layout.addWidget(btn_logout)

        return sidebar

    def _nav_button_style(self, active: bool) -> str:
        """Retorna el estilo de un botón de navegación."""
        if active:
            return f"""
                QPushButton {{
                    background-color: rgba(224, 80, 80, 0.15);
                    color: {COLORS['primary']};
                    border: none;
                    border-radius: 8px;
                    border-left: 3px solid {COLORS['primary']};
                    font-size: 13px;
                    font-weight: bold;
                    text-align: left;
                    padding: 10px 14px;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['text_secondary']};
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    text-align: left;
                    padding: 10px 14px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['bg_light']};
                    color: {COLORS['text_primary']};
                }}
            """

    def _navigate_to(self, index: int):
        """Navega a una sección del menú."""
        # Actualizar estilos de botones
        for i, btn in enumerate(self.nav_buttons):
            btn.setStyleSheet(self._nav_button_style(i == index))

        # Cambiar contenido
        if index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)

            # Refrescar datos del widget activo si tiene método refresh
            current_widget = self.content_stack.currentWidget()
            if hasattr(current_widget, 'refresh_data'):
                current_widget.refresh_data()

    def _confirm_logout(self):
        """Confirma el cierre de sesión."""
        reply = QMessageBox.question(
            self,
            "Cerrar Sesión",
            "¿Está seguro que desea cerrar sesión?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.logout_signal.emit()
