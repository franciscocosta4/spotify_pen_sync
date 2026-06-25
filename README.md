<div align="center">
    
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![FFmpeg](https://shields.io/badge/FFmpeg-%23171717.svg?logo=ffmpeg&style=for-the-badge&labelColor=171717&logoColor=5cb85c)

# Spotify Pen Sync

Sincroniza playlists do Spotify com uma pen USB.

</div>
    
---
## Dependências

Abrir o terminal e executar:

```
pip install spotipy yt-dlp
```

### FFmpeg

**Windows:**
1. Descarregar de: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
2. Extrair o ficheiro
3. Adicionar a pasta `bin` ao PATH

**Linux:**
```
sudo apt-get install ffmpeg
```

**macOS:**
```
brew install ffmpeg
```

---

## Configuração

### Credenciais Spotify

1. Aceder a: [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Login na conta Spotify
3. Criar uma aplicação
4. Definir nome da app
5. Adicionar Redirect URI: `http://127.0.0.1:8888/callback`
6. Guardar
7. Copiar Client ID e Client Secret


### Script

Editar `spotify_pen_sync.py`:

```python
CONFIG = {
    "SPOTIFY_CLIENT_ID": "COLOCAR_AQUI_O_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET": "COLOCAR_AQUI_O_CLIENT_SECRET",
    "PEN_DRIVE_PATH": "D:/",
    "PLAYLISTS": [
        "https://open.spotify.com/playlist/ID_DA_PLAYLIST",
    ],
}
```

### Pen USB

Windows: `D:/`, `E:/`
Linux: `/media/usb`, `/mnt/pen`
macOS: `/Volumes/NOME_DA_PEN`

---

## Execução

No terminal, na pasta do script:

```
python spotify_pen_sync.py
```

O processo:

1. Liga ao Spotify
2. Lê playlists
3. Compara ficheiros na pen
4. Descarrega músicas em falta
5. Atualiza ficheiros (se ativado)

---

## Opções

```python
"OVERWRITE_EXISTING": False,
"REMOVE_EXTRA_SONGS": False,
```

---

## Estrutura

```
D:/
├── Top 50 Global/
│   ├── Artista - Música.mp3
├── Playlist Pessoal/
│   ├── Artista - Música.mp3
```

## Notas

* Não guarda músicas localmente
* Download via YouTube convertido para MP3
* Qualidade: 192 kbps
