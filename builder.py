import streamlit as st
import yt_dlp
import os

st.set_page_config(page_title="YT Advanced Downloader", page_icon="📥")

st.title("📥 Downloader de Playlist Pro")

# --- Interface ---
url = st.text_input("Collez l'URL de la playlist YouTube ici :")
col1, col2 = st.columns(2)

with col1:
    format_type = st.radio("Format de sortie :", ["Vidéo (MP4)", "Audio (MP3)"])

with col2:
    if format_type == "Vidéo (MP4)":
        qualite = st.selectbox("Qualité max :", ["1080p", "720p", "480p", "Meilleure disponible"])
    else:
        qualite = st.selectbox("Qualité Audio :", ["320kbps", "192kbps", "128kbps"])

# --- Fonction de rappel pour la barre de progression ---
def my_hook(d):
    if d['status'] == 'downloading':
        # On nettoie la chaîne pour avoir un float
        pct_str = d.get('_percent_str', '0%').strip().replace('%','')
        try:
            pct = float(pct_str) / 100
            progress_placeholder.progress(pct, text=f"Fichier actuel : {d.get('_percent_str')}")
        except:
            pass

# --- Logique de téléchargement ---
if st.button("Démarrer le téléchargement"):
    if url:
        progress_placeholder = st.empty() # Emplacement pour la barre
        
        with st.status("Traitement en cours...", expanded=True) as status:
            try:
                ydl_opts = {
                    'noplaylist': False,
                    'quiet': True,
                    'progress_hooks': [my_hook], # L'élément clé ici
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
                    f = {
                        "1080p": "bestvideo[height<=1080]+bestaudio/best",
                        "720p": "bestvideo[height<=720]+bestaudio/best",
                        "480p": "bestvideo[height<=480]+bestaudio/best"
                    }.get(qualite, "bestvideo+bestaudio/best")
                    
                    ydl_opts.update({'format': f, 'merge_output_format': 'mp4'})

                # Nom du dossier
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)
                    nom_playlist = info.get('title', 'Playlist_Telechargee')
                
                nom_dossier = "".join([c for c in nom_playlist if c.isalnum() or c in (' ', '-', '_')]).strip()
                ydl_opts['outtmpl'] = f'{nom_dossier}/%(title)s.%(ext)s'

                # Téléchargement effectif
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                status.update(label="✅ Terminé !", state="complete", expanded=False)
                progress_placeholder.empty() # On enlève la barre à la fin
                st.success(f"Fichiers enregistrés dans : `{nom_dossier}`")
            
            except Exception as e:
                st.error(f"Erreur : {e}")
    else:
        st.warning("Veuillez entrer une URL.")
