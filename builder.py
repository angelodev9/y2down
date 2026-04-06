import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YT Advanced Downloader", page_icon="📥")

st.title("📥 Downloader de Playlist Pro")

# --- Interface de sélection ---
url = st.text_input("Collez l'URL de la playlist YouTube ici :")

col1, col2 = st.columns(2)

with col1:
    format_type = st.radio("Format de sortie :", ["Vidéo (MP4)", "Audio (MP3)"])

with col2:
    if format_type == "Vidéo (MP4)":
        qualite = st.selectbox("Qualité max :", ["1080p", "720p", "480p", "Meilleure disponible"])
    else:
        qualite = st.selectbox("Qualité Audio :", ["320kbps", "192kbps", "128kbps"])

# --- Logique de téléchargement ---
if st.button("Démarrer le téléchargement"):
    if url:
        with st.status("Téléchargement en cours...", expanded=True) as status:
            try:
                # 1. Configurer le format selon le choix
                ydl_opts = {
                    'noplaylist': False,
                    'quiet': True,
                }

                if format_type == "Audio (MP3)":
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': qualite.replace('kbps', ''),
                        }],
                    })
                else:
                    # Gestion de la qualité vidéo
                    if qualite == "1080p":
                        f = "bestvideo[height<=1080]+bestaudio/best"
                    elif qualite == "720p":
                        f = "bestvideo[height<=720]+bestaudio/best"
                    elif qualite == "480p":
                        f = "bestvideo[height<=480]+bestaudio/best"
                    else:
                        f = "bestvideo+bestaudio/best"
                    
                    ydl_opts.update({'format': f, 'merge_output_format': 'mp4'})

                # 2. Récupérer le nom de la playlist pour le dossier
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    nom_playlist = info.get('title', 'Playlist_Telechargee')
                
                nom_dossier = "".join([c for c in nom_playlist if c.isalnum() or c in (' ', '-', '_')]).strip()
                ydl_opts['outtmpl'] = f'{nom_dossier}/%(title)s.%(ext)s'

                # 3. Exécution
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                status.update(label="✅ Téléchargement terminé !", state="complete", expanded=False)
                st.success(f"Fichiers enregistrés dans le dossier : `{nom_dossier}`")
            
            except Exception as e:
                st.error(f"Erreur : {e}")
    else:
        st.warning("Veuillez entrer une URL.")

