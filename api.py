from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter
from pydantic import BaseModel
from typing import Optional
import yt_dlp
from fastapi.middleware.cors import CORSMiddleware  # Importa CORSMiddleware

app = FastAPI(title="Transcript Converter API")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite solicitudes de cualquier origen
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos HTTP
    allow_headers=["*"],  # Permite todos los encabezados
)

class TranscriptRequest(BaseModel):
    video_id: str
    language: Optional[str] = 'es'

class TranscriptResponse(BaseModel):
    converted_text: str

class VideoInfoResponse(BaseModel):
    title: str
    channel: str
    duration: str
    view_count: int
    description: str
    upload_date: str
    thumbnail: str
    like_count: Optional[int]
    comment_count: Optional[int]

def convert_time_format(text: str) -> str:
    # Function to convert time format
    def convert_time(time_str):
        # Remove milliseconds and keep only hours:minutes:seconds
        return time_str.split('.')[0]

    # Split the text into lines and process
    lines = text.split('\n')
    result_parts = []
    
    i = 0
    while i < len(lines):
        if '-->' in lines[i]:
            # Get time range
            start_time, end_time = lines[i].split(' --> ')
            time_str = f"{convert_time(start_time)} -> {convert_time(end_time)}"
            # Get next line (subtitle text)
            if i + 1 < len(lines):
                subtitle_text = lines[i + 1].strip()
                if subtitle_text:  # Only add if there's actual text
                    result_parts.append(f"{time_str} {subtitle_text}")
                i += 1
        i += 1

    # Join all parts with a single space
    return ' '.join(part for part in result_parts if part.strip())

def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} minutos {remaining_seconds} segundos"

def format_date(date_str: str) -> str:
    # date_str viene en formato YYYYMMDD
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

@app.post("/convert-transcript/", response_model=TranscriptResponse)
async def convert_transcript(request: TranscriptRequest):
    try:
        # Get transcript from YouTube
        transcript = YouTubeTranscriptApi.get_transcript(request.video_id, languages=[request.language])
        
        # Format to WebVTT
        formatter = WebVTTFormatter()
        text = formatter.format_transcript(transcript)
        
        # Remove WEBVTT header
        text = text.replace("WEBVTT", "")
        
        # Convert time format
        converted_text = convert_time_format(text)
        
        return {"converted_text": converted_text}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/video-info/", response_model=VideoInfoResponse)
async def get_video_info(request: TranscriptRequest):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://www.youtube.com/watch?v={request.video_id}"
            info = ydl.extract_info(url, download=False)
            
            return VideoInfoResponse(
                title=info.get('title', ''),
                channel=info.get('channel', ''),
                duration=format_duration(info.get('duration', 0)),
                view_count=info.get('view_count', 0),
                description=info.get('description', ''),
                upload_date=format_date(info.get('upload_date', '')),
                thumbnail=info.get('thumbnail', ''),
                like_count=info.get('like_count'),
                comment_count=info.get('comment_count')
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Welcome to Transcript Converter API. Use POST /convert-transcript/ to convert YouTube transcripts."}
