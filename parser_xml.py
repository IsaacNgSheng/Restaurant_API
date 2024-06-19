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

    # Extracting addresses
    addresses = {}
    adresse_siege = root.find(".//adresse_siege")
    if adresse_siege is not None:
        addresses["siege"] = {
            "rue": adresse_siege.find("rue").text,
            "code_postal": adresse_siege.find("code_postal").text,
            "ville": adresse_siege.find("ville").text
        }

    adresse_franchise = root.find(".//adresse_franchise")
    if adresse_franchise is not None:
        addresses["franchise"] = {
            "rue": adresse_franchise.find("rue").text,
            "code_postal": adresse_franchise.find("code_postal").text,
            "ville": adresse_franchise.find("ville").text
        }

    output["adresses"] = addresses

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

            # Correctly locate ingredients under <stocks>
            ingredient_node = root.find(".//stocks/ingredient[@id='{}']".format(id))
            if ingredient_node is not None:
                label = ingredient_node.get("id")  # Changed to get the id attribute
                conservation = ingredient_node.get("conservation")
                if label in ingredients:
                    ingredients[label]["quantite"] += quantite
                else:
                    ingredients[label] = {"quantite": quantite, "conservation": conservation}
            else:
                print(f"Ingredient with id '{id}' not found in <stocks>")

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
            print(json.dumps(data, indent=4))
