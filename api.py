from fastapi import FastAPI, HTTPException
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import WebVTTFormatter
from pydantic import BaseModel
from typing import Optional
import yt_dlp
from fastapi.middleware.cors import CORSMiddleware  

app = FastAPI(title="Transcript & Video Info API")

# Habilitar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
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

class FullVideoInfoResponse(VideoInfoResponse, TranscriptResponse):
    pass  # Esta clase hereda la estructura de las dos anteriores

def convert_time_format(text: str) -> str:
    def convert_time(time_str):
        return time_str.split('.')[0]  # Elimina milisegundos

    lines = text.split('\n')
    result_parts = []
    
    i = 0
    while i < len(lines):
        if '-->' in lines[i]:
            start_time, end_time = lines[i].split(' --> ')
            time_str = f"{convert_time(start_time)} -> {convert_time(end_time)}"
            if i + 1 < len(lines):
                subtitle_text = lines[i + 1].strip()
                if subtitle_text:
                    result_parts.append(f"{time_str} {subtitle_text}")
                i += 1
        i += 1

    return ' '.join(part for part in result_parts if part.strip())

def format_duration(seconds: int) -> str:
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes} minutos {remaining_seconds} segundos"

def format_date(date_str: Optional[str]) -> str:
    if not date_str:
        return "Fecha no disponible"
    return f"{date_str[:4]}/{date_str[4:6]}/{date_str[6:]}"

async def get_video_transcript(video_id: str, language: str):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=[language])
    except Exception:
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    formatter = WebVTTFormatter()
    text = formatter.format_transcript(transcript).replace("WEBVTT", "")
    return convert_time_format(text)

async def get_video_metadata(video_id: str):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            url = f"https://www.youtube.com/watch?v={video_id}"
            info = ydl.extract_info(url, download=False)
            
            return {
                "title": info.get('title', ''),
                "channel": info.get('uploader', ''),  
                "duration": format_duration(info.get('duration', 0)),
                "view_count": info.get('view_count', 0),
                "description": info.get('description', ''),
                "upload_date": format_date(info.get('upload_date')),
                "thumbnail": info.get('thumbnail', ''),
                "like_count": info.get('like_count'),
                "comment_count": info.get('comment_count')
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/convert-transcript/", response_model=TranscriptResponse)
async def convert_transcript(request: TranscriptRequest):
    converted_text = await get_video_transcript(request.video_id, request.language)
    return {"converted_text": converted_text}

@app.post("/video-info/", response_model=VideoInfoResponse)
async def get_video_info(request: TranscriptRequest):
    return await get_video_metadata(request.video_id)

@app.post("/video-full-info/", response_model=FullVideoInfoResponse)
async def get_full_video_info(request: TranscriptRequest):
    metadata = await get_video_metadata(request.video_id)
    transcript = await get_video_transcript(request.video_id, request.language)
    return {**metadata, "converted_text": transcript}

@app.get("/")
async def root():
    return {"message": "Welcome to Transcript & Video Info API. Use POST /video-full-info/ to get full details."}
