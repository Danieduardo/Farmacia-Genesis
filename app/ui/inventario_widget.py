"""
Inventario Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem,
    QComboBox, QSpinBox, QDateEdit
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt, QDate
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class MovimientoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nuevo Movimiento")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)
        title = QLabel("📦  Movimiento de Inventario")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)
        form = QFormLayout(); form.setSpacing(10)
        self.cmb_med = QComboBox(); self.cmb_med.setMinimumHeight(38)
        form.addRow("Medicamento:", self.cmb_med)
        self.cmb_tipo = QComboBox(); self.cmb_tipo.addItems(["Entrada", "Salida"]); self.cmb_tipo.setMinimumHeight(38)
        form.addRow("Tipo:", self.cmb_tipo)
        self.spn_cant = QSpinBox(); self.spn_cant.setMinimum(1); self.spn_cant.setMaximum(99999); self.spn_cant.setMinimumHeight(38)
        form.addRow("Cantidad:", self.spn_cant)
        self.inp_motivo = QLineEdit(); self.inp_motivo.setPlaceholderText("Motivo del movimiento"); self.inp_motivo.setMinimumHeight(38)
        form.addRow("Motivo:", self.inp_motivo)

        # Lote (opcional)
        self.inp_lote = QLineEdit(); self.inp_lote.setPlaceholderText("Nro. lote (opcional)"); self.inp_lote.setMinimumHeight(38)
        form.addRow("Lote:", self.inp_lote)
        self.dt_venc = QDateEdit(); self.dt_venc.setDate(QDate.currentDate().addMonths(12)); self.dt_venc.setCalendarPopup(True); self.dt_venc.setMinimumHeight(38)
        form.addRow("Vencimiento:", self.dt_venc)

        layout.addLayout(form)
        self._load_meds()
        btns = QHBoxLayout(); btns.addStretch()
        bc = QPushButton("Cancelar"); bc.setMinimumHeight(38)
        bc.setStyleSheet(f"QPushButton {{ background: transparent; color: {COLORS['text_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}")
        bc.clicked.connect(self.reject); btns.addWidget(bc)
        bs = QPushButton("💾  Guardar"); bs.setMinimumHeight(38); bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept); btns.addWidget(bs)
        layout.addLayout(btns)

    def _load_meds(self):
        try:
            for m in (DatabaseConnection.execute_query("SELECT id_medicamento, nombre, stock FROM medicamentos ORDER BY nombre", fetch_all=True) or []):
                self.cmb_med.addItem(f"{m['nombre']} (Stock: {m['stock']})", m)
        except: pass

    def get_data(self):
        med = self.cmb_med.currentData()
        return {"med": med, "tipo": self.cmb_tipo.currentText(), "cantidad": self.spn_cant.value(),
                "motivo": self.inp_motivo.text().strip(), "lote": self.inp_lote.text().strip(),
                "vencimiento": self.dt_venc.date().toPython()}


class InventarioWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="📦  Inventario", columns=["ID", "Medicamento", "Tipo", "Cantidad", "Fecha", "Motivo"], user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT mi.id_movimiento, m.nombre, mi.tipo_movimiento, mi.cantidad, mi.fecha, mi.motivo
                FROM movimientos_inventarios mi JOIN medicamentos m ON m.id_medicamento=mi.id_medicamento
                ORDER BY mi.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_movimiento']), r['nombre'], r['tipo_movimiento'],
                        str(r['cantidad']), str(r['fecha'])[:16], r.get('motivo') or ""]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                    if j == 2:
                        item.setForeground(Qt.green if v == "Entrada" else Qt.red)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = MovimientoDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['med']:
                QMessageBox.warning(self, "Aviso", "Seleccione un medicamento."); return
            med = d['med']; cant = d['cantidad']
            stock_ant = med['stock']
            if d['tipo'] == "Entrada":
                stock_new = stock_ant + cant
            else:
                if cant > stock_ant:
                    QMessageBox.warning(self, "Aviso", f"Stock insuficiente ({stock_ant})."); return
                stock_new = stock_ant - cant
            try:
                mid = DatabaseConnection.execute_query(
                    "INSERT INTO movimientos_inventarios (tipo_movimiento, cantidad, stock_anterior, stock_nuevo, motivo, id_medicamento) VALUES (%s,%s,%s,%s,%s,%s)",
                    (d['tipo'], cant, stock_ant, stock_new, d['motivo'], med['id_medicamento']))
                DatabaseConnection.execute_query("UPDATE medicamentos SET stock=%s WHERE id_medicamento=%s", (stock_new, med['id_medicamento']))
                if d['lote']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO lotes_medicamentos (numero_lote, fecha_vencimiento, cantidad, id_medicamento, id_movimiento) VALUES (%s,%s,%s,%s,%s)",
                        (d['lote'], d['vencimiento'], cant, med['id_medicamento'], mid))
                QMessageBox.information(self, "Éxito", f"Movimiento registrado. Stock: {stock_ant} → {stock_new}")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        QMessageBox.information(self, "Info", "Los movimientos no se pueden editar.")

    def on_delete(self):
        QMessageBox.information(self, "Info", "Los movimientos no se pueden eliminar.")
