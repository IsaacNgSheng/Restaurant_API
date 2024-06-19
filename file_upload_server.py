#!/usr/bin/env python3
from cmath import sin
from math import radians, cos, sqrt, atan2
import requests
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


def obtenir_coordonnees(adresse):
    # URL de l'API OpenStreetMap
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={adresse}"
    # Envoyer une requête GET à l'API
    reponse = requests.get(url)
    # Vérifier si la requête a réussi
    # Check if the request was successful
    if reponse.status_code == 200:
        # Analyser la réponse JSON
        data = reponse.json()
        if data:
            # Extraire les coordonnées de la première occurrence
            # Extract coordinates from first occurrence
            latitude = float(data[0]['lat'])
            longitude = float(data[0]['lon'])
            return latitude, longitude
        else:
            print("Aucune donnée trouvée pour cette adresse.")
            return None
    else:
        print("Erreur lors de la requête à l'API.")
        return None

#find_producer_near
def trouver_producteur_proche(denree, latitude, longitude, api_key):
    # URL de l'API AgenceBIO
    url = f"https://api.agencebio.org/v1/lieux-de-vente/{denree}/producteurs"

    # Paramètres de requête
    params = {
        "lat": latitude,
        "lon": longitude,
        "limit": 1,  # Limite de résultats à 1, pour obtenir le plus proche
        "api_key": api_key
    }

    # Envoyer une requête GET à l'API
    reponse = requests.get(url, params=params)

    # Vérifier si la requête a réussi
    # Check if the request was successful
    if reponse.status_code == 200:
        # Analyser la réponse JSON
        data = reponse.json()
        if data and 'producteurs' in data:
            # Extraire les informations du producteur le plus proche
            # Extract information from the nearest producer
            producteur_proche = data['producteurs'][0]
            nom = producteur_proche['nom']
            distance = producteur_proche['distance']
            return nom, distance
        else:
            print("Aucun producteur trouvé pour cette denrée.")
            return None, None
    else:
        print("Erreur lors de la requête à l'API AgenceBIO.")
        return None, None

#find_distance_between_points
def trouver_distance_entre_points(latitude_depart, longitude_depart, latitude_arrivee, longitude_arrivee):
    # URL de l'API IGN itinéraire
    url = "https://wxs.ign.fr/an7nvfzojv5wa96dsga5nk8z/itineraire/rest/route.json"

    # Paramètres de requête
    params = {
        "start": f"{longitude_depart},{latitude_depart}",
        "end": f"{longitude_arrivee},{latitude_arrivee}",
        "method": "time",  # Méthode de calcul basée sur la durée de trajet/Calculation based on travel time
        "graphName": "Voiture",  # Type de trajet en voiture/Car trip type
        "gp-access-lib": "0.11.5",
        "gp-version": "3.0",
        "apikey": "CLE_API_IGN"  # Remplacez par votre clé API IGN itinéraire/Replace with your IGN API route key
    }

    # Envoyer une requête GET à l'API IGN itinéraire
    reponse = requests.get(url, params=params)

    # Vérifier si la requête a réussi
    if reponse.status_code == 200:
        # Analyser la réponse JSON
        data = reponse.json()
        if 'routes' in data and len(data['routes']) > 0:
            # Extraire la distance la plus courte
            distance = data['routes'][0]['summary']['totalDistance']
            return distance
        else:
            print("Aucun itinéraire trouvé entre ces deux points.")
            return None
    else:
        print("Erreur lors de la requête à l'API IGN itinéraire.")
        return None
    
# get_company_data_by_siret
def obtenir_donnees_entreprise_par_siret(siret, api_token):
    # URL de l'API Recherche d'entreprise
    url = f"https://entreprise.api.gouv.fr/v2/entreprises/{siret}"

    # Paramètres de requête avec le token d'authentification
    headers = {
        "Authorization": f"Bearer {api_token}"
    }

    # Envoyer une requête GET à l'API Recherche d'entreprise
    reponse = requests.get(url, headers=headers)

    # Vérifier si la requête a réussi
    if reponse.status_code == 200:
        # Analyser la réponse JSON
        data = reponse.json()
        return data
    else:
        print("Erreur lors de la requête à l'API Recherche d'entreprise.")
        return None


def get_producer_for_ingredient(ingredient):
    producers = {" Pain frais ":{" Entreprise ":" MONTOIR MATHIEU "," Manager ":" Mathieu Montoir "," Distance " :20.6}," Pommes de terre ":{" Entreprise ":" ESPACE EMPLOI - JARDINS DUBREIL "," Manager ":" Unknown "," Distance " :4.57}}
    return producers.get(ingredient, None)

def distance(address1, address2):
    pass

@app.route('/get_producers', methods=['GET'])
def get_producers():
    global ingredients, Adresse
    if not ingredients or not Adresse:
        param_manquants = []
        if not ingredients:
            param_manquants.append("ingredients")
        if not Adresse:
            param_manquants.append("Adresse")
        return Response(param_manquants), 400
    else:
        producers = {}
        for ingredient, conservateur in ingredients.items():
            producer = get_producer_for_ingredient(ingredient)
            if producer:
                distance = distance(producer['address'], Adresse)
                producers[ingredient] = {
                    'Entreprise': producer['Entreprise'],
                    'Manager': producer['Manager'],
                    'Distance': distance
                }
    return Response(producers, 200)



@app.route('/load_xml', methods=['POST'])
def load_xml(filepath):
    global ingredients, adresse
    json_file = parser_xml.xml_to_json(filepath)
    dict_file = json.load(json_file)
    ingredients_dict_file = dict_file["ingredients"]
    adresse_dict_file = dict_file["adresses"]
    ingredients = ingredients_dict_file
    adresse = adresse_dict_file
    if dict_file:
        return Response(response="OK",
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response='Mauvaise requête (pas de fichier, fichier mal formé, etc.)',
                        status=400,
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
