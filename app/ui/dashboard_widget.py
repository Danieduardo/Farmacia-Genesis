"""
Dashboard Widget — Farmacia Génesis
"""
# pyrefly: ignore [missing-import]
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy
)
# pyrefly: ignore [missing-import]
from PySide6.QtCore import Qt
from app.config import COLORS
from app.database.connection import DatabaseConnection
from datetime import datetime


class DashboardWidget(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        self._setup_ui()
        self.refresh_data()

    def _create_stat_card(self, label, value, icon, color):
        card = QFrame()
        card.setStyleSheet(f"""QFrame {{ background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']};
            border-radius: 12px; padding: 16px; border-left: 4px solid {color}; }}""")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        card.setMinimumHeight(100)
        ly = QVBoxLayout(card)
        ly.setSpacing(6)
        ic = QLabel(icon)
        ic.setStyleSheet("font-size: 24px; background: transparent;")
        ly.addWidget(ic)
        vl = QLabel(value)
        vl.setObjectName(f"sv_{label}")
        vl.setStyleSheet(f"font-size: 26px; font-weight: bold; color: {COLORS['text_primary']}; background: transparent;")
        ly.addWidget(vl)
        tl = QLabel(label)
        tl.setStyleSheet(f"font-size: 11px; color: {COLORS['text_secondary']}; background: transparent;")
        ly.addWidget(tl)
        return card

    def _update_stat(self, card, value):
        for ch in card.findChildren(QLabel):
            if ch.objectName().startswith("sv_"):
                ch.setText(value)
                break

    def _setup_ui(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        content = QWidget()
        content.setStyleSheet("background: transparent;")
        self.ml = QVBoxLayout(content)
        self.ml.setContentsMargins(24, 20, 24, 20)
        self.ml.setSpacing(20)

        hl = QHBoxLayout()
        t = QLabel("Dashboard")
        t.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['text_primary']}; background: transparent;")
        hl.addWidget(t)
        hl.addStretch()
        dl = QLabel(datetime.now().strftime("📅  %d/%m/%Y"))
        dl.setStyleSheet(f"font-size: 14px; color: {COLORS['text_secondary']}; background: transparent;")
        hl.addWidget(dl)
        self.ml.addLayout(hl)

        sl = QHBoxLayout()
        sl.setSpacing(16)
        self.sv = self._create_stat_card("Ventas Hoy", "Q 0.00", "🛒", COLORS['primary'])
        self.sp = self._create_stat_card("Pacientes Hoy", "0", "👥", COLORS['secondary'])
        self.ss = self._create_stat_card("Stock Bajo", "0", "⚠️", COLORS['warning'])
        self.sc = self._create_stat_card("Citas Pendientes", "0", "📅", "#6366F1")
        sl.addWidget(self.sv)
        sl.addWidget(self.sp)
        sl.addWidget(self.ss)
        sl.addWidget(self.sc)
        self.ml.addLayout(sl)

        ac = QFrame()
        ac.setStyleSheet(f"QFrame {{ background-color: {COLORS['bg_card']}; border: 1px solid {COLORS['border']}; border-radius: 12px; padding: 20px; }}")
        al = QVBoxLayout(ac)
        at = QLabel("🔔  Alertas del Sistema")
        at.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['text_primary']}; background: transparent;")
        al.addWidget(at)
        self.alc = QVBoxLayout()
        al.addLayout(self.alc)
        self.nal = QLabel("✅  No hay alertas pendientes")
        self.nal.setStyleSheet(f"font-size: 14px; color: {COLORS['success']}; background: transparent; padding: 12px;")
        self.alc.addWidget(self.nal)
        self.ml.addWidget(ac)

        self.sl = QLabel("Cargando datos...")
        self.sl.setStyleSheet(f"font-size: 13px; color: {COLORS['text_secondary']}; background: transparent; padding: 8px;")
        self.sl.setWordWrap(True)
        self.ml.addWidget(self.sl)
        self.ml.addStretch()

        scroll.setWidget(content)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(scroll)

    def refresh_data(self):
        try:
            r = DatabaseConnection.execute_query("SELECT COALESCE(SUM(total),0) as t FROM ventas WHERE DATE(fecha)=CURDATE()", fetch_one=True)
            self._update_stat(self.sv, f"Q {r['t']:,.2f}" if r else "Q 0.00")
            r = DatabaseConnection.execute_query("SELECT COUNT(*) as t FROM pacientes WHERE DATE(fecha_registro)=CURDATE()", fetch_one=True)
            self._update_stat(self.sp, str(r['t'] if r else 0))
            r = DatabaseConnection.execute_query("SELECT COUNT(*) as t FROM medicamentos WHERE stock < 10", fetch_one=True)
            sb = r['t'] if r else 0
            self._update_stat(self.ss, str(sb))
            r = DatabaseConnection.execute_query("SELECT COUNT(DISTINCT c.id_cita) as t FROM citas c JOIN estados_citas ec ON ec.id_cita=c.id_cita WHERE ec.nombre='Pendiente' AND DATE(c.fecha)>=CURDATE()", fetch_one=True)
            self._update_stat(self.sc, str(r['t'] if r else 0))
            tm = DatabaseConnection.execute_query("SELECT COUNT(*) as t FROM medicamentos", fetch_one=True)
            tp = DatabaseConnection.execute_query("SELECT COUNT(*) as t FROM pacientes", fetch_one=True)
            td = DatabaseConnection.execute_query("SELECT COUNT(*) as t FROM medicos", fetch_one=True)
            self.sl.setText(f"📦 {tm['t'] if tm else 0} medicamentos  •  👥 {tp['t'] if tp else 0} pacientes  •  👨‍⚕️ {td['t'] if td else 0} médicos")
            if sb > 0:
                self.nal.hide()
        except Exception as e:
            self.sl.setText(f"⚠️ Error: {str(e)[:80]}")
