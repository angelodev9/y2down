import streamlit as st
import yt_dlp
import os

# =========================
# CONFIGURATION PAGE
# =========================
st.set_page_config(page_title="Téléchargeur YouTube", page_icon="📥")

st.title("📥 Téléchargeur de Vidéo et Playlist YouTube")
st.write("Télécharge facilement une vidéo ou une playlist.")

# =========================
# INTERFACE UTILISATEUR
# =========================
url = st.text_input("Lien YouTube :")

col1, col2 = st.columns(2)

with col1:
    type_format = st.radio("Type de fichier :", ["Vidéo (MP4)", "Audio (MP3)"])

with col2:
    if type_format == "Vidéo (MP4)":
        qualite = st.selectbox("Qualité vidéo :", ["1080p", "720p", "480p", "Meilleure"])
    else:
        qualite = st.selectbox("Qualité audio :", ["320kbps", "192kbps", "128kbps"])

# =========================
# BARRE DE PROGRESSION
# =========================
progress_bar = st.progress(0)
progress_text = st.empty()


def hook_progress(d):
    """
    Fonction appelée pendant le téléchargement.
    Permet de mettre à jour la barre de progression.
    """
    if d['status'] == 'downloading':
        if 'total_bytes' in d and d['total_bytes'] is not None:
            total = d['total_bytes']
            downloaded = d.get('downloaded_bytes', 0)
            percent = int(downloaded / total * 100)

            progress_bar.progress(percent)
            progress_text.text(f"Téléchargement : {percent}%")

    elif d['status'] == 'finished':
        progress_bar.progress(100)
        progress_text.text("Finalisation...")


# =========================
# FONCTION CONFIG FORMAT
# =========================
def get_format_options(type_format, qualite):
    """
    Retourne les options yt_dlp selon le choix utilisateur
    """
    options = {
        'quiet': True,
        'progress_hooks': [hook_progress]
    }

    # ---- AUDIO ----
    if type_format == "Audio (MP3)":
        options.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': qualite.replace('kbps', ''),
            }],
        })

    # ---- VIDEO ----
    else:
        if qualite == "1080p":
            f = "bestvideo[height<=1080]+bestaudio/best"
        elif qualite == "720p":
            f = "bestvideo[height<=720]+bestaudio/best"
        elif qualite == "480p":
            f = "bestvideo[height<=480]+bestaudio/best"
        else:
            f = "bestvideo+bestaudio/best"

        options.update({
            'format': f,
            'merge_output_format': 'mp4'
        })

    return options


# =========================
# DETECTER SI PLAYLIST
# =========================
def est_playlist(info):
    """
    Vérifie si l'URL est une playlist
    """
    return 'entries' in info


# =========================
# NETTOYER NOM DOSSIER
# =========================
def nettoyer_nom(nom):
    """
    Nettoie le nom pour éviter les erreurs système
    """
    return "".join([c for c in nom if c.isalnum() or c in (' ', '-', '_')]).strip()


# =========================
# BOUTON TELECHARGEMENT
# =========================
if st.button("Télécharger"):
    if not url:
        st.warning("Ajoute un lien.")
    else:
        try:
            with st.status("Analyse du lien...", expanded=True):

                # 1. Récupérer les infos sans télécharger
                with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                    info = ydl.extract_info(url, download=False)

                is_playlist = est_playlist(info)

                # 2. Configurer options
                ydl_opts = get_format_options(type_format, qualite)

                # =========================
                # CAS PLAYLIST
                # =========================
                if is_playlist:
                    nom_playlist = nettoyer_nom(info.get('title', 'Playlist'))

                    # Créer un dossier
                    ydl_opts['outtmpl'] = f"{nom_playlist}/%(title)s.%(ext)s"

                    st.info(f"Playlist détectée : {nom_playlist}")

                # =========================
                # CAS VIDEO SEULE
                # =========================
                else:
                    # Pas de dossier → fichier direct
                    ydl_opts['outtmpl'] = "%(title)s.%(ext)s"

                    st.info("Vidéo unique détectée")

                # 3. Télécharger
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

                st.success("Téléchargement terminé !")

        except Exception as e:
            st.error(f"Erreur : {e}")
