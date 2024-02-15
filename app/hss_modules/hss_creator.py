import pandas as pd
# import numpy as np
import json
import re

# TODO
# faire un checker de nom (EPS_Name) -> match requirements de Hitachi -> informer l'utilisateur au moment où il nomme sa gauge si le format est valide ou non
# reporter les valeurs par défaut du sem_chef au template JSON ?
# pour le fichier d'output, créer le fichier si il n'existe pas -> faire une fonction ou à l'initialisation
# remove trailing comma eps_data if pb
# par rapport aux requirements de recette, voir pour ajouter ou supprimer des colonnes de EPS_Data par exemple (format firewall ou permis)
# nettoyer les appels de fonction pour qu'ils soient fait au bon endroit et si possible de manière unique
# implémenter une logique pour le type de parser -> if fichier genepy -> mapping genepy
# nommage des df etc à faire
# autofill pour recette fonctionnelle et exhaustive -> concertation des points à apporter -> faire en fonction de la doc et de l'xp de Romain
# dans le mapping -> faire correspondre les "TypeN" au template pour le merge des infos de eps_data au noms de colonne du template
# faire un checker pour csv ET hss -> intégrer le tool d'alex / voir si l'ordre des colonnes importe vraiment


class adaptativeRecipeFilling:
    def __init__(self) -> None:
        pass

    def set_id(self, dataframe, key_name=None) -> None:
        if dataframe == "<EPS_Data>":
            self.eps_data['EPS_ID'] = range(
                1, min(self.gauges.shape[0] + 1, 9999))
            # preventing data to be out of range -> match doc
            if any(id > 9999 for id in self.eps_data['EPS_ID']):
                raise ValueError("EPS_ID values cannot exceed 9999")
        # else:
        #     HssCreator. ['EPS_ID'] = range(1, min(self.gauges.shape[0] + 1, 9999))
        #     # preventing data to be out of range -> match doc
        #     if any(id > 9999 for id in self.eps_data['EPS_ID']):
        #         raise ValueError("EPS_ID values cannot exceed 9999")


