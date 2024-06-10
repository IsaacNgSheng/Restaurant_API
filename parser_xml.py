import lxml.etree as etree
import json
import argparse


def validate_xml(filepath, schema):
    try:
        xmlschema = etree.XMLSchema(etree.parse(schema))
        xmlschema.assertValid(etree.parse(filepath))
    except etree.ParseError as e:
        print("Erreur de syntaxe XML: ", e)
        return False
    except etree.DocumentInvalid as e:
        print("Document invalide: ", e)
        return False
    return True


def xml_to_json(filepath):

    tree = etree.parse(filepath)
    root = tree.getroot()
    output = {}

    # Extracting address
    adresse = root.find(".//adresse_restaurant")
    address = {
        "rue": adresse.find("rue").text,
        "code_postal": adresse.find("code_postal").text,
        "ville": adresse.find("ville").text
    }
    output["adresse"] = address

    # Extracting ingredients
    ingredients = {}
    for recette in root.findall(".//recette"):
        nbCouverts = recette.get("nbCouverts")
        if nbCouverts is None:
            print("Attribut 'nbCouverts' manquant !")
            return None
        nbCouvertsParJour = recette.get("nbCouvertsParJour")
        if nbCouvertsParJour is None:
            print("Attribut 'nbCouvertsParJour' manquant !")
            return None
        for ingredient in recette.findall(".//ingredient"):
            quantite = (int(nbCouvertsParJour) / int(nbCouverts)) * int(ingredient.get("qte"))
            id = ingredient.get("id")
            label = root.find(".//stocks/ingredient[@id='{}']".format(id)).text
            conservation = root.find(".//stocks/ingredient[@id='{}']".format(id)).get("conservation")
            if label in ingredients:
                ingredients[label]["quantite"] += quantite
            else:
                ingredients[label] = {"quantite": quantite, "conservation": conservation}
    output["ingredients"] = ingredients
    return output


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("-xml", "--inputXML", help="chemin du fichier XML à parser")
    parser.add_argument("-xsd", "--inputSchema", help="chemin du fichier XSD à parser")
    parser.add_argument("-o", "--outputFile", help="chemin du fichier JSON de sortie")
    args = parser.parse_args()

    if args.inputXML is None:
        print("Veuillez spécifier un fichier XML en argument")
        exit(1)

    if args.inputSchema is None:
        print("Veuillez spécifier un fichier XSD en argument")
        exit(1)

    if validate_xml(args.inputXML, args.inputSchema):
        data = xml_to_json(args.inputXML)
        if args.outputFile is not None:
            with open(args.outputFile, "w") as f:
                json.dump(data, f)
                print("Fichier JSON généré avec succès !")
        else:
            print(json.dumps(data))

