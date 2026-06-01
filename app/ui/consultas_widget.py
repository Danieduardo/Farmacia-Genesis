"""
Consultas & Recetas Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem,
    QComboBox, QTextEdit, QWidget, QTabWidget, QSpinBox
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class ConsultaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Consulta")
        self.setMinimumWidth(550)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("🩺  Nueva Consulta Médica")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.cmb_paciente = QComboBox()
        self.cmb_paciente.setMinimumHeight(38)
        form.addRow("Paciente:", self.cmb_paciente)

        self.cmb_medico = QComboBox()
        self.cmb_medico.setMinimumHeight(38)
        form.addRow("Médico:", self.cmb_medico)

        self.inp_diagnostico = QTextEdit()
        self.inp_diagnostico.setPlaceholderText("Diagnóstico del paciente...")
        self.inp_diagnostico.setMaximumHeight(80)
        form.addRow("Diagnóstico:", self.inp_diagnostico)

        self.inp_tratamiento = QTextEdit()
        self.inp_tratamiento.setPlaceholderText("Tratamiento indicado...")
        self.inp_tratamiento.setMaximumHeight(80)
        form.addRow("Tratamiento:", self.inp_tratamiento)

        layout.addLayout(form)

        # Sección de receta
        rec_label = QLabel("📋  Receta (opcional)")
        rec_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {COLORS['secondary']}; background: transparent; margin-top: 8px;")
        layout.addWidget(rec_label)

        rec_row = QHBoxLayout()
        self.cmb_medicamento = QComboBox()
        self.cmb_medicamento.setMinimumHeight(36)
        self.cmb_medicamento.setMinimumWidth(180)
        rec_row.addWidget(self.cmb_medicamento)

        self.inp_cantidad = QSpinBox()
        self.inp_cantidad.setMinimum(1)
        self.inp_cantidad.setMaximum(999)
        self.inp_cantidad.setMinimumHeight(36)
        rec_row.addWidget(QLabel("Cant:"))
        rec_row.addWidget(self.inp_cantidad)

        self.inp_dosis = QLineEdit()
        self.inp_dosis.setPlaceholderText("Ej: 1 cada 8 horas")
        self.inp_dosis.setMinimumHeight(36)
        rec_row.addWidget(self.inp_dosis)

        btn_add_med = QPushButton("➕")
        btn_add_med.setMinimumHeight(36)
        btn_add_med.setMaximumWidth(40)
        btn_add_med.setCursor(Qt.PointingHandCursor)
        btn_add_med.clicked.connect(self._add_med_to_list)
        rec_row.addWidget(btn_add_med)
        layout.addLayout(rec_row)

        self.meds_list = QLabel("Sin medicamentos agregados")
        self.meds_list.setStyleSheet(f"color: {COLORS['text_muted']}; background: transparent; padding: 6px;")
        self.meds_list.setWordWrap(True)
        layout.addWidget(self.meds_list)
        self.receta_items = []

        self._load_combos()

        btns = QHBoxLayout()
        btns.addStretch()
        bc = QPushButton("Cancelar")
        bc.setMinimumHeight(38)
        bc.setStyleSheet(f"""QPushButton {{ background: transparent; color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}
            QPushButton:hover {{ border-color: {COLORS['secondary']}; color: {COLORS['secondary']}; }}""")
        bc.clicked.connect(self.reject)
        btns.addWidget(bc)
        bs = QPushButton("💾  Guardar Consulta")
        bs.setMinimumHeight(38)
        bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept)
        btns.addWidget(bs)
        layout.addLayout(btns)

    def _load_combos(self):
        try:
            for p in (DatabaseConnection.execute_query("SELECT id_paciente, nombre_completo FROM pacientes ORDER BY nombre_completo", fetch_all=True) or []):
                self.cmb_paciente.addItem(f"{p['id_paciente']} - {p['nombre_completo']}", p['id_paciente'])
            for m in (DatabaseConnection.execute_query("SELECT id_medico, nombre FROM medicos ORDER BY nombre", fetch_all=True) or []):
                self.cmb_medico.addItem(f"{m['id_medico']} - {m['nombre']}", m['id_medico'])
            for med in (DatabaseConnection.execute_query("SELECT id_medicamento, nombre FROM medicamentos ORDER BY nombre", fetch_all=True) or []):
                self.cmb_medicamento.addItem(f"{med['nombre']}", med['id_medicamento'])
        except Exception:
            pass

    def _add_med_to_list(self):
        if self.cmb_medicamento.currentData() is None: return
        item = {
            "id_medicamento": self.cmb_medicamento.currentData(),
            "nombre": self.cmb_medicamento.currentText(),
            "cantidad": self.inp_cantidad.value(),
            "dosis": self.inp_dosis.text().strip() or "Según indicación",
        }
        self.receta_items.append(item)
        text = "\n".join([f"  • {it['nombre']} — Cant: {it['cantidad']} — {it['dosis']}" for it in self.receta_items])
        self.meds_list.setText(text)
        self.meds_list.setStyleSheet(f"color: {COLORS['text_primary']}; background: {COLORS['bg_light']}; padding: 8px; border-radius: 6px;")

    def get_data(self):
        return {
            "id_paciente": self.cmb_paciente.currentData(),
            "id_medico": self.cmb_medico.currentData(),
            "diagnostico": self.inp_diagnostico.toPlainText().strip(),
            "tratamiento": self.inp_tratamiento.toPlainText().strip(),
            "receta_items": self.receta_items,
        }


class ConsultasWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="🩺  Consultas & Recetas",
                         columns=["ID", "Paciente", "Médico", "Diagnóstico", "Fecha"],
                         user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT c.id_consulta, p.nombre_completo as paciente, m.nombre as medico,
                       c.diagnostico, c.fecha
                FROM consultas c
                JOIN pacientes p ON p.id_paciente=c.id_paciente
                JOIN medicos m ON m.id_medico=c.id_medico
                ORDER BY c.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_consulta']), r['paciente'], r['medico'],
                        r['diagnostico'][:40], str(r['fecha'])[:16]]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = ConsultaDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['id_paciente'] or not d['diagnostico']:
                QMessageBox.warning(self, "Aviso", "Paciente y diagnóstico son obligatorios.")
                return
            try:
                cid = DatabaseConnection.execute_query(
                    "INSERT INTO consultas (diagnostico, tratamiento, id_paciente, id_medico) VALUES (%s,%s,%s,%s)",
                    (d['diagnostico'], d['tratamiento'], d['id_paciente'], d['id_medico']))

                if d['receta_items']:
                    rid = DatabaseConnection.execute_query(
                        "INSERT INTO recetas (id_consulta) VALUES (%s)", (cid,))
                    for it in d['receta_items']:
                        DatabaseConnection.execute_query(
                            "INSERT INTO detalles_recetas (cantidad, dosis, id_receta, id_medicamento) VALUES (%s,%s,%s,%s)",
                            (it['cantidad'], it['dosis'], rid, it['id_medicamento']))

                QMessageBox.information(self, "Éxito", "Consulta y receta registradas.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        QMessageBox.information(self, "Info", "Para editar, elimine y cree una nueva consulta.")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar consulta #{data[0]}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM consultas WHERE id_consulta=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Consulta eliminada.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
