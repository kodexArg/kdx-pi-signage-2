# Especificaciones Técnicas

## Tecnologías Principales

### Python Runtime
- **Versión**: Python 3.8+
- **Gestor de paquetes**: uv
- **Ejecución**: `uv run main.py`

### Reproductor Multimedia
- **VLC Media Player**: Para reproducción de videos
- **Modo headless**: Sin interfaz gráfica
- **Plataformas**: Linux (Raspberry Pi), Windows

### Almacenamiento en Nube
- **Google Drive API**: Para sincronización de videos
- **Autenticación**: OAuth 2.0 / Service Account
- **Monitoreo**: Detección de cambios en tiempo real

## Dependencias de Producción

### Core Dependencies
```toml
# pyproject.toml
[project]
dependencies = [
    "python-vlc>=3.0.0",
    "google-api-python-client>=2.0.0",
    "google-auth>=2.0.0",
    "google-auth-oauthlib>=1.0.0",
    "google-auth-httplib2>=0.1.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
    "asyncio>=3.4.3",
    "aiofiles>=23.0.0",
]
```

### Development Dependencies
```toml
[tool.uv.dev-dependencies]
pytest = ">=7.0.0"
black = ">=23.0.0"
isort = ">=5.12.0"
mypy = ">=1.0.0"
```

### Bonus: YouTube Support
```toml
# Optional: Para soporte de YouTube
yt-dlp = ">=2023.0.0"
```

## Configuración del Sistema

### Variables de Entorno (.env)
```bash
# Google Drive Configuration
GOOGLE_DRIVE_FOLDER_ID=your_folder_id_here
GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json

# Application Configuration
CACHE_DIR=cache
LOGS_DIR=logs
VIDEO_EXTENSIONS=.mp4,.avi,.mov,.mkv

# VLC Configuration
VLC_VERBOSE_LEVEL=0
VLC_FULLSCREEN=true
```

### Configuración de Aplicación (pyproject.toml)
```toml
[tool.kdx_pi_signage]
# Sync configuration
sync_interval = 30  # seconds
max_retries = 3
timeout = 10  # seconds

# Playback configuration
video_check_interval = 5  # seconds
max_video_duration = 3600  # seconds

# Logging configuration
log_level = "INFO"
log_max_file_size = "10MB"
log_backup_count = 7
```

## Estructura del Caché

### Organización de Archivos
```
cache/
├── videos/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
├── metadata/
│   ├── video1.json
│   ├── video2.json
│   └── ...
└── temp/
    ├── downloading/
    └── processing/
```

### Metadata de Video
```json
{
  "id": "unique_video_id",
  "name": "video_name.mp4",
  "size": 104857600,
  "modified_time": "2024-01-01T12:00:00Z",
  "drive_id": "google_drive_file_id",
  "local_path": "cache/videos/video_name.mp4",
  "checksum": "sha256_hash"
}
```

## Sistema de Logging

### Estructura de Logs
```
logs/
├── 2024/
│   ├── 01/
│   │   ├── 01.log
│   │   ├── 02.log
│   │   └── ...
│   └── 02/
│       └── ...
└── latest.log -> logs/2024/01/01.log
```

### Formato de Log
```
[2024-01-01 12:00:00] INFO: Video synchronization started
[2024-01-01 12:00:01] INFO: Found 5 videos in Google Drive
[2024-01-01 12:00:02] INFO: Downloaded new_video.mp4 (50.2 MB)
[2024-01-01 12:05:00] INFO: Playing video: advertisement.mp4
[2024-01-01 12:10:00] INFO: Video completed: advertisement.mp4
```

### Niveles de Log
- **CRITICAL**: Fallos que detienen el sistema
- **ERROR**: Errores que requieren atención
- **WARNING**: Problemas solucionables automáticamente
- **INFO**: Eventos normales del sistema
- **DEBUG**: Información detallada para debugging

## Sincronización con Google Drive

### Proceso de Sincronización
1. **Consulta**: Obtener lista de archivos actual
2. **Comparación**: Comparar con caché local
3. **Descarga**: Descargar archivos nuevos/modificados
4. **Limpieza**: Eliminar archivos obsoletos
5. **Verificación**: Validar integridad de archivos

### Estrategia de Deltas
- **Checksums**: Para detectar cambios en archivos
- **Timestamps**: Para determinar orden de modificación
- **Batch processing**: Para optimizar transferencias

## Reproducción de Videos

### Modo de Reproducción
- **Pantalla completa**: Siempre maximizado
- **Sin bordes**: Ocultar controles del sistema
- **Loop automático**: Transición seamless entre videos
- **Error recovery**: Continuar con siguiente video si hay error

### Control de VLC
```python
import vlc

class VLCPlayer:
    def __init__(self):
        self.instance = vlc.Instance([
            '--fullscreen',
            '--no-video-title-show',
            '--mouse-hide-timeout=0'
        ])
        self.player = self.instance.media_player_new()
```

## Manejo de Errores

### Categorías de Error
1. **NetworkError**: Problemas de conectividad
2. **FileError**: Errores de archivo o permisos
3. **PlaybackError**: Errores durante reproducción
4. **ConfigurationError**: Problemas de configuración

### Estrategia de Recuperación
- **Reintentos exponenciales** para errores temporales
- **Fallback automático** a videos locales
- **Estado degradado** cuando servicios externos fallan
- **Alertas automáticas** para errores críticos