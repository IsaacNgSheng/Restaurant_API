#!/usr/bin/env python3
from flask import Flask #pour créer le serveur
from flask import request #pour gérer les différentes requêtes
from flask import Response #pour envoyer des réponses (on peut aussi utiliser jsonify avec, mais on a utilisé json)
from werkzeug.utils import secure_filename
import json
import os


UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'xml'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/', methods=['POST'])
def upload():
    resp = Response("Erreur inattendue", status=405)
    if request.method == 'POST':
        print(request.files)
        # voir si la erquête post à une section 'fichiers'
        if 'upload_file' not in request.files:
            resp = Response("Pas de section “fichier” dans la requête", status=405)
        else:
            file = request.files['upload_file']
            if file.filename == '': #on vérifie que le fichier est bien envoyé
                resp = Response('Aucun fichier fourni', status = 405)
            elif file and allowed_file(file.filename):
                #on vérifie qu'il n'y a pas de pb de sécurité de base avec le fichier
                filename = secure_filename(file.filename)
                #on sauvegarde le fichier
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resp = Response(f'Fichier {filename} sauvegardé', status = 200)
    return resp

#will only execute if this file is run
if __name__ == "__main__":
    debugging = True
    app.run(host="0.0.0.0", port=8080, debug=debugging)
