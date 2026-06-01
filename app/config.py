"""
Configuración global del Sistema Farmacia Génesis.
"""

# ─────────────────────────────────────────────
# BASE DE DATOS
# ─────────────────────────────────────────────
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root123",   # Contraseña de MySQL
    "database": "farmacia_genesis",
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci",
    "autocommit": False,
    "pool_name": "farmacia_pool",
    "pool_size": 5,
}

# ─────────────────────────────────────────────
# APLICACIÓN
# ─────────────────────────────────────────────
APP_NAME = "Farmacia Génesis"
APP_SUBTITLE = "Sistema de Gestión"
APP_VERSION = "1.0.0"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 750

# ─────────────────────────────────────────────
# COLORES — Paleta Farmacia Génesis
# ─────────────────────────────────────────────
COLORS = {
    "primary":        "#E05050",   # Rojo coral  — botones, marca
    "primary_hover":  "#C43E3E",   # Rojo coral oscuro
    "primary_light":  "#F06060",   # Rojo coral claro
    "secondary":      "#4EC8D4",   # Turquesa   — íconos, bordes
    "secondary_hover":"#3AB0BC",   # Turquesa oscuro
    "bg_dark":        "#0D1B2A",   # Navy oscuro — fondo principal
    "bg_medium":      "#162032",   # Navy medio  — sidebar, cards
    "bg_light":       "#1B2A3E",   # Navy claro  — inputs, hover
    "bg_card":        "#1E2D42",   # Navy card   — tarjetas
    "text_primary":   "#E2E8F0",   # Blanco cálido — texto principal
    "text_secondary": "#94A3B8",   # Gris claro  — texto secundario
    "text_muted":     "#64748B",   # Gris oscuro — placeholders
    "success":        "#22C55E",   # Verde — éxito, stock OK
    "warning":        "#F59E0B",   # Naranja — alerta, stock bajo
    "danger":         "#EF4444",   # Rojo puro — error, eliminar
    "border":         "#2A3A50",   # Borde sutil
    "border_focus":   "#4EC8D4",   # Borde al hacer foco (turquesa)
}

# ─────────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────────
ROLE_ADMIN = "admin"
ROLE_MEDICO = "medico"
