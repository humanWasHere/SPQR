import pandas as pd

class clipboardParser:

    def clipboard_to_dataframe(self):
        # user_input = input("Coller le contenu de votre clipboard ici (Ctrl + V -> Enter): ")

        # Lecture des données du presse-papiers
        df = pd.read_clipboard()

        # Affichage du dataframe
        print(df.head())