class HssCreator:
    # TODO add eps_dataframe: pd.DataFrame
    def __init__(self, eps_dataframe: pd.DataFrame, template=None, output_file=None):
        # "imports"
        if template is None:
            template = "/work/opc/all/users/chanelir/semrc/assets/template_SEM_recipe.json"
        if output_file is None:
            output_file = "/work/opc/all/users/chanelir/semrc-outputs/recette.hss"
        self.json_template = self.import_json(template)
        # initialization
        self.num_columns = 0
        self.output_file = output_file
        self.eps_data = eps_dataframe
        self.first_level_df = pd.DataFrame()
        # dict which contains all the second level sections of the second level JSON template
        self.dict_of_second_level_df = {}

    def import_json(self, template_file) -> any:
        '''fonction that opens a JSON file in reading mode qui ouvre en lecture un fichier JSON et le retourne si il est clean sinon une erreur est relevée'''
        try:
            with open(template_file, 'r') as f:
                template_file = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading JSON file: {e}")
        return template_file

    def json_to_dataframe(self) -> None:
        '''method that parses a valid JSON file (no redondant data in same section) into a dataframe (writes it in instance - not return)'''
        # initialization of first
        first_lines_first_level = {}
        # checking which treatment the template's sections will have
        for key, value in self.json_template.items():
            if isinstance(value, dict):
                if isinstance(list(value.values())[0], list):
                    self.dict_of_second_level_df[key] = pd.DataFrame(value)
                else:
                    self.dict_of_second_level_df[key] = pd.json_normalize(
                        value)
            else:
                first_lines_first_level[key] = value
        # here we assume there is only one value per section with one name of section per row
        # conversion of the 3 first lines of the template into a one level dataframe (normalize)
        self.first_level_df = pd.json_normalize(first_lines_first_level)

    # TODO avoir template['<EPS_Data>'] pour get columns in class eps creator
    # then hssCreator.template['<EPS_Data>'] = EPSCreator.template['<EPS_Data>'] in HssCreator
    # pour l'instant, modify the columns before eps assignation in template header
    def add_MP(self, nb_of_mp_to_add) -> None:
        if nb_of_mp_to_add < 1:
            return None
        template_header_df = pd.DataFrame(
            self.dict_of_second_level_df["<EPS_Data>"])
        # FIXME implement code in order to iterate in mp creation
        for mp in range(nb_of_mp_to_add):
            # type counting in order to add Type column before all the MPn columns
            i = 1
            while True:
                if f"Type{i}" in template_header_df.keys():
                    i += 1
                    pass
                else:
                    # TODO or change to empty
                    template_header_df[f"Type{i}"] = ''
                    break
            # count MP number by "MPn_X" key
            mp_count = 1
            i = 1
            while i:  # FIXME logic ?
                if f"MP{i}_X" in template_header_df.keys():
                    mp_count = i
                    i += 1
                else:
                    # TODO écrire en dur avec un mapping ou faire le code suivant ?
                    for col, val in template_header_df.items():
                        # TODO dans l'idéal : détecter le nombre de MP déjà présent pour créer un MP+1
                        # FIXME put col in str and it should work
                        if str(col).startswith(f"MP{mp_count}"):
                            new_col_name = str(col).replace(
                                f"MP{mp_count}", f"MP{mp_count + 1}")
                            template_header_df[f"{new_col_name}"] = val
                    break
        template_header_df = template_header_df.drop(
            template_header_df.index, axis=0)
        self.dict_of_second_level_df["<EPS_Data>"] = template_header_df

    def drop_unused_columns(self) -> None:
        '''method that **should** drop all columns of the df_template that the title is not in the df_data ONLY IF the columns title is already matching'''
        # get EPS_Data section from template
        # check de correspondance -> ajout des donnée finales ou drop des données du template -> création de EPS_Data final
        # itération dans les noms de colonnes du template pour ajouter les colonnes manquantes à EPS_Data
        # for column_name in pd.DataFrame(self.dict_of_second_level_df["<EPS_Data>"]):
        #     if column_name not in self.eps_data.columns:
        #         # ajout de la colonne au dataframe eps_data (par comparaison au template)
        #         self.eps_data[column_name] = ''  # TODO voir s'il faut pas set NAN ou une value vide ''
        template_header = pd.DataFrame(
            self.dict_of_second_level_df["<EPS_Data>"])
        template_header = template_header.drop(template_header.index, axis=0)
        for column_name, value_name in self.eps_data.items():
            if column_name in template_header:
                # ajout des valeurs du dataframe eps_data aux header du dataframe de template
                template_header[column_name] = value_name
        self.dict_of_second_level_df["<EPS_Data>"] = template_header

    # TODO séparer la logique de calcul des valeurs du flow (qui fait simplement du printing)  
    def set_type_in_eps_data(self, number_of_mp) -> None:
        '''define what it does'''  # TODO
        # sanitize value
        if number_of_mp < 1:
            number_of_mp = 1
        for col in self.dict_of_second_level_df["<EPS_Data>"]:
            if col == "Type1":
                self.dict_of_second_level_df["<EPS_Data>"][col] = 1
            # WARNING maintenabilité : 11 dépends du nommage et de la place de la colonne Type11
            elif str(col).startswith("Type") and int(str(col)[4:6]) < 11:
                self.dict_of_second_level_df["<EPS_Data>"][col] = 2
        # defines if writing data is necessary or not - for MP
        # if data empty in MPn section is empty, corresponding (relative value) type is set to "" else fill with 2s
        # WARNING maintenabilité
        for mp_nb in range(1, number_of_mp + 1):
            mp_n_is_empty = False
            for col, val in self.dict_of_second_level_df["<EPS_Data>"].items():
                if str(col).startswith(f"MP{mp_nb}"):
                    if pd.isnull(val).all():
                        mp_n_is_empty = True
                    else:
                        mp_n_is_empty = False
            if mp_n_is_empty is True:
                self.dict_of_second_level_df["<EPS_Data>"][f"Type{mp_nb + 10}"] = ""
            else:
                self.dict_of_second_level_df["<EPS_Data>"][f"Type{mp_nb + 10}"] = 2

    def dataframe_to_hss(self) -> str:
        '''method that converts a dataframe into a HSS format (writes it as a file)'''
        whole_recipe = ""
        # we assume there is only one fixed value
        # treatment of first level keys
        for titre_premier_niveau in self.first_level_df.columns:
            whole_recipe += f"{titre_premier_niveau}\n"
            # treatment of first level values
            for value_premier_niveau in self.first_level_df[titre_premier_niveau]:
                whole_recipe += f"{value_premier_niveau}\n"
        # treatment of keys (first level (section) and second level (dataframe.columns)) and second level values (dataframe.to_csv)
        for section, dataframe in self.dict_of_second_level_df.items():
            # writing of first level keys (in dataframe)
            whole_recipe += f"{section}\n"
            header_str = ','.join(dataframe.columns)
            # writing of second level keys
            whole_recipe += f"#{header_str}\n"
            csv_str = dataframe.to_csv(index=False, header=False)
            # writing of second level values
            for line in csv_str.splitlines():
                whole_recipe += f"{line}\n"
        # removes the last backspace '\n' added by iteration at the data's end
        whole_recipe = whole_recipe.rstrip('\n')
        return whole_recipe

    def rename_eps_data_header(self, string_to_edit) -> str:
        '''method that converts all "TypeN" with N a number in "Type"'''
        # TODO modifier seulement la section <EPS_Data> / d'un autre côté RCPD attends des "Type" et pas autre chose
        new_string = re.sub(r"Type(\d+)", r"Type", string_to_edit)
        return new_string

    def set_commas_afterwards(self, string_to_modify) -> str:
        '''this method gets the max value number in the output file in order to set the self.num_columns and know the number of commas to write in the file'''
        # cleans the string - removes trailing eventual whitespace
        lines = [line.rstrip() for line in string_to_modify.split('\n')]
        # counts the max number of elements in each rows
        # warning : number separated with commas (english notation) may false the calculation here. Maybe use .shape[0] pandas attribute
        self.num_columns = max(line.count(',') + 1 for line in lines)
        # defines and writes the number of commas needed for each lines
        modified_string = ""
        for line in lines:
            num_commas = self.num_columns - (line.count(',') + 1)
            modified_string += line + "," * num_commas + "\n"
        return str(modified_string)

    def write_in_file(self, mp_to_add) -> None:
        # get template
        self.json_to_dataframe()
        # add mp if told to
        self.add_MP(mp_to_add)
        # gets data from otherClass.eps_data_df
        self.drop_unused_columns()
        self.set_type_in_eps_data(mp_to_add + 1)
        whole_recipe_template = self.dataframe_to_hss()
        # whole_recipe_EPS_Data
        # renaming of "TypeN" into "Type" - doesn't apply on df so we do to recipe output string
        whole_recipe_good_types = self.rename_eps_data_header(
            whole_recipe_template)
        # cleans, calculates and writes the correct number of commas in the output file
        whole_recipe_to_output = self.set_commas_afterwards(
            whole_recipe_good_types)
        with open(self.output_file, 'w') as f:
            f.write(whole_recipe_to_output)


# runCsv = HssCreator(pd.read_csv("/work/opc/all/users/chanelir/semrc-test/measure_result.temp"))
# runCsv.set_type_in_eps_data(3)
