# YouTube Transcript API

API para obtener y convertir transcripciones de videos de YouTube.

## Requisitos

- Docker
- Docker Compose

## Instrucciones de Despliegue

1. Clona este repositorio en tu servidor:
   ```bash
   git clone <tu-repositorio>
   cd youtube-transcript
   ```

2. Construye y ejecuta los contenedores:
   ```bash
   docker-compose up -d
   ```

   El servicio estará disponible en el puerto 8080.

3. Para detener el servicio:
   ```bash
   docker-compose down
   ```

## Uso de la API

### Obtener transcripción de un video

```bash
curl -X POST "http://localhost:8080/convert-transcript/" \
-H "Content-Type: application/json" \
-d '{
    "video_id": "ID_DEL_VIDEO",
    "language": "es"
}'
```

Ejemplo en PowerShell:
```powershell
$body = @{
    video_id = "ID_DEL_VIDEO"
    language = "es"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8080/convert-transcript/" -Method Post -Body $body -ContentType "application/json"
```

### Parámetros

- `video_id`: ID del video de YouTube (requerido)
- `language`: Código del idioma (opcional, por defecto "es")

## Monitoreo

Para ver los logs del contenedor:
```bash
docker-compose logs -f
```

## Solución de Problemas

1. Si el puerto 8080 está en uso, puedes cambiarlo en el `docker-compose.yml`:
   ```yaml
   ports:
     - "NUEVO_PUERTO:8080"
   ```

2. Para reiniciar el servicio:
   ```bash
   docker-compose restart
   ```
