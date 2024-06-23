#!/usr/bin/env python3
from cmath import sin
from math import radians, cos, sqrt, atan2
import requests
from flask import Flask, request, Response, jsonify
from werkzeug.utils import secure_filename
import json
import os
import string
import random

from projet import parser_xml

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', r'C:\Users\Isaac\OneDrive\Documents\NUS\Exchange\Notes\CBD\Exercise\Project')
ALLOWED_EXTENSIONS = {'xml'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ingredients = {}
adresse = {}
location = {}
users = {}

@app.route("/project_info", methods=["GET"])
def project_info():
    response = {
        "groupe": "GI3.1",
        "depot": "https://gitlab.insa-lyon.fr/cbd-projet-conseil-en-restauration-biologique-et-locale/projet",
        "authentification": "IP",
        "stockage": "serialisation",
        "membres": [
            {"prenom": "Isaac", "nom": "NG"},
            {"prenom": "Imane", "nom": "KRIKECH"},
            {"prenom": "Isseu", "nom": "DIAGNE"}
        ]
    }
    return Response(response=json.dumps(response), status=200, mimetype='application/json')

@app.route('/ingredients', methods=['GET'])
def get_ingredients():
    return jsonify(ingredients), 200

@app.route('/ingredients', methods=['POST'])
def post_ingredients():
    global ingredients
    ingredients = request.json
    return jsonify(ingredients), 200

@app.route('/ingredients', methods=['DELETE'])
def delete_ingredients():
    global ingredients
    ingredients = {}
    return "Liste des ingrédients effacée", 200

@app.route('/ingredients/<ing>/<cnsrv>', methods=['POST'])
def add_ingredient(ing, cnsrv):
    global ingredients
    ingredients[ing] = int(cnsrv)
    return jsonify(ingredients), 200

@app.route('/ingredients/<ing>', methods=['DELETE'])
def delete_ingredient(ing):
    global ingredients
    if ing in ingredients:
        del ingredients[ing]
        return jsonify(ingredients), 200
    return jsonify(ingredients), 304

@app.route('/location', methods=['GET'])
def get_location():
    # Example data to be consistent with the expected output
    location = {
        "street": "",
        "city": ""
    }
    return jsonify(location), 200

@app.route('/location', methods=['POST'])
def post_location():
    global location
    location = request.json

    # Verify that the received data has the expected keys
    if not all(key in location for key in ("street", "city")):
        return jsonify({"error": "Invalid input format"}), 400

    return jsonify(location), 200

def obtenir_coordonnees(address):
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": address,
        "format": "json",
        "addressdetails": 1,
        "limit": 1
    }
    headers = {
        'User-Agent': 'My User Agent 1.0',
        'From': 'youremail@domain.example'
    }
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
    return None, None

