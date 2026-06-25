# Spotify Pen Sync

Sincroniza playlists do Spotify com uma pen USB.

---

## Requisitos

* Python 3.8 ou superior
* Pen USB ligada ao computador
* Conta Spotify (gratuita ou premium)

---

## Instalação

### 1. Instalar Python

Download em: [https://www.python.org/downloads/](https://www.python.org/downloads/)

### 2. Instalar dependências

Abrir o terminal (Linha de Comandos) e executar:

```
pip install spotipy yt-dlp
```

### 3. Instalar FFmpeg

**Windows:**

1. Descarregar de: [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
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

## Configuração

### 1. Obter credenciais do Spotify

1. Aceder a: [https://developer.spotify.com/dashboard](https://developer.spotify.com/dashboard)
2. Iniciar sessão com a conta Spotify
3. Clicar em "Create App"
4. Dar um nome à aplicação
5. Em "Redirect URI" adicionar: `http://127.0.0.1:8888/callback`
6. Clicar em "Save"
7. Copiar o `Client ID` e o `Client Secret`

---

### 2. Configurar o script

Abrir o ficheiro `spotify_pen_sync.py` e alterar:

```python
CONFIG = {
    "SPOTIFY_CLIENT_ID": "COLOCAR_AQUI_O_CLIENT_ID",
    "SPOTIFY_CLIENT_SECRET": "COLOCAR_AQUI_O_CLIENT_SECRET",
    "PEN_DRIVE_PATH": "D:/",  # Alterar para o caminho da pen
    "PLAYLISTS": [
        "https://open.spotify.com/playlist/ID_DA_PLAYLIST",
    ],
}
```

---

### 3. Caminho da pen USB

**Windows:** `D:/`, `E:/`, etc.
**Linux:** `/media/usb`, `/mnt/pen`, etc.
**macOS:** `/Volumes/NOME_DA_PEN`

---

## Execução

No terminal, dentro da pasta do script:

```
python spotify_pen_sync.py
```

O script irá:

1. Ligar-se ao Spotify
2. Ler as playlists
3. Comparar com os ficheiros na pen
4. Descarregar as músicas em falta
5. Atualizar músicas antigas (se configurado)

---

## Configurações avançadas

No ficheiro `spotify_pen_sync.py`:

```python
# Substituir ficheiros existentes (True = sim, False = não)
"OVERWRITE_EXISTING": False,

# Remover músicas que já não estão na playlist
"REMOVE_EXTRA_SONGS": False,
```

---

## Estrutura de pastas

O script cria uma pasta para cada playlist com o respetivo nome:

```
D:/
├── Top 50 Global/
│   ├── Artista - Música 1.mp3
│   ├── Artista - Música 2.mp3
│   └── ...
├── Playlist Pessoal/
│   ├── Artista - Música 1.mp3
│   └── ...
```

---

## Resolver problemas

**Erro: "FFmpeg não encontrado"**

* Instalar o FFmpeg (ver secção de instalação)

**Erro: "Pen drive não encontrada"**

* Confirmar se a pen está ligada
* Verificar o caminho definido no script

**Erro: "Erro ao ligar ao Spotify"**

* Confirmar o Client ID e Client Secret
* Verificar se o Redirect URI está correto

---

## Ficheiros

* `spotify_pen_sync.py` - Script principal
* `sync_log.txt` - Registo de atividade
* `.spotify_cache` - Token de autenticação (criado automaticamente)

---

## Notas

* O script não guarda as músicas localmente, apenas as transfere para a pen
* As músicas são descarregadas via YouTube e convertidas para MP3
* Qualidade de áudio: 192 kbps

---

## Suporte

Em caso de problemas, consultar o ficheiro `sync_log.txt`.
