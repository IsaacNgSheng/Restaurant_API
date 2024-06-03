#!/usr/bin/env python3
from flask import Flask #pour créer le serveur/to create the server
from flask import request #pour gérer les différentes requêtes/manage different requests
from flask import Response #pour envoyer des réponses (on peut aussi utiliser jsonify avec, mais on a utilisé json)
#to send responses (you can also use jsonify with it, but we used json)
from werkzeug.utils import secure_filename
import json
import os


UPLOAD_FOLDER = r'C:\Users\Isaac\OneDrive\Documents\NUS\Exchange\Notes\CBD\Exercise\Project'
ALLOWED_EXTENSIONS = {'xml'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/project_info', methods=['GET'])
def project_info():
    response = {"groupe" : "GI3.1",
        "depot":"https://gitlab.insa-lyon.fr/cbd-projet-conseil-en-restauration-biologique-et-locale/projet",
        "authentification" : "IP",
        "stockage" : "serialisation",
        "membres" : [
            {"prenom" : "Isaac", "nom" : "NG"},
            {"prenom" : "Imane", "nom" : "KRIKECH"},
            {"prenom" : "Isseu", "nom" : "DIAGNE"}
            ]
    }
    return Response(response, 200)

@app.route('/', methods=['POST'])
def upload():
    resp = Response("Erreur inattendue", status=405)
    if request.method == 'POST':
        print(request.files)
        # voir si la erquête post à une section 'fichiers'
        # see if the post query has a 'files' section
        if 'upload_file' not in request.files:
            resp = Response("Pas de section “fichier” dans la requête", status=405)
        else:
            file = request.files['upload_file']
            if file.filename == '': 
                #on vérifie que le fichier est bien envoyé
                #we check that the file is sent
                resp = Response('Aucun fichier fourni', status = 405)
            elif file and allowed_file(file.filename):
                #on vérifie qu'il n'y a pas de pb de sécurité de base avec le fichier
                #we check that there are no basic security problems with the file
                filename = secure_filename(file.filename)
                #on sauvegarde le fichier
                #we save the file
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                resp = Response(f'Fichier {filename} sauvegardé', status = 200)
    return resp

#will only execute if this file is run
if __name__ == "__main__":
    debugging = True
    app.run(host="0.0.0.0", port=5080, debug=debugging)
