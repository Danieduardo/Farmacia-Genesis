"""
Citas Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem,
    QComboBox, QDateTimeEdit
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, QDateTime
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class CitaDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Cita" if data else "Nueva Cita")
        self.setMinimumWidth(450)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.data = data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Editar Cita" if self.data else "Nueva Cita")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.cmb_paciente = QComboBox()
        self.cmb_paciente.setMinimumHeight(38)
        self._load_pacientes()
        form.addRow("Paciente:", self.cmb_paciente)

        self.cmb_medico = QComboBox()
        self.cmb_medico.setMinimumHeight(38)
        self._load_medicos()
        form.addRow("Médico:", self.cmb_medico)

        self.dt_fecha = QDateTimeEdit()
        self.dt_fecha.setDateTime(QDateTime.currentDateTime())
        self.dt_fecha.setCalendarPopup(True)
        self.dt_fecha.setMinimumHeight(38)
        form.addRow("Fecha/Hora:", self.dt_fecha)

        self.inp_motivo = QLineEdit()
        self.inp_motivo.setPlaceholderText("Motivo de la cita")
        self.inp_motivo.setMinimumHeight(38)
        form.addRow("Motivo:", self.inp_motivo)

        self.cmb_estado = QComboBox()
        self.cmb_estado.addItems(["Pendiente", "Confirmada", "Completada", "Cancelada"])
        self.cmb_estado.setMinimumHeight(38)
        form.addRow("Estado:", self.cmb_estado)

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

    def _load_pacientes(self):
        try:
            pacs = DatabaseConnection.execute_query(
                "SELECT id_paciente, nombre_completo FROM pacientes ORDER BY nombre_completo", fetch_all=True) or []
            for p in pacs:
                self.cmb_paciente.addItem(f"{p['id_paciente']} - {p['nombre_completo']}", p['id_paciente'])
        except Exception:
            pass

    def _load_medicos(self):
        try:
            meds = DatabaseConnection.execute_query(
                "SELECT id_medico, nombre FROM medicos ORDER BY nombre", fetch_all=True) or []
            for m in meds:
                self.cmb_medico.addItem(f"{m['id_medico']} - {m['nombre']}", m['id_medico'])
        except Exception:
            pass

    def get_data(self):
        return {
            "id_paciente": self.cmb_paciente.currentData(),
            "id_medico": self.cmb_medico.currentData(),
            "fecha": self.dt_fecha.dateTime().toPython(),
            "motivo": self.inp_motivo.text().strip(),
            "estado": self.cmb_estado.currentText(),
        }


class CitasWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="📅  Citas", columns=["ID", "Paciente", "Médico", "Fecha", "Estado"], user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT c.id_cita, p.nombre_completo as paciente, m.nombre as medico, c.fecha,
                    (SELECT ec.nombre FROM estados_citas ec WHERE ec.id_cita=c.id_cita ORDER BY ec.fecha_cambio DESC LIMIT 1) as estado
                FROM citas c
                JOIN pacientes p ON p.id_paciente=c.id_paciente
                JOIN medicos m ON m.id_medico=c.id_medico
                ORDER BY c.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_cita']), r['paciente'], r['medico'],
                        str(r['fecha'])[:16], r.get('estado') or 'Sin estado']
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    if j == 4:
                        if v == "Completada":
                            item.setForeground(Qt.green)
                        elif v == "Cancelada":
                            item.setForeground(Qt.red)
                        elif v == "Pendiente":
                            item.setForeground(Qt.yellow)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = CitaDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['id_paciente'] or not d['id_medico']:
                QMessageBox.warning(self, "Aviso", "Seleccione paciente y médico.")
                return
            try:
                cid = DatabaseConnection.execute_query(
                    "INSERT INTO citas (fecha, motivo, id_paciente, id_medico) VALUES (%s,%s,%s,%s)",
                    (d['fecha'], d['motivo'], d['id_paciente'], d['id_medico']))
                DatabaseConnection.execute_query(
                    "INSERT INTO estados_citas (nombre, descripcion, id_cita) VALUES (%s,%s,%s)",
                    (d['estado'], f"Cita creada - {d['estado']}", cid))
                QMessageBox.information(self, "Éxito", "Cita agendada.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        dlg = CitaDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                DatabaseConnection.execute_query(
                    "UPDATE citas SET fecha=%s, motivo=%s, id_paciente=%s, id_medico=%s WHERE id_cita=%s",
                    (d['fecha'], d['motivo'], d['id_paciente'], d['id_medico'], int(data[0])))
                DatabaseConnection.execute_query(
                    "INSERT INTO estados_citas (nombre, descripcion, id_cita) VALUES (%s,%s,%s)",
                    (d['estado'], f"Estado cambiado a {d['estado']}", int(data[0])))
                QMessageBox.information(self, "Éxito", "Cita actualizada.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar cita #{data[0]}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM citas WHERE id_cita=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Cita eliminada.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
