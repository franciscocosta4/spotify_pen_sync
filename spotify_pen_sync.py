#!/usr/bin/env python3
"""
Sincronizador Spotify Pen - Sincroniza playlists do Spotify com uma pen USB
Versao 2.0 - Com correcoes para playlists privadas e melhor tratamento de erros
"""

import os
import sys
import json
import re
import time
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional
from datetime import datetime
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from yt_dlp import YoutubeDL

# ============================================
# CONFIGURACAO - AJUSTE AQUI!
# ============================================

CONFIG = {
    # Spotify API (obter em https://developer.spotify.com/dashboard)
    "SPOTIFY_CLIENT_ID": "",
    "SPOTIFY_CLIENT_SECRET": "",
    "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
    
    # Caminho da pen USB (ex: "D:/" no Windows, "/media/usb" no Linux)
    "PEN_DRIVE_PATH": "D:/",
    
    # Playlists do Spotify (URLs ou IDs)
    "PLAYLISTS": [
        "https://open.spotify.com/playlist/...",
    ],
    
    # Configuracoes do YouTube Download
    "YT_DOWNLOAD_OPTIONS": {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
    },
    
    "MAX_RETRIES": 3,
    "SLEEP_BETWEEN_DOWNLOADS": 2,
    "LOG_FILE": "sync_log.txt",
}

# ============================================
# CLASSE PRINCIPAL
# ============================================

