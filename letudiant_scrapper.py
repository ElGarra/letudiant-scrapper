import json
import re
from turtle import st
import requests
from bs4 import BeautifulSoup
import xlsxwriter


class LetudiantScrapper():
    def __init__(self):
        self.main_url = "https://www.letudiant.fr/classements/classement-des-ecoles-d-ingenieurs.html?page="
        self.ecoles_urls = []
        self.ecoles_names = []
        self.ecoles_chiffres = [] 
        self.ecoles_scores = []
        self.ecoles_debrief = []
        self.ecoles_categories = []
        self.ecoles_dicts = []
        self.current_url = None
        self.excel_workbook = xlsxwriter.Workbook('letudiant_database.xlsx')
        self.excel_worksheet = self.excel_workbook.add_worksheet()
        self.ecoles_info_list = []

    def get_ecoles_urls(self):
        urls_key_string = '<a class="tw-cursor-pointer" href="https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/'
        for tag in self.html.find_all(re.compile("a")):
            str_tag = str(tag)
            if urls_key_string in str_tag:
                url = re.findall(r'(https?://[^\s]+)', str_tag)[0]
                aux_index = url.index('>')
                url = url[0:aux_index-1]
                if url not in self.ecoles_urls:
                    self.ecoles_urls.append(url)

    def request_ranking_pages(self):
        for i in range(1, 10):
            self.current_url = self.main_url + str(i)
            self.data = requests.get(self.current_url)
            self.html = BeautifulSoup(self.data.text, "html.parser")
            self.get_ecoles_urls()

    def get_ecole_name(self, ecole_name_tag):
        for tag in ecole_name_tag:
            name = tag.get_text().split(" ")
            final_name = ""
            aux_string = ""
            for char in name:
                if char != '' and char != '\n':
                    aux_string += char + " "
            len_aux_string = len(aux_string)
            final_name = aux_string[0:len_aux_string - 2]
            print(final_name)
            return final_name

    def get_ecole_chiffres(self, ecole_chiffres):
        # Case in which we have number of students and formation
        if 2 < len(ecole_chiffres):
            aux_nombre_eleves = ecole_chiffres[0].get_text().split(" ")
            nombre_eleves_2 = aux_nombre_eleves[1] + "-" + aux_nombre_eleves[3]
            nombre_eleves = nombre_eleves_2.replace("\xa0", "")
        else:
            nombre_eleves = '-'
        formations = ecole_chiffres[1].get_text()
        return [nombre_eleves, formations]

    def get_ecole_score(self, ecole_score):
        score = ""
        for elem in ecole_score:
            aux_list = elem.get_text().split(" ")
            for string in aux_list:
                elem_lenght = len(string)
                if 2 < elem_lenght:
                    score = string[0:elem_lenght - 1]
                    return score
        score = '-'
        return score
      
    def get_ecole_debrief(self, ecole_debrief):
        debrief_data = ecole_debrief[1:4]
        debrief_list = []
        for data in debrief_data:
            debrief_list.append(data.get_text().replace('\n',''))
        return debrief_list
    
    def get_ecole_categories(self, categories):
        categories_list = []
        for category in categories:
            categories_list.append(category.get_text().replace('\n', '').replace(' ', ''))
        return categories_list


    def get_ecole_dicts(self, ecole_dicts):
        sentences_list = []
        for sentence in ecole_dicts:
            sentence_list = sentence.get_text().split(" ")
            aux_string = ""
            for char in sentence_list:
                if char != '' and char != '\n' and char != '\n\n':
                    aux_string += char + " "
                    def_string = aux_string.replace('\n', '')
            def_string_2 = def_string[0:-1]
            sentences_list.append(def_string_2.split(' '))

        dicts_list = [
            {
                "Durée d'habilitation CTI": ' '.join(sentences_list[0][3:]),
                "Moyenne au bac des intégrés": ' '.join(sentences_list[1][5:]),
                "Nombre d'élèves par enseignant": ' '.join(sentences_list[2][4:]),
                "Part d'enseignants-chercheurs": ' '.join(sentences_list[3][2:]),
                "Pourcentage de diplômés poursuivant en thèse": ' '.join(sentences_list[4][6:]),
                "Nombre de doctorants (y compris cotutelles)": ' '.join(sentences_list[5][6:]),
                "Nombre d'enseignants HDR": ' '.join(sentences_list[6][3:])
            },
            {
                "Part d'élèves en alternance": ' '.join(sentences_list[7][4:]),
                "Nombre total d'alternants": ' '.join(sentences_list[8][3:]),
                "Durée minimale des stages en entreprise": ' '.join(sentences_list[9][6:]),
                "Politique de chaires industrielles": ' '.join(sentences_list[10][4:]),
                "Forums entreprises": ''.join(sentences_list[11][2:]),
                "Forums entreprises (+ de 250 salariés)": ' '.join(sentences_list[12][6:]),
                "Forums entreprises (réseau PME)": ' '.join(sentences_list[13][4:]),
                "Nombre d'anciens sur LinkedIn": ' '.join(sentences_list[14][4:])
            },
            {
                "Pourcentage d'étudiants étrangers": ' '.join(sentences_list[15][3:]),
                "Niveau d'anglais exigé": ' '.join(sentences_list[16][3:]),
                "Deuxième langue étrangère": ' '.join(sentences_list[17][3:]),
                "Durée minimale à l'étranger (hors apprentissage)": ' '.join(sentences_list[18][6:]),
                "Durée minimale à l'étranger pour les apprentis": ' '.join(sentences_list[19][7:]),
                "Diplômés ayant passé plus d'un semestre à l'étranger en échange académique": ' '.join(sentences_list[20][11:]),
                "Diplômés ayant passé plus d'un semestre à l'étranger en stage": ''.join(sentences_list[21][10:]),
                "Élèves par accord de double diplôme international": ' '.join(sentences_list[22][7:]),
                "Pourcentage de double diplômés internationaux": ' '.join(sentences_list[23][5:]),
                "Réputation internationale": ' '.join(sentences_list[24][2:])
            },
            {
                "Salaire à la sortie": ' '.join(sentences_list[25][4:]),
                "Insertion à deux mois": ' '.join(sentences_list[26][4:]),
                "Diplômés en poste à l'étranger": ' '.join(sentences_list[27][5:])
            },
            {
                "Industrie automobile, aéronautique, navale et ferroviaire": ' '.join(sentences_list[28][6:]),
                "BTP, construction": ' '.join(sentences_list[29][2:]),
                "Énergie": ' '.join(sentences_list[30][1:]),
                "Institutions financières, banque, assurance": ' '.join(sentences_list[31][4:]),
                "Industrie des technologies de l'information": ' '.join(sentences_list[32][5:]),
                "Industrie chimique ou pharmaceutique": ' '.join(sentences_list[33][4:]),
                "Technologie de l'information (services)": ' '.join(sentences_list[34][4:]),
                "Industrie agroalimentaire": ' '.join(sentences_list[35][2:]),
                "Agriculture, sylviculture, pêche": ' '.join(sentences_list[36][3:]),
                "Transports": ' '.join(sentences_list[37][1:]),
                "Fonction publique": ' '.join(sentences_list[38][2:]),
                "Recherche et enseignement": ' '.join(sentences_list[39][3:]),
                "Sociétés de conseil, bureaux d'études": ' '.join(sentences_list[40][5:]),
                "Autres secteurs": ' '.join(sentences_list[41][2:]),
            },
            {
                "Cycle prépa intégrée - Nombre d'intégrés à bac": ' '.join(sentences_list[42][8:]),
                "Cycle ingénieur - Nombre d'intégrés issus de prépa intégrée ou d'une prépa commune sans distinction géographique": ' '.join(sentences_list[43][16:]),
                "Cycle ingénieur - Nombre d'intégrés issus de CPGE": ' '.join(sentences_list[44][8:]),
                "Cycle ingénieur - Nombre d'intégrés issus d'admissions parallèles": ' '.join(sentences_list[45][8:]),
                "Part d'intégrés via les admissions parallèles": ' '.join(sentences_list[46][6:]),
                "Nombre d'intégrés issus de BTS et ATS": ' '.join(sentences_list[47][7:]),
                "Moyenne au bac des intégrés issus de BTS et ATS": ' '.join(sentences_list[48][10:]),
                "Nombre d'intégrés issus de DUT": ' '.join(sentences_list[49][5:]),
                "Moyenne au bac des intégrés issus de DUT": ' '.join(sentences_list[50][8:]),
                "Nombre d'intégrés issus de l'université": ' '.join(sentences_list[51][5:]),
                "Moyenne au bac des intégrés issus de l'université": ' '.join(sentences_list[52][8:]),
                "Proportion de bacheliers S": ' '.join(sentences_list[53][4:]),
                "Proportion de bacheliers STI2D": ' '.join(sentences_list[54][4:]),
                "Proportion autres bacheliers": ' '.join(sentences_list[55][3:]),
                "Nombre de bacheliers ES": ' '.join(sentences_list[56][4:]),
                "Nombre de bacheliers L": ' '.join(sentences_list[57][4:]),
                "Nombre de bacheliers STL": ' '.join(sentences_list[58][4:]),
                "Nombre de bacheliers STAV": ' '.join(sentences_list[59][4:]),
                "Nombre d'intégrés issus d'autres bacs": ' '.join(sentences_list[60][5:]),
                "Nombre de bacheliers Maths et autre science 'exacte'": ' '.join(sentences_list[61][8:]),
                "Nombre de bacheliers Science 'exacte' et autre science 'exacte' hors maths": ' '.join(sentences_list[62][11:]),
                "Nombre de bacheliers Maths et SHS": ' '.join(sentences_list[63][6:]),
                "Nombre de bacheliers Science 'exacte' hors maths et SHS": ' '.join(sentences_list[64][9:]),
                "Nombre de bacheliers autres doublettes": ' '.join(sentences_list[65][5:]),
            },
            {
                "Cours sur le développement durable": ' '.join(sentences_list[66][5:]),
                "Labels environnementaux": ' '.join(sentences_list[67][2:])
            },
            {
                "Ouverture à de nouveaux publics": ' '.join(sentences_list[68][5:]),
                "Frais de scolarité par an": ' '.join(sentences_list[69][5:]),
                "Boursiers Crous": ' '.join(sentences_list[70][2:]),
                "Présence sur Parcoursup": ' '.join(sentences_list[71][3:]),
                "Parité au sein de la promotion (Hommes/Femmes)": ' '.join(sentences_list[72][7:]),
                "Etudiants en situation de handicap": ' '.join(sentences_list[73][5:]),
                "Villes d'implantation de l'école": ' '.join(sentences_list[74][4:]),
                "Élèves rémunérés pendant leurs études": ' '.join(sentences_list[75][5:]),
                "Statut de l'école": ' '.join(sentences_list[76][3:]),
                "Ministère de tutelle": ' '.join(sentences_list[77][3:]),
                "Spécialités proposées": ' '.join(sentences_list[78][2:]),
                "Taille des promos en cycle ingénieur": ' '.join(sentences_list[79][6:]),
                "Budget alloué aux associations par élève": ' '.join(sentences_list[80][6:]),
                "Valorisation de l'engagement étudiant": ' '.join(sentences_list[81][4:]),
            }
        ]
        return dicts_list

    def get_ecole_info(self):
        for ecole in self.ecoles_urls:
            self.ecole_data = requests.get(ecole)
            self.ecole_html = BeautifulSoup(
                self.ecole_data.text, "html.parser")
            # Get Ecole Names
            self.ecole_name_tag = self.ecole_html.find_all(
                "h1", class_="tw-w-full tw-text-center sm:tw-text-left tw-font-heading tw-text-4xl tw-leading-8 sm:tw-text-5xl sm:tw-leading-9 tw-mb-2")
            name = self.get_ecole_name(self.ecole_name_tag)
            self.ecoles_names.append(name)

            # Get Ecole Chiffres
            self.ecole_chiffres_tag = self.ecole_html.find_all(
                "span", class_="tw-block tw-font-heading tw-text-4xl tw-leading-8")
            chiffres = self.get_ecole_chiffres(self.ecole_chiffres_tag)
            self.ecoles_chiffres.append(chiffres)

            # Get Ecole Score
            self.ecole_score_tag = self.ecole_html.find_all("span", class_="tw-text-2xl tw-font-heading")
            score = self.get_ecole_score(self.ecole_score_tag)
            self.ecoles_scores.append(score)

            # Get Ecole Debrief
            self.ecole_debrief_tag = self.ecole_html.find_all("div", class_="tw-font-medium")
            debrief = self.get_ecole_debrief(self.ecole_debrief_tag)
            self.ecoles_debrief.append(debrief)

            # Get Ecole categories
            self.ecole_categories_tag = self.ecole_html.find_all("div", class_="text-align-right")
            categories = self.get_ecole_categories(self.ecole_categories_tag)
            self.ecoles_categories.append(categories)

            # Get Ecole dicts
            self.ecole_dicts_tag = self.ecole_html.find_all("div", class_="criterion-row tw-flex tw-flex-wrap tw-border-b tw-border-gray-600 tw-text-sm")
            dicts = self.get_ecole_dicts(self.ecole_dicts_tag)
            self.ecoles_dicts.append(dicts)

    def fill_ecole_dict(self):
        self.counter = 0
        for i in range(len(self.ecoles_names)):
            self.info_format = {
                "Classement": self.counter + 1,
                "Nom": self.ecoles_names[self.counter],
                "Score": self.ecoles_scores[self.counter],
                "Nombre d'élèves": self.ecoles_chiffres[self.counter][0],
                "Nombre de formations": self.ecoles_chiffres[self.counter][1],
                "N° d'eleves en alternance": self.ecoles_debrief[self.counter][0],
                "Statut": self.ecoles_debrief[self.counter][1],
                "Durée du cursus": self.ecoles_debrief[self.counter][2],
                "Score Excellence académique": self.ecoles_categories[self.counter][0],
                "Score Ouverture internationale": self.ecoles_categories[self.counter][1],
                "Score Proximité avec les entreprises": self.ecoles_categories[self.counter][2],
                "Score Ouverture à de nouveaux publics": self.ecoles_categories[self.counter][3],
                "Detail Excellence académique": self.ecoles_dicts[self.counter][0],
                "Detail Proximité avec les enterprises": self.ecoles_dicts[self.counter][1],
                "Detail Ouverture internationale": self.ecoles_dicts[self.counter][2],
                "Detail Devenir des diplomes": self.ecoles_dicts[self.counter][3],
                "Detail Débouchés": self.ecoles_dicts[self.counter][4],
                "Detai Origine des intégrés": self.ecoles_dicts[self.counter][5],
                "Detail Environnement": self.ecoles_dicts[self.counter][6],
                "Detail Mieux connaitre l'ecole": self.ecoles_dicts[self.counter][7],
                "Lien": self.ecoles_urls[self.counter],
            }
            self.ecoles_info_list.append(self.info_format)
            self.counter += 1

    def create_json_file(self):
        json_list = json.dumps(
            self.ecoles_info_list, ensure_ascii=False, indent=4).encode('utf8')
        with open("letudiant.json", "w", encoding="utf8") as file:
            file.write(json_list.decode())

    def create_excel_database(self):
        pass



link = "https://www.letudiant.fr/etudes/annuaire-enseignement-superieur/etablissement/etablissement-centralesupelec-cursus-ingenieur-supelec-7696.html#classement-des-ecoles-d-ingenieurs"
data = requests.get(link)
html = BeautifulSoup(data.text, "html.parser")
esk = html.find_all("div", class_="criterion-row tw-flex tw-flex-wrap tw-border-b tw-border-gray-600 tw-text-sm")
print(len(esk))
all_elem_list = []
for elem in esk:
    elem_list = elem.get_text().split(" ")
    # print(elem_list)
    aux_string = ""
    for char in elem_list:
        if char != '' and char != '\n' and char != '\n\n':
            aux_string += char + " "
            def_string = aux_string.replace('\n', '')
    def_string_2 = def_string[0:-1]
    print(def_string_2.split(' '))
    
    # print(elem.get_text().split(" "))
# print(esk[0].get_text().split(" "))

# print(esk[1].get_text())


scrapper = LetudiantScrapper()
scrapper.request_ranking_pages()
scrapper.get_ecole_info()
scrapper.fill_ecole_dict()
scrapper.create_json_file()

