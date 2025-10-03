# KDX Pi Signage 2

Sistema multiplataforma de cartelería digital para Raspberry Pi.

## Instalación

1. Clona el repositorio:
```bash
git clone <repository-url>
cd kdx-pi-signage-2
```

2. Instala dependencias con uv:
```bash
uv sync
```

3. Configura las variables de entorno:
```bash
cp .env.example .env
# Edita .env con tus credenciales
```

4. Ejecuta la aplicación:
```bash
uv run main.py
```

## Configuración

### Variables de Entorno Requeridas

- `GOOGLE_DRIVE_FOLDER_ID`: ID de la carpeta de Google Drive con videos
- `GOOGLE_APPLICATION_CREDENTIALS`: Ruta al archivo de credenciales de Google

### Variables de Entorno Opcionales

- `CACHE_DIR`: Directorio de caché (por defecto: `cache`)
- `LOGS_DIR`: Directorio de logs (por defecto: `logs`)
- `SYNC_INTERVAL`: Intervalo de sincronización en segundos (por defecto: `30`)
- `LOG_LEVEL`: Nivel de logging (por defecto: `INFO`)

## Uso

El sistema se ejecuta como un servicio que:

1. Sincroniza videos desde Google Drive al caché local
2. Reproduce videos en pantalla completa usando VLC
3. Monitorea cambios en Google Drive y actualiza automáticamente
4. Registra toda la actividad en logs organizados por fecha

## Arquitectura

- **Core**: Entidades de dominio (Video, Playlist)
- **Application**: Casos de uso (PlaybackService)
- **Infrastructure**: Adaptadores externos (GoogleDriveRepository, VLCPlayer)

## Documentación

Consulta la documentación técnica en la carpeta `docs/`:

- [01-project-overview.md](docs/01-project-overview.md) - Visión general del proyecto
- [02-architecture.md](docs/02-architecture.md) - Arquitectura del sistema
- [03-technical-specifications.md](docs/03-technical-specifications.md) - Especificaciones técnicas

## Desarrollo

Para desarrollo con dependencias adicionales:

```bash
uv sync --dev
```

## YouTube Support (Bonus)

Para soporte de YouTube, instala las dependencias opcionales:

```bash
uv sync --extra youtube
```

## Licencia

MIT