def trouver_producteur_proche(ingredient, lat, lon):
    url = "https://opendata.agencebio.org/api/gouv/operateurs"
    params = {
        "produit": ingredient,
        "activite": "Production",
        "lat": lat,
        "lng": lon,
        "nb_max": 1
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and data["items"]:
            nearest_producer = data["items"][0]
            adresse = nearest_producer["adressesOperateurs"][0]
            return {
                "Entreprise": nearest_producer["raisonSociale"],
                "Manager": nearest_producer.get("gerant", "Unknown"),
                "Distance": trouver_distance_entre_points(lat, lon, adresse["lat"], adresse["long"])
            }
    return None

def trouver_distance_entre_points(lat1, lon1, lat2, lon2):
    url = "https://wxs.ign.fr/calcul/geoportail/itineraire/rest/1.0.0/route"
    params = {
        "resource": "bdtopo-osrm",
        "start": f"{lon1},{lat1}",
        "end": f"{lon2},{lat2}",
        "profile": "car",
        "optimization": "shortest",
        "getSteps": "false",
        "distanceUnit": "kilometer",
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data and data.get("distance"):
            return data["distance"]
    return None

@app.route('/get_producers', methods=['POST'])
def get_producers_endpoint():
    data = request.json
    adresse = data.get('adresse')
    ingredients = data.get('ingredients')
    if not adresse or not ingredients:
        return jsonify(["location", "ingredients"]), 400

    result = get_producers(adresse, ingredients)
    return jsonify(result), 200

def get_producers(adresse, ingredients):
    producers = {}
    reference_lat, reference_lon = obtenir_coordonnees(adresse)
    if reference_lat is None or reference_lon is None:
        print(f"Could not obtain coordinates for the reference address: {adresse}")
        return producers

    for ingredient in ingredients:
        producer_info = trouver_producteur_proche(ingredient, reference_lat, reference_lon)
        if producer_info:
            producers[ingredient] = producer_info
        else:
            print(f"Could not find producer for the ingredient: {ingredient}")

    return producers

@app.route('/load_xml', methods=['POST'])
def load_xml():
    global ingredients, adresse
    if 'file' not in request.files:
        return Response(response='No file part', status=400)
    file = request.files['file']
    if file.filename == '':
        return Response(response='No selected file', status=400)
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        try:
            dict_file = parser_xml.xml_to_json(filepath)
            ingredients_dict_file = dict_file["ingredients"]
            adresse_dict_file = dict_file["adresses"]
            ingredients = ingredients_dict_file
            adresse = adresse_dict_file
            return Response(response="OK", status=200, mimetype='application/json')
        except Exception as e:
            return Response(response=f'Error processing file: {str(e)}', status=400, mimetype='application/json')
    return Response(response='Invalid file type', status=400, mimetype='application/json')

class User:
    _id_counter = 0

    def __init__(self, username, pw):
        self.username = username
        self.pw = pw
        self.id = User._generate_id()
        self.authenticated = False
        self.active = False
        self.anonymous = False

    @classmethod
    def _generate_id(cls):
        cls._id_counter += 1
        return cls._id_counter

    def is_authenticated(self):
        return self.authenticated

    def set_authentication(self, auth_status: bool):
        self.authenticated = auth_status
        return self

    def is_active(self):
        return self.active

    def set_activity(self, active_status: bool):
        self.active = active_status
        return self

    def is_anonymous(self):
        return self.anonymous

    def set_anonymity(self, anonymous_status: bool):
        self.anonymous = anonymous_status
        return self

    def get_id(self):  # must return a string
        return f"{self.id}"

    @staticmethod
    def generate_auth_code(length=10):
        characters = string.ascii_letters + string.digits + "%*:.-~="
        return ''.join(random.choice(characters) for _ in range(length))

@app.route('/register', methods=['POST'])
def register():
    global users
    dict = request.get_json()

    if not dict or 'login' not in dict or 'password' not in dict:
        return Response(response=json.dumps({"error": "explication de l’erreur"}),
                        status=400,
                        mimetype='application/json')

    user = User(dict["login"], dict["password"])

    if user.username not in users.keys():
        # implemented with username:user_obj key-value pair
        users[user.username] = user
        user.set_authentication(True)
        auth = user.generate_auth_code()
        return Response(response=json.dumps({"auth_code": auth}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({"error": "user name already exists"}),
                        status=400,
                        mimetype='application/json')

@app.route('/login', methods=['POST'])
def login():
    global users
    dict = request.get_json()

    if not dict or 'login' not in dict or 'password' not in dict:
        return Response(response=json.dumps({"error": "explication de l’erreur"}),
                        status=400,
                        mimetype='application/json')

    user = users.get(dict["login"])

    if user and user.pw == dict["password"]:
        # verify if username exists and password given is same as the password
        user.set_authentication(True)
        auth = user.generate_auth_code()
        return Response(response=json.dumps({"auth_code": auth}),
                        status=200,
                        mimetype='application/json')
    else:
        return Response(response=json.dumps({"error": "Invalid username or password"}),
                        status=400,
                        mimetype='application/json')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5080, debug=True)
