#!/usr/bin/env python3

from flask import Flask
from flask import request
from flask import Response
from werkzeug.utils import secure_filename
import json
import os
import parser_xml


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
    return Response(response=json.dumps(response), 
                    status=200, 
                    mimetype='application/json')


app = Flask(__name__)
ingredients = {}
adresse = {}

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    resp = Response(response=json.dumps(ingredients),
                  status=200,
                  mimetype='application/json')
    return resp

@app.route('/ingredients', methods=['POST'])
def post_ingredients():
    global ingredients
    new_ingredients = request.json
    ingredients = new_ingredients
    resp = Response(response=json.dumps(ingredients),
                        status=200,
                        mimetype='application/json')
    return resp

@app.route('/ingredients', methods=['DELETE'])
def delete_ingredients():
    global ingredients
    ingredients = {}
    return Response(response=f'Ingredients supprimés avec succés', 
                    status=200, 
                    mimetype='application/json')
    
@app.route('/ingredients/<ing>/<cnsrv>', methods=['POST'])
def add_ingredients(ing,cnsrv):
    global ingredients
    if ing in ingredients.keys:
         return Response(response=f"l'ingrédient à ajouter est déjà présent, aucun changement dans les ingrédients",
                          status=304,
                          mimetype='application/json')
    else:
        ingredients['ing']=cnsrv
        return Response(response=json.dumps(ingredients),
                        status=200,
                        mimetype='application/json')
        

@app.route('/ingredients/<ing>', methods=['DELETE'])
def delete_ingredients(ing,cnsrv):
    global ingredients
    ingredients = {}
    if ing in ingredients.keys:
        ingredients.pop(ing)
        return Response(resposne=json.dumps(ingredients),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=f"l'ingrédient à supprimer n'est pas présent, aucun changement dans les ingrédients",
                        status=304,
                        mimetype='application/json')



@app.route('/location', methods=['GET'])  
def manage_location():
    return Response(response=json.dumps(adresse),
                    status=200,
                    mimetype='application/json')
    

@app.route('/location', methods=['POST'])  
def modify_location(json_file):
    global adresse
    adresse=json.load(json_file)
    return Response(response=json.dumps(adresse),
                    status=200,
                    mimetype='application/json')


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
