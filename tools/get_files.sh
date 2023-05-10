#!/bin/bash
# Script permettant de télécharger tous les fichiers présent sur la board.
# Testé avec ESP8266

# TODO ajouter en paramètre optionel : dossier de destination et port

set -e

# Définir le port série de l'ESP8266
PORT=/dev/ttyUSB0

# Se connecter à l'ESP8266 avec ampy
#ampy --port $PORT ls

# Créer un dossier pour stocker les fichiers téléchargés
CURRENT_TIME=$(date +"%Y%m%d_%H%M%S")
DEST_FOLDER="esp8266_files_$CURRENT_TIME"
mkdir -p "$DEST_FOLDER"

# Fonction récursive pour explorer les dossiers
function explore_folder {
  for file in $(ampy --port $PORT ls $1); do
    if [[ $file == *.* ]]; then
      # Le fichier est un fichier
      echo "Téléchargement du fichier : ${file}"
      ampy --port $PORT get ${file} > $DEST_FOLDER${file}
    else
      # Le fichier est un dossier
      mkdir -p $DEST_FOLDER${file}
      explore_folder $1${file}
    fi
  done
}

# Explorer le dossier racine de l'ESP8266
explore_folder ""
echo "Tous les fichiers ont été téléchargés avec succès dans le dossier $DEST_FOLDER !"

