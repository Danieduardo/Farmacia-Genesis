"""
Pacientes Widget — Farmacia Génesis
CRUD completo de pacientes con historial médico.
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QMessageBox, QFormLayout, QTextEdit
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class PacienteDialog(QDialog):
    """Diálogo para crear/editar paciente."""
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Paciente" if data else "Nuevo Paciente")
        self.setMinimumWidth(450)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.data = data
        self._setup_ui()
        if data:
            self._load_data(data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Editar Paciente" if self.data else "Nuevo Paciente")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Nombre completo del paciente")
        self.inp_nombre.setMinimumHeight(38)
        form.addRow("Nombre:", self.inp_nombre)

        self.inp_edad = QLineEdit()
        self.inp_edad.setPlaceholderText("Edad")
        self.inp_edad.setMinimumHeight(38)
        form.addRow("Edad:", self.inp_edad)

        self.inp_genero = QComboBox()
        self.inp_genero.addItems(["Masculino", "Femenino", "Otro"])
        self.inp_genero.setMinimumHeight(38)
        form.addRow("Género:", self.inp_genero)

        self.inp_correo = QLineEdit()
        self.inp_correo.setPlaceholderText("correo@ejemplo.com")
        self.inp_correo.setMinimumHeight(38)
        form.addRow("Correo:", self.inp_correo)

        self.inp_telefono = QLineEdit()
        self.inp_telefono.setPlaceholderText("Número de teléfono")
        self.inp_telefono.setMinimumHeight(38)
        form.addRow("Teléfono:", self.inp_telefono)

        self.inp_departamento = QLineEdit()
        self.inp_departamento.setPlaceholderText("Departamento")
        self.inp_departamento.setMinimumHeight(38)
        form.addRow("Depto:", self.inp_departamento)

        self.inp_municipio = QLineEdit()
        self.inp_municipio.setPlaceholderText("Municipio")
        self.inp_municipio.setMinimumHeight(38)
        form.addRow("Municipio:", self.inp_municipio)

        self.inp_referencia = QLineEdit()
        self.inp_referencia.setPlaceholderText("Referencia de la dirección")
        self.inp_referencia.setMinimumHeight(38)
        form.addRow("Referencia:", self.inp_referencia)

        layout.addLayout(form)

        # Botones
        btns = QHBoxLayout()
        btns.addStretch()
        btn_cancel = QPushButton("Cancelar")
        btn_cancel.setMinimumHeight(38)
        btn_cancel.setStyleSheet(f"""QPushButton {{ background: transparent; color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}
            QPushButton:hover {{ border-color: {COLORS['secondary']}; color: {COLORS['secondary']}; }}""")
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_cancel)

        btn_save = QPushButton("💾  Guardar")
        btn_save.setMinimumHeight(38)
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self.accept)
        btns.addWidget(btn_save)
        layout.addLayout(btns)

    def _load_data(self, data):
        if len(data) > 1: self.inp_nombre.setText(data[1])
        if len(data) > 2: self.inp_edad.setText(data[2])
        if len(data) > 3:
            idx = self.inp_genero.findText(data[3])
            if idx >= 0: self.inp_genero.setCurrentIndex(idx)

    def get_data(self):
        return {
            "nombre": self.inp_nombre.text().strip(),
            "edad": self.inp_edad.text().strip(),
            "genero": self.inp_genero.currentText(),
            "correo": self.inp_correo.text().strip(),
            "telefono": self.inp_telefono.text().strip(),
            "departamento": self.inp_departamento.text().strip(),
            "municipio": self.inp_municipio.text().strip(),
            "referencia": self.inp_referencia.text().strip(),
        }


class PacientesWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(
            title="👥  Pacientes",
            columns=["ID", "Nombre", "Edad", "Género", "Registro"],
            user_data=user_data
        )
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query(
                "SELECT id_paciente, nombre_completo, edad, genero, fecha_registro FROM pacientes ORDER BY id_paciente DESC",
                fetch_all=True
            ) or []
            self.table.setRowCount(0)
            # pyrefly: ignore [missing-import]
            from PySide6.QtWidgets import QTableWidgetItem
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_paciente']), r['nombre_completo'], str(r['edad']), r['genero'],
                        str(r['fecha_registro'])[:10] if r['fecha_registro'] else ""]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar pacientes: {e}")

    def on_add(self):
        dlg = PacienteDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['nombre'] or not d['edad']:
                QMessageBox.warning(self, "Aviso", "Nombre y edad son obligatorios.")
                return
            try:
                pid = DatabaseConnection.execute_query(
                    "INSERT INTO pacientes (nombre_completo, edad, genero) VALUES (%s, %s, %s)",
                    (d['nombre'], int(d['edad']), d['genero'])
                )
                if d['correo']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO correos (correo, id_paciente) VALUES (%s, %s)",
                        (d['correo'], pid)
                    )
                if d['telefono']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO telefonos_pacientes (telefono, id_paciente) VALUES (%s, %s)",
                        (d['telefono'], pid)
                    )
                if d['departamento'] and d['municipio'] and d['referencia']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO direcciones (departamento, municipio, referencia, id_paciente) VALUES (%s,%s,%s,%s)",
                        (d['departamento'], d['municipio'], d['referencia'], pid)
                    )
                QMessageBox.information(self, "Éxito", "Paciente registrado correctamente.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        dlg = PacienteDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['nombre'] or not d['edad']:
                QMessageBox.warning(self, "Aviso", "Nombre y edad son obligatorios.")
                return
            try:
                DatabaseConnection.execute_query(
                    "UPDATE pacientes SET nombre_completo=%s, edad=%s, genero=%s WHERE id_paciente=%s",
                    (d['nombre'], int(d['edad']), d['genero'], int(data[0]))
                )
                QMessageBox.information(self, "Éxito", "Paciente actualizado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar paciente '{data[1]}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM pacientes WHERE id_paciente=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Paciente eliminado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
