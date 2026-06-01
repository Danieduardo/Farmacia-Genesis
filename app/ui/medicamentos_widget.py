"""
Medicamentos Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFormLayout, QTableWidgetItem, QComboBox
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class MedicamentoDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Medicamento" if data else "Nuevo Medicamento")
        self.setMinimumWidth(450)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.data = data
        self._setup_ui()
        if data:
            self._load(data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)

        title = QLabel("Editar Medicamento" if self.data else "Nuevo Medicamento")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)
        self.inp_nombre = QLineEdit()
        self.inp_nombre.setPlaceholderText("Nombre del medicamento")
        self.inp_nombre.setMinimumHeight(38)
        form.addRow("Nombre:", self.inp_nombre)

        self.inp_precio = QLineEdit()
        self.inp_precio.setPlaceholderText("0.00")
        self.inp_precio.setMinimumHeight(38)
        form.addRow("Precio (Q):", self.inp_precio)

        self.inp_stock = QLineEdit()
        self.inp_stock.setPlaceholderText("0")
        self.inp_stock.setMinimumHeight(38)
        form.addRow("Stock:", self.inp_stock)

        self.inp_descripcion = QLineEdit()
        self.inp_descripcion.setPlaceholderText("Descripción del medicamento")
        self.inp_descripcion.setMinimumHeight(38)
        form.addRow("Descripción:", self.inp_descripcion)

        self.inp_unidad = QComboBox()
        self.inp_unidad.addItems(["Tabletas", "Cápsulas", "Jarabe (ml)", "Frascos", "Ampollas", "Sobres", "Crema (g)", "Otro"])
        self.inp_unidad.setMinimumHeight(38)
        form.addRow("Unidad:", self.inp_unidad)

        self.inp_tipo = QLineEdit()
        self.inp_tipo.setPlaceholderText("Ej: Analgésico, Antibiótico...")
        self.inp_tipo.setMinimumHeight(38)
        form.addRow("Tipo:", self.inp_tipo)

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
        if len(data) > 2: self.inp_precio.setText(data[2])
        if len(data) > 3: self.inp_stock.setText(data[3])

    def get_data(self):
        return {
            "nombre": self.inp_nombre.text().strip(),
            "precio": self.inp_precio.text().strip(),
            "stock": self.inp_stock.text().strip(),
            "descripcion": self.inp_descripcion.text().strip(),
            "unidad": self.inp_unidad.currentText(),
            "tipo": self.inp_tipo.text().strip(),
        }


class MedicamentosWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="💊  Medicamentos",
                         columns=["ID", "Nombre", "Precio", "Stock", "Unidad"],
                         user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query(
                "SELECT id_medicamento, nombre, precio, stock, unidad_medida FROM medicamentos ORDER BY nombre",
                fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_medicamento']), r['nombre'], f"Q {r['precio']:,.2f}",
                        str(r['stock']), r.get('unidad_medida') or ""]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v)
                    item.setTextAlignment(Qt.AlignCenter)
                    # Color de stock
                    if j == 3:
                        stock = r['stock']
                        if stock < 5:
                            item.setForeground(Qt.red)
                        elif stock < 10:
                            item.setForeground(Qt.yellow)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar medicamentos: {e}")

    def on_add(self):
        dlg = MedicamentoDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['nombre'] or not d['precio']:
                QMessageBox.warning(self, "Aviso", "Nombre y precio son obligatorios.")
                return
            try:
                mid = DatabaseConnection.execute_query(
                    "INSERT INTO medicamentos (nombre, precio, stock, descripcion, unidad_medida) VALUES (%s,%s,%s,%s,%s)",
                    (d['nombre'], float(d['precio']), int(d['stock'] or 0), d['descripcion'], d['unidad']))
                if d['tipo']:
                    DatabaseConnection.execute_query(
                        "INSERT INTO tipos_medicamentos (nombre, descripcion, id_medicamento) VALUES (%s,%s,%s)",
                        (d['tipo'], d['tipo'], mid))
                QMessageBox.information(self, "Éxito", "Medicamento registrado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        dlg = MedicamentoDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                DatabaseConnection.execute_query(
                    "UPDATE medicamentos SET nombre=%s, precio=%s, stock=%s, descripcion=%s, unidad_medida=%s WHERE id_medicamento=%s",
                    (d['nombre'], float(d['precio']), int(d['stock'] or 0), d['descripcion'], d['unidad'], int(data[0])))
                QMessageBox.information(self, "Éxito", "Medicamento actualizado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar '{data[1]}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                DatabaseConnection.execute_query("DELETE FROM medicamentos WHERE id_medicamento=%s", (int(data[0]),))
                QMessageBox.information(self, "Éxito", "Medicamento eliminado.")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")
