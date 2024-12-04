# YouTube Transcript API

API para obtener transcripciones y datos de videos de YouTube. Proporciona endpoints para obtener tanto la transcripción como información básica de los videos.

## Características

- Obtención de transcripciones de videos de YouTube
- Soporte para múltiples idiomas
- Información detallada del video (título, canal, vistas, etc.)
- Contenedor Docker para fácil despliegue

## Requisitos

- Docker
- Docker Compose

## Instalación y Ejecución

1. Clona el repositorio:
   ```bash
   git clone https://github.com/julianponguta/youtube-transcript.git
   cd youtube-transcript
   ```

2. Construye y ejecuta los contenedores:
   ```bash
   docker-compose up -d
   ```

   El servicio estará disponible en el puerto 8081.

## Uso de la API

### 1. Obtener Transcripción

```bash
curl -X POST "http://localhost:8081/convert-transcript/" \
-H "Content-Type: application/json" \
-d '{
    "video_id": "ID_DEL_VIDEO",
    "language": "es"
}'
```

### 2. Obtener Información del Video

```bash
curl -X POST "http://localhost:8081/video-info/" \
-H "Content-Type: application/json" \
-d '{
    "video_id": "ID_DEL_VIDEO",
    "language": "es"
}'
```

La respuesta incluirá:
- Título del video
- Canal
- Duración
- Número de vistas
- Descripción
- Fecha de subida
- URL de la miniatura
- Número de likes (si está disponible)
- Número de comentarios (si está disponible)

## Ejemplos de Uso

### PowerShell
```powershell
$body = @{
    video_id = "6w9ZUzDkOTY"
    language = "es"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8081/video-info/" -Method Post -Body $body -ContentType "application/json"
```

### Linux/Mac
```bash
curl -X POST "http://localhost:8081/video-info/" \
-H "Content-Type: application/json" \
-d '{"video_id": "6w9ZUzDkOTY", "language": "es"}'
```

## Monitoreo

Para ver los logs del contenedor:
```bash
docker-compose logs -f
```

## Solución de Problemas

1. Si el puerto 8081 está en uso, puedes cambiarlo en el `docker-compose.yml`:
   ```yaml
   ports:
     - "NUEVO_PUERTO:8080"
   ```

2. Para reiniciar el servicio:
   ```bash
   docker-compose restart
   ```

## Tecnologías Utilizadas

- FastAPI
- youtube-transcript-api
- yt-dlp
- Docker
- Python 3.9

## Contribuir

1. Haz un Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request
