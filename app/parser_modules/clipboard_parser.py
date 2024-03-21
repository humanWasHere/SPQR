import pandas as pd

# FIXME highly connected to GUI ? 


class ClipboardParser:

    def clipboard_to_dataframe(self):
        '''explain what this fonction does here'''
        # user_input = input("Coller le contenu de votre clipboard ici (Ctrl + V -> Enter): ")

        # Lecture des données du presse-papiers
        df = pd.read_clipboard()

        # Affichage du dataframe
        print(df.head())
