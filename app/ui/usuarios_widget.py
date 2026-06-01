"""
Usuarios Widget — Farmacia Génesis (Solo Admin)
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
from app.services.auth_service import AuthService
from app.database.connection import DatabaseConnection


class UsuarioDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowTitle("Usuario")
        self.setMinimumWidth(420)
        self.setStyleSheet(f"background-color: {COLORS['bg_medium']};")
        self.data = data
        self._setup_ui()
        if data: self._load(data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 20, 24, 20)
        title = QLabel("👤  Usuario")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {COLORS['primary']}; background: transparent;")
        layout.addWidget(title)
        form = QFormLayout(); form.setSpacing(10)
        self.inp_user = QLineEdit(); self.inp_user.setMinimumHeight(38); self.inp_user.setPlaceholderText("Nombre de usuario")
        form.addRow("Usuario:", self.inp_user)
        self.inp_pass = QLineEdit(); self.inp_pass.setMinimumHeight(38); self.inp_pass.setPlaceholderText("Contraseña")
        self.inp_pass.setEchoMode(QLineEdit.Password)
        form.addRow("Contraseña:", self.inp_pass)
        self.inp_nombre = QLineEdit(); self.inp_nombre.setMinimumHeight(38); self.inp_nombre.setPlaceholderText("Nombre completo")
        form.addRow("Nombre:", self.inp_nombre)
        self.cmb_rol = QComboBox(); self.cmb_rol.addItems(["admin", "medico"]); self.cmb_rol.setMinimumHeight(38)
        form.addRow("Rol:", self.cmb_rol)
        self.cmb_medico = QComboBox(); self.cmb_medico.setMinimumHeight(38)
        self.cmb_medico.addItem("-- Ninguno --", None)
        form.addRow("Vincular médico:", self.cmb_medico)
        layout.addLayout(form)
        if self.data:
            self.inp_pass.setPlaceholderText("Dejar vacío para no cambiar")
        self._load_medicos()
        btns = QHBoxLayout(); btns.addStretch()
        bc = QPushButton("Cancelar"); bc.setMinimumHeight(38)
        bc.setStyleSheet(f"QPushButton {{ background: transparent; color: {COLORS['text_secondary']}; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 20px; }}")
        bc.clicked.connect(self.reject); btns.addWidget(bc)
        bs = QPushButton("💾  Guardar"); bs.setMinimumHeight(38); bs.setCursor(Qt.PointingHandCursor)
        bs.clicked.connect(self.accept); btns.addWidget(bs)
        layout.addLayout(btns)

    def _load_medicos(self):
        try:
            for m in (DatabaseConnection.execute_query("SELECT id_medico, nombre FROM medicos ORDER BY nombre", fetch_all=True) or []):
                self.cmb_medico.addItem(f"{m['id_medico']} - {m['nombre']}", m['id_medico'])
        except: pass

    def _load(self, d):
        if len(d)>1: self.inp_user.setText(d[1])
        if len(d)>3: self.inp_nombre.setText(d[3])
        if len(d)>2:
            idx = self.cmb_rol.findText(d[2])
            if idx >= 0: self.cmb_rol.setCurrentIndex(idx)

    def get_data(self):
        return {"usuario": self.inp_user.text().strip(), "password": self.inp_pass.text(),
                "nombre": self.inp_nombre.text().strip(), "rol": self.cmb_rol.currentText(),
                "id_medico": self.cmb_medico.currentData()}


class UsuariosWidget(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="👤  Gestión de Usuarios",
                         columns=["ID", "Usuario", "Rol", "Nombre", "Activo", "Último Acceso"],
                         user_data=user_data)
        self.refresh_data()

    def refresh_data(self):
        try:
            data = AuthService.get_all_users()
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_usuario']), r['nombre_usuario'], r['rol'], r['nombre_completo'],
                        "✅ Sí" if r['activo'] else "❌ No",
                        str(r['ultimo_acceso'])[:16] if r.get('ultimo_acceso') else "Nunca"]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_add(self):
        dlg = UsuarioDialog(self)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            if not d['usuario'] or not d['password'] or not d['nombre']:
                QMessageBox.warning(self, "Aviso", "Todos los campos son obligatorios."); return
            try:
                AuthService.create_user(d['usuario'], d['password'], d['rol'], d['nombre'], d['id_medico'])
                QMessageBox.information(self, "Éxito", "Usuario creado."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        dlg = UsuarioDialog(self, data)
        if dlg.exec() == QDialog.Accepted:
            d = dlg.get_data()
            try:
                DatabaseConnection.execute_query(
                    "UPDATE usuarios SET nombre_usuario=%s, rol=%s, nombre_completo=%s, id_medico=%s WHERE id_usuario=%s",
                    (d['usuario'], d['rol'], d['nombre'], d['id_medico'], int(data[0])))
                if d['password']:
                    AuthService.change_password(int(data[0]), d['password'])
                QMessageBox.information(self, "Éxito", "Usuario actualizado."); self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error: {e}")

    def on_delete(self):
        data = self.get_selected_row_data()
        if not data: return
        if data[1] == "admin":
            QMessageBox.warning(self, "Aviso", "No se puede eliminar el admin principal."); return
        # En lugar de eliminar, desactivar
        try:
            is_active = data[4] == "✅ Sí"
            AuthService.toggle_user_active(int(data[0]), not is_active)
            action = "desactivado" if is_active else "activado"
            QMessageBox.information(self, "Éxito", f"Usuario {action}."); self.refresh_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error: {e}")
