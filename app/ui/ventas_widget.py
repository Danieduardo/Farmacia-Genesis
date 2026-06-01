"""
Ventas Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem,
    QComboBox, QSpinBox, QTableWidget, QHeaderView, QAbstractItemView
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class VentaDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Venta")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.items = []
        self.total = 0.0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("🛒  Nueva Venta")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(8)
        self.cmb_paciente = QComboBox()
        self.cmb_paciente.setMinimumHeight(38)
        form.addRow("Paciente:", self.cmb_paciente)
        layout.addLayout(form)

        # Agregar medicamento
        add_lbl = QLabel("Agregar medicamento:")
        add_lbl.setStyleSheet(f"font-size: 13px; font-weight: bold; color: {COLORS['secondary']}; background: transparent;")
        layout.addWidget(add_lbl)

        row = QHBoxLayout()
        self.cmb_med = QComboBox()
        self.cmb_med.setMinimumHeight(36)
        self.cmb_med.setMinimumWidth(200)
        row.addWidget(self.cmb_med)

        row.addWidget(QLabel("Cant:"))
        self.spn_cant = QSpinBox()
        self.spn_cant.setMinimum(1)
        self.spn_cant.setMaximum(9999)
        self.spn_cant.setMinimumHeight(36)
        row.addWidget(self.spn_cant)

        btn_add = QPushButton("➕ Agregar")
        btn_add.setMinimumHeight(36)
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._add_item)
        row.addWidget(btn_add)
        layout.addLayout(row)

        # Tabla de items
        self.tbl = QTableWidget()
        self.tbl.setColumnCount(5)
        self.tbl.setHorizontalHeaderLabels(["ID", "Medicamento", "Precio", "Cantidad", "Subtotal"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.verticalHeader().setVisible(False)
        self.tbl.setMaximumHeight(200)
        layout.addWidget(self.tbl)

        # Total
        self.lbl_total = QLabel("Total: Q 0.00")
        self.lbl_total.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {COLORS['primary']}; background: transparent; padding: 8px;")
        self.lbl_total.setAlignment(Qt.AlignRight)
        layout.addWidget(self.lbl_total)

        # Método de pago
        pay_row = QHBoxLayout()
        pay_row.addWidget(QLabel("Método de pago:"))
        self.cmb_metodo = QComboBox()
        self.cmb_metodo.addItems(["Efectivo", "Tarjeta de Crédito", "Tarjeta de Débito", "Transferencia"])
        self.cmb_metodo.setMinimumHeight(36)
        pay_row.addWidget(self.cmb_metodo)
        layout.addLayout(pay_row)

        self._load_combos()

        btns = QHBoxLayout()
        btns.addStretch()
        bc = QPushButton("Cancelar")
        bc.setMinimumHeight(38)
        bc.setStyleSheet(f"""QPushButton {{ background: transparent; color: {COLORS['text_secondary']};
            border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}""")
        bc.clicked.connect(self.reject)
        btns.addWidget(bc)
        bs = QPushButton("💰  Registrar Venta")
        bs.setMinimumHeight(38)
        bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept)
        btns.addWidget(bs)
        layout.addLayout(btns)

    def _load_combos(self):
        try:
            for p in (DatabaseConnection.execute_query("SELECT id_paciente, nombre_completo FROM pacientes ORDER BY nombre_completo", fetch_all=True) or []):
                self.cmb_paciente.addItem(f"{p['id_paciente']} - {p['nombre_completo']}", p['id_paciente'])
            for m in (DatabaseConnection.execute_query("SELECT id_medicamento, nombre, precio, stock FROM medicamentos WHERE stock > 0 ORDER BY nombre", fetch_all=True) or []):
                self.cmb_med.addItem(f"{m['nombre']} (Stock: {m['stock']}) - Q{m['precio']:.2f}", m)
        except Exception:
            pass

    def _add_item(self):
        med_data = self.cmb_med.currentData()
        if not med_data: return
        cant = self.spn_cant.value()
        if cant > med_data['stock']:
            QMessageBox.warning(self, "Aviso", f"Stock insuficiente. Disponible: {med_data['stock']}")
            return
        subtotal = float(med_data['precio']) * cant
        self.items.append({"id": med_data['id_medicamento'], "nombre": med_data['nombre'],
                          "precio": float(med_data['precio']), "cantidad": cant, "subtotal": subtotal})
        self.total += subtotal
        self._refresh_table()

    def _refresh_table(self):
        self.tbl.setRowCount(len(self.items))
        for i, it in enumerate(self.items):
            for j, v in enumerate([str(it['id']), it['nombre'], f"Q {it['precio']:.2f}",
                                   str(it['cantidad']), f"Q {it['subtotal']:.2f}"]):
                item = QTableWidgetItem(v)
                item.setTextAlignment(Qt.AlignCenter)
                self.tbl.setItem(i, j, item)
        self.lbl_total.setText(f"Total: Q {self.total:,.2f}")

    def get_data(self):
        return {
            "id_paciente": self.cmb_paciente.currentData(),
            "items": self.items,
            "total": self.total,
            "metodo_pago": self.cmb_metodo.currentText(),
        }


class VentasWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="🛒  Ventas", columns=["ID", "Paciente", "Fecha", "Total"], user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT v.id_venta, p.nombre_completo as paciente, v.fecha, v.total
                FROM ventas v JOIN pacientes p ON p.id_paciente=v.id_paciente
                ORDER BY v.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_venta']), r['paciente'], str(r['fecha'])[:16], f"Q {r['total']:,.2f}"]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = VentaDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['id_paciente'] or not d['items']:
                QMessageBox.warning(self, "Aviso", "Seleccione paciente y agregue medicamentos.")
                return
            try:
                vid = DatabaseConnection.execute_query(
                    "INSERT INTO ventas (total, id_paciente) VALUES (%s,%s)",
                    (d['total'], d['id_paciente']))
                for it in d['items']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO detalles_ventas (cantidad, precio_unitario, subtotal, id_medicamento, id_venta) VALUES (%s,%s,%s,%s,%s)",
                        (it['cantidad'], it['precio'], it['subtotal'], it['id'], vid))
                    # Descontar stock
                    DatabaseConnection.execute_query(
                        "UPDATE medicamentos SET stock = stock - %s WHERE id_medicamento = %s",
                        (it['cantidad'], it['id']))
                # Registrar pago
                pid = DatabaseConnection.execute_query(
                    "INSERT INTO pagos (monto, id_venta) VALUES (%s,%s)", (d['total'], vid))
                DatabaseConnection.execute_query(
                    "INSERT INTO metodos_pagos (tipo, id_pago) VALUES (%s,%s)", (d['metodo_pago'], pid))

                QMessageBox.information(self, "Éxito", f"Venta #{vid} registrada. Total: Q {d['total']:,.2f}")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        QMessageBox.information(self, "Info", "Las ventas no se pueden editar. Registre una nueva.")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Anular venta #{data[0]}?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM ventas WHERE id_venta=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Venta anulada.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
