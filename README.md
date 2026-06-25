# Spotify Pen Sync

Sincroniza playlists do Spotify com uma pen USB.

---

## Requisitos

- Python 3.8 ou superior
- Pen USB ligada ao computador
- Conta Spotify (gratuita ou premium)

---

## Instalacao

### 1. Instalar Python

Download em: https://www.python.org/downloads/

### 2. Instalar dependencias

Abrir o terminal (Prompt de Comando) e executar:

```
pip install spotipy yt-dlp
```

### 3. Instalar FFmpeg

**Windows:**
1. Baixar de: https://ffmpeg.org/download.html
2. Extrair o ficheiro
3. Adicionar a pasta `bin` ao PATH do sistema

**Linux:**
```
sudo apt-get install ffmpeg
```

**macOS:**
```
brew install ffmpeg
```

---

## Configuracao

### 1. Obter credenciais do Spotify

1. Aceder a: https://developer.spotify.com/dashboard
2. Fazer login com a conta Spotify
3. Clicar em "Create App"
4. Dar um nome a aplicacao
5. Em "Redirect URI" adicionar: `http://127.0.0.1:8888/callback`
6. Clicar em "Save"
7. Copiar o `Client ID` e `Client Secret`

### 2. Configurar o script

Abrir o ficheiro `spotify_pen_sync.py` e alterar:

```python
CONFIG = {
    "SPOTIFY_CLIENT_ID": "COLAR_AQUI_O_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET": "COLAR_AQUI_O_CLIENT_SECRET",
    "PEN_DRIVE_PATH": "D:/",  # Alterar para o caminho da pen
    "PLAYLISTS": [
        "https://open.spotify.com/playlist/ID_DA_PLAYLIST",
    ],
}
```

### 3. Caminho da pen USB

**Windows:** `D:/`, `E:/`, etc.
**Linux:** `/media/usb`, `/mnt/pen`, etc.
**macOS:** `/Volumes/NOME_DA_PEN`

---

## Execucao

No terminal, na pasta do script:

```
python spotify_pen_sync.py
```

O script vai:
1. Ligar-se ao Spotify
2. Ler as playlists
3. Comparar com os ficheiros na pen
4. Baixar as musicas em falta
5. Atualizar musicas antigas (se configurado)

---

## Configuracoes avancadas

No ficheiro `spotify_pen_sync.py`:

```python
# Substituir ficheiros existentes (True = sim, False = nao)
"OVERWRITE_EXISTING": False,

# Remover musicas que nao estao mais na playlist
"REMOVE_EXTRA_SONGS": False,
```

---

## Estrutura de pastas

O script cria uma pasta para cada playlist com o nome da mesma:

```
D:/
├── Top 50 Global/
│   ├── Artista - Musica 1.mp3
│   ├── Artista - Musica 2.mp3
│   └── ...
├── Playlist Pessoal/
│   ├── Artista - Musica 1.mp3
│   └── ...
```

---

## Resolver problemas

**Erro: "FFmpeg nao encontrado"**
- Instalar o FFmpeg (ver secao de instalacao)

**Erro: "Pen drive nao encontrada"**
- Verificar se a pen esta ligada
- Confirmar o caminho no script

**Erro: "Erro ao ligar ao Spotify"**
- Verificar o Client ID e Client Secret
- Confirmar que a Redirect URI esta correta

---

## Ficheiros

- `spotify_pen_sync.py` - Script principal
- `sync_log.txt` - Registo de atividades
- `.spotify_cache` - Token de autenticacao (criado automaticamente)

---

## Notas

- O script nao guarda as musicas, apenas as descarrega para a pen
- As musicas sao descarregadas do YouTube e convertidas para MP3
- Qualidade do audio: 192 kbps

---

## Suporte

Para duvidas ou problemas, consultar os logs no ficheiro `sync_log.txt`.
