"""
Médicos Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class MedicoDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Médico" if data else "Nuevo Médico")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.data = data
        self._setup_ui()
        if data:
            self._load(data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Editar Médico" if self.data else "Nuevo Médico")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Nombre completo")
        self.inp_nombre.setMinimumHeight(38)
        form.addRow("Nombre:", self.inp_nombre)

        self.inp_especialidad = QLineEdit()
        self.inp_especialidad.setPlaceholderText("Especialidad médica")
        self.inp_especialidad.setMinimumHeight(38)
        form.addRow("Especialidad:", self.inp_especialidad)

        self.inp_telefono = QLineEdit()
        self.inp_telefono.setPlaceholderText("Teléfono de contacto")
        self.inp_telefono.setMinimumHeight(38)
        form.addRow("Teléfono:", self.inp_telefono)
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addStretch()
        bc = QPushButton("Cancelar")
        bc.setMinimumHeight(38)
        bc.setStyleSheet(f"""QPushButton {{ background: transparent; color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}
            QPushButton:hover {{ border-color: {COLORS['secondary']}; color: {COLORS['secondary']}; }}""")
        bc.clicked.connect(self.reject)
        btns.addWidget(bc)
        bs = QPushButton("💾  Guardar")
        bs.setMinimumHeight(38)
        bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept)
        btns.addWidget(bs)
        layout.addLayout(btns)

    def _load(self, data):
        if len(data) > 1: self.inp_nombre.setText(data[1])
        if len(data) > 2: self.inp_especialidad.setText(data[2])
        if len(data) > 3: self.inp_telefono.setText(data[3])

    def get_data(self):
        return {
            "nombre": self.inp_nombre.text().strip(),
            "especialidad": self.inp_especialidad.text().strip(),
            "telefono": self.inp_telefono.text().strip(),
        }


class MedicosWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="👨‍⚕️  Médicos", columns=["ID", "Nombre", "Especialidad", "Teléfono"], user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query(
                "SELECT id_medico, nombre, especialidad, telefono FROM medicos ORDER BY id_medico DESC",
                fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                for j, v in enumerate([str(r['id_medico']), r['nombre'], r['especialidad'], str(r['telefono'])]):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar médicos: {e}")

    def on_add(self):
        dlg = MedicoDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['nombre'] or not d['especialidad']:
                QMessageBox.warning(self, "Aviso", "Nombre y especialidad son obligatorios.")
                return
            try:
                DatabaseConnection.execute_query(
                    "INSERT INTO medicos (nombre, especialidad, telefono) VALUES (%s, %s, %s)",
                    (d['nombre'], d['especialidad'], d['telefono']))
                QMessageBox.information(self, "Éxito", "Médico registrado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        dlg = MedicoDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                DatabaseConnection.execute_query(
                    "UPDATE medicos SET nombre=%s, especialidad=%s, telefono=%s WHERE id_medico=%s",
                    (d['nombre'], d['especialidad'], d['telefono'], int(data[0])))
                QMessageBox.information(self, "Éxito", "Médico actualizado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar médico '{data[1]}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM medicos WHERE id_medico=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Médico eliminado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
