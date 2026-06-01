"""
Compras & Proveedores Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem,
    QComboBox, QSpinBox, QTableWidget, QHeaderView, QAbstractItemView,
    QTabWidget, QWidget
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class ProveedorDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Proveedor")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.data = data
        self._setup_ui()
        if data: self._load(data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)
        title = QLabel("Proveedor")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)
        form = QFormLayout()
        form.setSpacing(10)
        self.inp_nombre = QLineEdit(); self.inp_nombre.setMinimumHeight(38); self.inp_nombre.setPlaceholderText("Nombre")
        form.addRow("Nombre:", self.inp_nombre)
        self.inp_dir = QLineEdit(); self.inp_dir.setMinimumHeight(38); self.inp_dir.setPlaceholderText("Dirección")
        form.addRow("Dirección:", self.inp_dir)
        self.inp_correo = QLineEdit(); self.inp_correo.setMinimumHeight(38); self.inp_correo.setPlaceholderText("correo@prov.com")
        form.addRow("Correo:", self.inp_correo)
        self.inp_tel = QLineEdit(); self.inp_tel.setMinimumHeight(38); self.inp_tel.setPlaceholderText("Teléfono")
        form.addRow("Teléfono:", self.inp_tel)
        layout.addLayout(form)
        btns = QHBoxLayout(); btns.addStretch()
        bc = QPushButton("Cancelar"); bc.setMinimumHeight(38)
        bc.setStyleSheet(f"QPushButton {{ background: transparent; color: {COLORS['text_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}")
        bc.clicked.connect(self.reject); btns.addWidget(bc)
        bs = QPushButton("💾  Guardar"); bs.setMinimumHeight(38); bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept); btns.addWidget(bs)
        layout.addLayout(btns)

    def _load(self, d):
        if len(d)>1: self.inp_nombre.setText(d[1])
        if len(d)>2: self.inp_dir.setText(d[2])
        if len(d)>3: self.inp_correo.setText(d[3])

    def get_data(self):
        return {"nombre": self.inp_nombre.text().strip(), "direccion": self.inp_dir.text().strip(),
                "correo": self.inp_correo.text().strip(), "telefono": self.inp_tel.text().strip()}


class CompraDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Compra")
        self.setMinimumWidth(580)
        self.setMinimumHeight(450)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.items = []; self.total = 0.0
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(24, 20, 24, 20)
        title = QLabel("🏭  Nueva Orden de Compra")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)
        form = QFormLayout(); form.setSpacing(8)
        self.cmb_prov = QComboBox(); self.cmb_prov.setMinimumHeight(38)
        form.addRow("Proveedor:", self.cmb_prov)
        layout.addLayout(form)

        row = QHBoxLayout()
        self.cmb_med = QComboBox(); self.cmb_med.setMinimumHeight(36); self.cmb_med.setMinimumWidth(200)
        row.addWidget(self.cmb_med)
        row.addWidget(QLabel("Cant:"))
        self.spn_cant = QSpinBox(); self.spn_cant.setMinimum(1); self.spn_cant.setMaximum(99999); self.spn_cant.setMinimumHeight(36)
        row.addWidget(self.spn_cant)
        row.addWidget(QLabel("Precio:"))
        self.inp_precio = QLineEdit(); self.inp_precio.setPlaceholderText("0.00"); self.inp_precio.setMinimumHeight(36); self.inp_precio.setMaximumWidth(100)
        row.addWidget(self.inp_precio)
        btn_add = QPushButton("➕"); btn_add.setMinimumHeight(36); btn_add.setMaximumWidth(40)
        btn_add.clicked.connect(self._add_item); row.addWidget(btn_add)
        layout.addLayout(row)

        self.tbl = QTableWidget(); self.tbl.setColumnCount(5)
        self.tbl.setHorizontalHeaderLabels(["ID", "Medicamento", "Precio", "Cantidad", "Subtotal"])
        self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tbl.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl.verticalHeader().setVisible(False); self.tbl.setMaximumHeight(180)
        layout.addWidget(self.tbl)

        self.lbl_total = QLabel("Total: Q 0.00")
        self.lbl_total.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        self.lbl_total.setAlignment(Qt.AlignRight); layout.addWidget(self.lbl_total)

        self._load_combos()
        btns = QHBoxLayout(); btns.addStretch()
        bc = QPushButton("Cancelar"); bc.setMinimumHeight(38)
        bc.setStyleSheet(f"QPushButton {{ background: transparent; color: {COLORS['text_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}")
        bc.clicked.connect(self.reject); btns.addWidget(bc)
        bs = QPushButton("💾  Registrar Compra"); bs.setMinimumHeight(38); bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept); btns.addWidget(bs)
        layout.addLayout(btns)

    def _load_combos(self):
        try:
            for p in (DatabaseConnection.execute_query("SELECT id_proveedor, nombre FROM proveedores ORDER BY nombre", fetch_all=True) or []):
                self.cmb_prov.addItem(f"{p['id_proveedor']} - {p['nombre']}", p['id_proveedor'])
            for m in (DatabaseConnection.execute_query("SELECT id_medicamento, nombre FROM medicamentos ORDER BY nombre", fetch_all=True) or []):
                self.cmb_med.addItem(m['nombre'], m['id_medicamento'])
        except: pass

    def _add_item(self):
        mid = self.cmb_med.currentData()
        if not mid: return
        try: precio = float(self.inp_precio.text())
        except: QMessageBox.warning(self, "Aviso", "Precio inválido."); return
        cant = self.spn_cant.value(); sub = precio * cant
        self.items.append({"id": mid, "nombre": self.cmb_med.currentText(), "precio": precio, "cantidad": cant, "subtotal": sub})
        self.total += sub
        self.tbl.setRowCount(len(self.items))
        for i, it in enumerate(self.items):
            for j, v in enumerate([str(it['id']), it['nombre'], f"Q {it['precio']:.2f}", str(it['cantidad']), f"Q {it['subtotal']:.2f}"]):
                item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter); self.tbl.setItem(i, j, item)
        self.lbl_total.setText(f"Total: Q {self.total:,.2f}")

    def get_data(self):
        return {"id_proveedor": self.cmb_prov.currentData(), "items": self.items, "total": self.total}


class ComprasWidget(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        tabs = QTabWidget()
        self.compras_tab = ComprasTab(self.user_data)
        self.prov_tab = ProveedoresTab(self.user_data)
        tabs.addTab(self.compras_tab, "🏭  Compras")
        tabs.addTab(self.prov_tab, "📦  Proveedores")
        layout.addWidget(tabs)

    def refresh_data(self):
        self.compras_tab.refresh_data()
        self.prov_tab.refresh_data()


class ComprasTab(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="🏭  Órdenes de Compra", columns=["ID", "Proveedor", "Fecha", "Total"], user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT c.id_compra, p.nombre as proveedor, c.fecha, c.total
                FROM compras c JOIN proveedores p ON p.id_proveedor=c.id_proveedor
                ORDER BY c.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                for j, v in enumerate([str(r['id_compra']), r['proveedor'], str(r['fecha'])[:16], f"Q {r['total']:,.2f}"]):
                    item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter); self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = CompraDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['id_proveedor'] or not d['items']:
                QMessageBox.warning(self, "Aviso", "Seleccione proveedor y agregue medicamentos."); return
            try:
                cid = DatabaseConnection.execute_query(
                    "INSERT INTO compras (total, id_proveedor) VALUES (%s,%s)", (d['total'], d['id_proveedor']))
                for it in d['items']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO detalles_compras (cantidad, precio_compra, subtotal, id_compra, id_medicamento) VALUES (%s,%s,%s,%s,%s)",
                        (it['cantidad'], it['precio'], it['subtotal'], cid, it['id']))
                    DatabaseConnection.execute_query(
                        "UPDATE medicamentos SET stock = stock + %s WHERE id_medicamento = %s", (it['cantidad'], it['id']))
                QMessageBox.information(self, "Éxito", f"Compra #{cid} registrada."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        QMessageBox.information(self, "Info", "Las compras no se pueden editar.")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar compra #{data[0]}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM compras WHERE id_compra=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Compra eliminada."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")


class ProveedoresTab(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="📦  Proveedores", columns=["ID", "Nombre", "Dirección", "Correo"], user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("SELECT id_proveedor, nombre, direccion, correo FROM proveedores ORDER BY nombre", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                for j, v in enumerate([str(r['id_proveedor']), r['nombre'], r['direccion'], r['correo']]):
                    item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter); self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = ProveedorDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['nombre']:
                QMessageBox.warning(self, "Aviso", "Nombre obligatorio."); return
            try:
                pid = DatabaseConnection.execute_query(
                    "INSERT INTO proveedores (nombre, direccion, correo) VALUES (%s,%s,%s)",
                    (d['nombre'], d['direccion'], d['correo']))
                if d['telefono']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO telefonos_proveedores (telefono, id_proveedor) VALUES (%s,%s)", (d['telefono'], pid))
                QMessageBox.information(self, "Éxito", "Proveedor registrado."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        dlg = ProveedorDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                DatabaseConnection.execute_query("UPDATE proveedores SET nombre=%s, direccion=%s, correo=%s WHERE id_proveedor=%s",
                    (d['nombre'], d['direccion'], d['correo'], int(data[0])))
                QMessageBox.information(self, "Éxito", "Proveedor actualizado."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        if QMessageBox.question(self, "Confirmar", f"¿Eliminar '{data[1]}'?", QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM proveedores WHERE id_proveedor=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Proveedor eliminado."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
