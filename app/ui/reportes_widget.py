"""
Reportes Widget — Farmacia Génesis
Consulta de recetas, facturas y generación de PDF.
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QMessageBox, QTableWidgetItem, QComboBox, QLineEdit,
    QTabWidget, QFrame, QScrollArea, QFileDialog
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.ui.base_crud_widget import BaseCrudWidget
from app.database.connection import DatabaseConnection


class ReportesWidget(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        tabs = QTabWidget()
        self.recetas_tab = RecetasTab(self.user_data)
        self.facturas_tab = FacturasTab(self.user_data)
        tabs.addTab(self.recetas_tab, "📋  Recetas")
        tabs.addTab(self.facturas_tab, "🧾  Facturas / Ventas")
        layout.addWidget(tabs)

    def refresh_data(self):
        self.recetas_tab.refresh_data()
        self.facturas_tab.refresh_data()


class RecetasTab(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="📋  Recetas Médicas",
                         columns=["ID", "Paciente", "Médico", "Diagnóstico", "Fecha"],
                         user_data=user_data)
        self.btn_add.hide()
        self.btn_delete.hide()

        # Reemplazar editar por "Ver / Imprimir"
        self.btn_edit.setText("📄  Ver / Imprimir PDF")
        self.btn_edit.setStyleSheet(f"""QPushButton {{ background-color: {COLORS['primary']}; color: #fff;
            border: none; border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px 16px; }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}""")
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT r.id_receta, p.nombre_completo as paciente, m.nombre as medico,
                       c.diagnostico, r.fecha
                FROM recetas r
                JOIN consultas c ON c.id_consulta=r.id_consulta
                JOIN pacientes p ON p.id_paciente=c.id_paciente
                JOIN medicos m ON m.id_medico=c.id_medico
                ORDER BY r.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_receta']), r['paciente'], r['medico'],
                        r['diagnostico'][:40], str(r['fecha'])[:16]]
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        self._generate_receta_pdf(int(data[0]))

    def _generate_receta_pdf(self, id_receta):
        try:
            receta = DatabaseConnection.execute_query("""
                SELECT r.id_receta, r.fecha, c.diagnostico, c.tratamiento,
                       p.nombre_completo as paciente, p.edad, p.genero,
                       m.nombre as medico, m.especialidad
                FROM recetas r
                JOIN consultas c ON c.id_consulta=r.id_consulta
                JOIN pacientes p ON p.id_paciente=c.id_paciente
                JOIN medicos m ON m.id_medico=c.id_medico
                WHERE r.id_receta=%s""", (id_receta,), fetch_one=True)

            detalles = DatabaseConnection.execute_query("""
                SELECT dr.cantidad, dr.dosis, med.nombre as medicamento
                FROM detalles_recetas dr
                JOIN medicamentos med ON med.id_medicamento=dr.id_medicamento
                WHERE dr.id_receta=%s""", (id_receta,), fetch_all=True) or []

            if not receta:
                QMessageBox.warning(self, "Error", "Receta no encontrada."); return

            path, _ = QFileDialog.getSaveFileName(self, "Guardar Receta PDF", f"Receta_{id_receta}.pdf", "PDF (*.pdf)")
            if not path: return

            from app.services.pdf_service import PDFService
            PDFService.generate_receta(receta, detalles, path)
            QMessageBox.information(self, "Éxito", f"Receta guardada en:\n{path}")
        except ImportError:
            QMessageBox.warning(self, "Aviso", "Módulo PDF no disponible. Instale reportlab.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando PDF: {e}")


class FacturasTab(BaseCrudWidget):
    def __init__(self, user_data=None):
        super().__init__(title="🧾  Facturas de Venta",
                         columns=["ID Venta", "Paciente", "Fecha", "Total", "Método Pago"],
                         user_data=user_data)
        self.btn_add.hide()
        self.btn_delete.hide()
        self.btn_edit.setText("📄  Generar Factura PDF")
        self.btn_edit.setStyleSheet(f"""QPushButton {{ background-color: {COLORS['primary']}; color: #fff;
            border: none; border-radius: 8px; font-size: 13px; font-weight: bold; padding: 8px 16px; }}
            QPushButton:hover {{ background-color: {COLORS['primary_hover']}; }}""")
        self.refresh_data()

    def refresh_data(self):
        try:
            data = DatabaseConnection.execute_query("""
                SELECT v.id_venta, p.nombre_completo as paciente, v.fecha, v.total,
                    (SELECT mp.tipo FROM metodos_pagos mp JOIN pagos pg ON pg.id_pago=mp.id_pago
                     WHERE pg.id_venta=v.id_venta LIMIT 1) as metodo
                FROM ventas v JOIN pacientes p ON p.id_paciente=v.id_paciente
                ORDER BY v.fecha DESC""", fetch_all=True) or []
            self.table.setRowCount(len(data))
            for i, r in enumerate(data):
                vals = [str(r['id_venta']), r['paciente'], str(r['fecha'])[:16],
                        f"Q {r['total']:,.2f}", r.get('metodo') or 'N/A']
                for j, v in enumerate(vals):
                    item = QTableWidgetItem(v); item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(i, j, item)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error: {e}")

    def on_edit(self):
        data = self.get_selected_row_data()
        if not data: return
        self._generate_factura_pdf(int(data[0]))

    def _generate_factura_pdf(self, id_venta):
        try:
            venta = DatabaseConnection.execute_query("""
                SELECT v.id_venta, v.fecha, v.total, p.nombre_completo as paciente
                FROM ventas v JOIN pacientes p ON p.id_paciente=v.id_paciente
                WHERE v.id_venta=%s""", (id_venta,), fetch_one=True)

            detalles = DatabaseConnection.execute_query("""
                SELECT dv.cantidad, dv.precio_unitario, dv.subtotal, m.nombre as medicamento
                FROM detalles_ventas dv JOIN medicamentos m ON m.id_medicamento=dv.id_medicamento
                WHERE dv.id_venta=%s""", (id_venta,), fetch_all=True) or []

            if not venta:
                QMessageBox.warning(self, "Error", "Venta no encontrada."); return

            path, _ = QFileDialog.getSaveFileName(self, "Guardar Factura PDF", f"Factura_{id_venta}.pdf", "PDF (*.pdf)")
            if not path: return

            from app.services.pdf_service import PDFService
            PDFService.generate_factura(venta, detalles, path)
            QMessageBox.information(self, "Éxito", f"Factura guardada en:\n{path}")
        except ImportError:
            QMessageBox.warning(self, "Aviso", "Módulo PDF no disponible. Instale reportlab.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error generando PDF: {e}")
