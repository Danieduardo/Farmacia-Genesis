# Sistema de Gestión de Farmacia "Génesis"

Sistema de escritorio para la administración y gestión de una farmacia, desarrollado en Python utilizando la biblioteca PySide6 (Qt) para la interfaz gráfica y MySQL como gestor de base de datos.

## Características Principales

*   **Autenticación y Seguridad:** Sistema de inicio de sesión seguro con contraseñas encriptadas mediante `bcrypt`.
*   **Gestión de Usuarios:** Control de roles y permisos (Administrador, Cajero, etc.).
*   **Gestión de Inventario:** Control de medicamentos, productos y alertas de stock.
*   **Punto de Venta (POS):** Registro de ventas y facturación.
*   **Reportes y Estadísticas:** Generación de reportes exportables a PDF (con `reportlab`) y visualización de gráficos (con `matplotlib`).
*   **Interfaz Moderna:** Diseño atractivo con tema oscuro gestionado mediante hojas de estilo (QSS).

## Requisitos del Sistema

*   **Python:** 3.8 o superior.
*   **Base de Datos:** MySQL Server (local o remoto).

## Instalación y Configuración

Sigue estos pasos para ejecutar el proyecto en tu entorno local:

1.  **Clonar o descargar el proyecto** y abrir una terminal en el directorio raíz (`Farmacia Proyecto`).

2.  **Crear y activar un entorno virtual** (recomendado para aislar las dependencias):
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # En Linux/macOS
    # En Windows usar: .venv\Scripts\activate
    ```

3.  **Instalar las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configurar la base de datos MySQL:**
    *   Asegúrate de que el servicio de MySQL esté corriendo.
    *   Ejecuta el script SQL incluido para crear la base de datos (`farmacia_genesis`) y sus tablas. Desde la terminal:
        ```bash
        mysql -u root -p < "base de datos de farmacia.sql"
        ```
    *   *(Opcional)*: Si tu usuario de MySQL no es `root` o tiene una contraseña diferente, actualiza las credenciales de conexión en el archivo `app/config.py`.

## Ejecución de la Aplicación

Para iniciar el sistema de farmacia, ejecuta el siguiente comando desde la raíz del proyecto (asegurándote de que el entorno virtual esté activado):

```bash
python3 -m app.main
```

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

*   `app/` - Contiene todo el código fuente de la aplicación.
    *   `main.py`: Punto de entrada principal (controlador de la aplicación).
    *   `config.py`: Configuraciones globales y credenciales.
    *   `assets/`: Archivos estáticos como estilos `.qss`, imágenes e iconos.
    *   `database/`: Módulos para la conexión a MySQL (Connection Pool).
    *   `services/`: Lógica de negocio (ej. `auth_service.py`).
    *   `ui/`: Archivos de interfaz de usuario, ventanas y componentes (PySide6).
    *   `utils/`: Herramientas auxiliares y funciones de uso general.
*   `base de datos de farmacia.sql` - Script completo para restaurar la estructura de la base de datos.
*   `requirements.txt` - Archivo con las librerías necesarias para el proyecto.
*   `SISTEMA PARA FARMACIA.pptx` / `Flujo.jpeg` - Documentación gráfica y presentaciones del flujo del sistema.

## Notas Adicionales

*   El sistema intentará verificar la conexión a la base de datos al iniciar. Si no puede conectarse, mostrará un mensaje de error indicando que se debe revisar el servicio de MySQL y las credenciales en `app/config.py`.
*   Si la base de datos se inicializa correctamente, el sistema creará automáticamente un usuario administrador por defecto si este no existe.
