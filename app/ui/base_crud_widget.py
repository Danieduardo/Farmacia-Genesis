"""
Widget base CRUD — Farmacia Génesis
Base reutilizable para todos los módulos con tabla + formulario.
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem,
    QHeaderView, QMessageBox, QScrollArea, QSizePolicy, QAbstractItemView
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS


class BaseCrudWidget(QWidget):
    """Widget base con tabla, búsqueda, y botones CRUD."""

    def __init__(self, title="Módulo", columns=None, user_data=None):
        super().__init__()
        self.title_text = title
        self.columns = columns or []
        self.user_data = user_data or {}
        self._setup_ui()

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()
        title = QLabel(self.title_text)
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['text_primary']}; background: transparent;")
        header.addWidget(title)
        header.addStretch()

        self.btn_add = QPushButton("  ➕  Nuevo")
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.btn_add.setMinimumHeight(38)
        self.btn_add.setStyleSheet(f"""QPushButton {{ background-color: {COLORS['primary']}; color: #fff;
            border: none; border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px 18px; }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}""")
        self.btn_add.clicked.connect(self.on_add)
        header.addWidget(self.btn_add)
        layout.addLayout(header)

        # Búsqueda
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍  Buscar...")
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_input)

        self.btn_refresh = QPushButton("🔄  Actualizar")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setMinimumHeight(40)
        self.btn_refresh.setStyleSheet(f"""QPushButton {{ background-color: {COLORS['secondary']}; color: {COLORS['bg_dark']};
            border: none; border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px 16px; }}
            QPushButton:hover {{ background-color: {COLORS['secondary_hover']}; }}""")
        self.btn_refresh.clicked.connect(self.refresh_data)
        search_layout.addWidget(self.btn_refresh)
        layout.addLayout(search_layout)

        # Tabla
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(350)
        layout.addWidget(self.table)

        # Botones de acción para fila seleccionada
        actions = QHBoxLayout()
        actions.addStretch()

        self.btn_edit = QPushButton("  ✏️  Editar")
        self.btn_edit.setCursor(Qt.PointingHandCursor)
        self.btn_edit.setMinimumHeight(36)
        self.btn_edit.setStyleSheet(f"""QPushButton {{ background-color: {COLORS['secondary']}; color: {COLORS['bg_dark']};
            border: none; border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px 16px; }}
            QPushButton:hover {{ background-color: {COLORS['secondary_hover']}; }}""")
        self.btn_edit.clicked.connect(self.on_edit)
        actions.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("  🗑️  Eliminar")
        self.btn_delete.setCursor(Qt.PointingHandCursor)
        self.btn_delete.setMinimumHeight(36)
        self.btn_delete.setStyleSheet(f"""QPushButton {{ background-color: {COLORS['danger']}; color: #fff;
            border: none; border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px 16px; }}
            QPushButton:hover {{ background-color: #DC2626; }}""")
        self.btn_delete.clicked.connect(self.on_delete)
        actions.addWidget(self.btn_delete)
        layout.addLayout(actions)

        layout.addStretch()
        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def populate_table(self, data: list, id_field: str = "id"):
        """Llena la tabla con datos. data es lista de dicts."""
        self.table.setRowCount(len(data))
        for row_idx, record in enumerate(data):
            for col_idx, col_name in enumerate(self.columns):
                key = col_name.lower().replace(" ", "_").replace("é", "e").replace("ó", "o").replace("í", "i")
                value = ""
                for k, v in record.items():
                    if k.lower() == key or col_name.lower() in k.lower() or k.lower() in col_name.lower():
                        value = str(v) if v is not None else ""
                        break
                if not value and col_idx < len(record):
                    vals = list(record.values())
                    if col_idx < len(vals):
                        value = str(vals[col_idx]) if vals[col_idx] is not None else ""
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row_idx, col_idx, item)

    def get_selected_row_data(self) -> list | None:
        """Obtiene los datos de la fila seleccionada."""
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un registro primero.")
            return None
        data = []
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            data.append(item.text() if item else "")
        return data

    def on_search(self, text):
        """Filtra filas de la tabla."""
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    # Métodos para sobrescribir en cada módulo
    def on_add(self):
        pass

    def on_edit(self):
        pass

    def on_delete(self):
        pass

    def refresh_data(self):
        pass