class SpotifyPenSync:
    def __init__(self, config: Dict):
        self.config = config
        self.spotify_client = None
        self.setup_logging()
        self.setup_spotify()
        
    def setup_logging(self):
        """Configura o sistema de registo"""
        log_path = Path(self.config["LOG_FILE"])
        self.log_file = log_path
        if not log_path.exists():
            log_path.touch()
            
    def log(self, message: str, level: str = "INFO"):
        """Regista mensagens no ficheiro e na consola"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}"
        
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        print(log_entry)
        
    def setup_spotify(self):
        """Configura a ligacao com a API do Spotify"""
        try:
            scope = "playlist-read-private playlist-read-collaborative"
            
            self.spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=self.config["SPOTIFY_CLIENT_ID"],
                client_secret=self.config["SPOTIFY_CLIENT_SECRET"],
                redirect_uri=self.config["SPOTIFY_REDIRECT_URI"],
                scope=scope,
                cache_path=".spotify_cache",
                requests_timeout=30
            ))
            
            user = self.spotify_client.current_user()
            self.log(f"Ligacao ao Spotify estabelecida como: {user['display_name']}")
            return True
            
        except Exception as e:
            self.log(f"Erro ao ligar ao Spotify: {e}", "ERROR")
            return False
    
    def get_playlist_tracks(self, playlist_url: str) -> List[Dict]:
        """
        Obtem todas as musicas de uma playlist do Spotify
        Suporta tanto o campo 'track' como 'item' (formatos diferentes da API)
        """
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            self.log(f"A obter musicas da playlist ID: {playlist_id}")
            
            tracks = []
            offset = 0
            limit = 100
            
            while True:
                try:
                    response = self.spotify_client.playlist_tracks(
                        playlist_id,
                        offset=offset,
                        limit=limit
                    )
                    
                    if not response.get("items"):
                        break
                    
                    for item in response["items"]:
                        # Verifica tanto 'track' como 'item' (formatos diferentes)
                        track = item.get("track")
                        if track is None:
                            track = item.get("item")
                        
                        if track is None:
                            continue
                        
                        # Ignora episodios de podcast
                        if track.get("type") == "episode":
                            continue
                        
                        # Verifica se tem os campos necessarios
                        if not track.get("name") or not track.get("artists"):
                            continue
                        
                        track_data = {
                            "name": track.get("name", "Desconhecido"),
                            "artists": [artist.get("name", "Desconhecido") for artist in track.get("artists", [])],
                            "id": track.get("id", ""),
                            "search_query": f"{track.get('name', '')} {' '.join([artist.get('name', '') for artist in track.get('artists', [])])}"
                        }
                        
                        # Evita duplicados
                        if track_data not in tracks:
                            tracks.append(track_data)
                            self.log(f"Musica encontrada: {track_data['name']} - {', '.join(track_data['artists'])}")
                    
                    if response.get("next"):
                        offset += limit
                    else:
                        break
                        
                except Exception as e:
                    self.log(f"Erro ao obter pagina: {e}", "ERROR")
                    break
            
            self.log(f"Total: {len(tracks)} musicas encontradas")
            return tracks
            
        except Exception as e:
            self.log(f"Erro ao obter playlist: {e}", "ERROR")
            import traceback
            self.log(traceback.format_exc(), "DEBUG")
            return []
    
    def get_playlist_name(self, playlist_url: str) -> str:
        """Obtem o nome da playlist"""
        try:
            playlist_id = playlist_url.split("/")[-1].split("?")[0]
            playlist = self.spotify_client.playlist(playlist_id, fields="name")
            name = playlist.get("name", f"playlist_{playlist_id[:8]}")
            name = re.sub(r'[<>:"/\\|?*]', '_', name)
            return name.strip()
        except Exception as e:
            self.log(f"Erro ao obter nome da playlist: {e}", "ERROR")
            return "playlist_desconhecida"
    
    def get_existing_songs(self, folder_path: Path) -> Set[str]:
        """Procura ficheiros MP3 existentes na pasta"""
        existing_songs = set()
        
        if not folder_path.exists():
            self.log(f"A criar pasta: {folder_path}")
            folder_path.mkdir(parents=True, exist_ok=True)
            return existing_songs
        
        for file in folder_path.glob("*.mp3"):
            song_name = file.stem
            song_name = re.sub(r'\s*[-–]\s*YouTube.*$', '', song_name)
            song_name = re.sub(r'\s*\[.*?\]$', '', song_name)
            existing_songs.add(song_name.lower().strip())
        
        self.log(f"Encontrados {len(existing_songs)} MP3 na pasta")
        return existing_songs
    
    def normalize_song_name(self, track: Dict) -> str:
        """Normaliza o nome da musica para comparacao"""
        artist_str = ", ".join(track.get("artists", []))
        return f"{artist_str} - {track.get('name', 'Desconhecido')}".lower().strip()
    
    def find_missing_songs(self, tracks: List[Dict], existing_songs: Set[str]) -> List[Dict]:
        """Encontra musicas que faltam na pen"""
        missing = []
        
        if not tracks:
            return missing
            
        for track in tracks:
            normalized = self.normalize_song_name(track)
            
            exists = False
            for existing in existing_songs:
                if normalized in existing or existing in normalized:
                    exists = True
                    break
                
                # Tenta comparar sem " - " no meio
                track_parts = normalized.split(" - ")
                if len(track_parts) == 2:
                    if track_parts[0] in existing or track_parts[1] in existing:
                        exists = True
                        break
            
            if not exists:
                missing.append(track)
                self.log(f"Musica em falta: {track['name']} - {', '.join(track['artists'])}")
        
        return missing
    
    def download_from_youtube(self, track: Dict, output_path: Path) -> bool:
        """Baixa a musica do YouTube e converte para MP3"""
        search_query = track.get('search_query', '')
        if not search_query:
            self.log("Consulta de pesquisa vazia", "WARNING")
            return False
        
        artist_name = ", ".join(track.get("artists", ["Desconhecido"]))
        safe_name = f"{artist_name} - {track.get('name', 'Desconhecido')}"
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', safe_name)
        
        output_file = output_path / f"{safe_name}.mp3"
        
        if output_file.exists():
            self.log(f"Ficheiro ja existe: {output_file.name}")
            return True
        
        ydl_opts = self.config["YT_DOWNLOAD_OPTIONS"].copy()
        ydl_opts["outtmpl"] = str(output_path / f"{safe_name}.%(ext)s")
        
        for attempt in range(self.config["MAX_RETRIES"]):
            try:
                self.log(f"A baixar: {search_query} (tentativa {attempt+1}/{self.config['MAX_RETRIES']})")
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"ytsearch10:{search_query}", download=False)
                    
                    if not info or not info.get('entries'):
                        self.log("Nenhum resultado encontrado", "WARNING")
                        return False
                    
                    best_video = None
                    for entry in info['entries']:
                        if entry and entry.get('title'):
                            best_video = entry
                            break
                    
                    if not best_video:
                        self.log("Nenhum video valido encontrado", "WARNING")
                        return False
                    
                    video_url = f"https://youtube.com/watch?v={best_video['id']}"
                    self.log(f"Video encontrado: {best_video['title'][:50]}...")
                    
                    ydl.download([video_url])
                
                self.log(f"Download concluido: {safe_name}")
                time.sleep(self.config["SLEEP_BETWEEN_DOWNLOADS"])
                return True
                
            except Exception as e:
                self.log(f"Erro ao baixar {track['name']}: {e}", "ERROR")
                if attempt < self.config["MAX_RETRIES"] - 1:
                    wait = self.config["SLEEP_BETWEEN_DOWNLOADS"] * (attempt + 1)
                    self.log(f"A aguardar {wait}s antes de tentar novamente...")
                    time.sleep(wait)
        
        return False
    
    def sync_playlist(self, playlist_url: str) -> bool:
        """Sincroniza uma playlist completa"""
        self.log(f"\n{'='*60}")
        self.log(f"A sincronizar playlist: {playlist_url}")
        
        playlist_name = self.get_playlist_name(playlist_url)
        playlist_folder = Path(self.config["PEN_DRIVE_PATH"]) / playlist_name
        
        self.log(f"Pasta: {playlist_folder}")
        
        tracks = self.get_playlist_tracks(playlist_url)
        if not tracks:
            self.log("Nenhuma musica encontrada na playlist", "WARNING")
            return False
        
        existing_songs = self.get_existing_songs(playlist_folder)
        missing_tracks = self.find_missing_songs(tracks, existing_songs)
        
        if not missing_tracks:
            self.log("Todas as musicas ja estao sincronizadas!")
            return True
        
        self.log(f"A baixar {len(missing_tracks)} musicas em falta...")
        
        success_count = 0
        for i, track in enumerate(missing_tracks, 1):
            self.log(f"\n[{i}/{len(missing_tracks)}] A processar: {track['name']}")
            
            if self.download_from_youtube(track, playlist_folder):
                success_count += 1
            
            if i < len(missing_tracks):
                time.sleep(self.config["SLEEP_BETWEEN_DOWNLOADS"])
        
        self.log(f"Resumo: {success_count}/{len(missing_tracks)} musicas baixadas com sucesso")
        return success_count == len(missing_tracks)
    
    def run(self):
        """Executa a sincronizacao"""
        self.log("A iniciar Spotify Pen Sync")
        self.log(f"Pen drive: {self.config['PEN_DRIVE_PATH']}")
        self.log(f"Playlists: {len(self.config['PLAYLISTS'])}")
        
        pen_path = Path(self.config["PEN_DRIVE_PATH"])
        if not pen_path.exists():
            self.log(f"Pen drive nao encontrada em: {pen_path}", "ERROR")
            self.log("Verifique o caminho e se a pen esta ligada")
            return
        
        if not self.check_dependencies():
            self.log("Dependencias nao instaladas corretamente", "ERROR")
            return
        
        total_playlists = len(self.config["PLAYLISTS"])
        for i, playlist_url in enumerate(self.config["PLAYLISTS"], 1):
            self.log(f"\nPlaylist {i}/{total_playlists}")
            self.sync_playlist(playlist_url)
        
        self.log("\nSincronizacao concluida!")
        self.log(f"Registo guardado em: {self.log_file}")
    
    def check_dependencies(self) -> bool:
        """Verifica se as dependencias estao instaladas"""
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            self.log("FFmpeg encontrado")
        except:
            self.log("FFmpeg nao encontrado. Instale: https://ffmpeg.org/", "ERROR")
            return False
        
        try:
            subprocess.run(["yt-dlp", "--version"], capture_output=True, check=True)
            self.log("yt-dlp encontrado")
        except:
            self.log("yt-dlp nao encontrado. Instale: pip install yt-dlp", "ERROR")
            return False
        
        try:
            import spotipy
            self.log("spotipy encontrado")
        except:
            self.log("spotipy nao encontrado. Instale: pip install spotipy", "ERROR")
            return False
        
        return True

# ============================================
# FUNCAO PRINCIPAL
# ============================================

def main():
    """Funcao principal"""
    
    if CONFIG["SPOTIFY_CLIENT_ID"] == "SEU_CLIENT_ID_AQUI":
        print("Configure as suas credenciais do Spotify no CONFIG!")
        print("  1. Acesse: https://developer.spotify.com/dashboard")
        print("  2. Crie uma aplicacao e obtenha CLIENT_ID e CLIENT_SECRET")
        print("  3. Configure em CONFIG no inicio do script")
        sys.exit(1)
    
    if CONFIG["PEN_DRIVE_PATH"] == "D:/" and not Path("D:/").exists():
        print("Configure o caminho da pen drive!")
        print("  Windows: D:/, E:/, etc")
        print("  Linux: /media/usb, /mnt/pen, etc")
        sys.exit(1)
    
    sync = SpotifyPenSync(CONFIG)
    sync.run()

if __name__ == "__main__":
    main()
