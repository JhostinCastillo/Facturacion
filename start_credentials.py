from pydrive2.auth import GoogleAuth
import os

def actualizar_credenciales():
    os.remove(r".streamlit\configuser.json")

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()


actualizar_credenciales()