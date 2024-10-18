# Version 1.0.0
<!-- sum up all previous main changes from v0 to v1-->

## Version 0.3

Released 17/10/2024  
### **TL; DR**
Main changes coming with SPQR v0.3.0:  
- **CLI - 3 new commands (init, edit, upload)**  
- **Documentation and auto-documentation**  

See detail below.

---

### New features (functional)
SPQR version 0.3.0 welcomes new features (functional):  
- **CLI - `init` command**: Creates either configuration file, coordinate file (ssfile genepy like) or both. New default files in app source code.
- **CLI - `edit` command**: Edits a recipe interactively. Needs a recipe, configuration file and recipe name according to the configuration file. Generates a recipe with formatted name.
- **CLI - `upload` command**: Uploads either a given recipe, a given layout or both. 

### Changes and improvements
As well as some changes:  
- Fixed number of rows and columns in OPCField reverse matricing.
- CLI - `start` command renamed to `test`.  
- Enhance short command names (more logical usage).
- Enhancing test quality (file storage and test process). Up to 104 tests.  
- Better differentiation between CSV and JSON recipe output (more maintainable).  
- (dry run recipedirector.py) ?

### Other implementations (non-functional)
- **Documentation and auto-documentation**. Use of _Sphinx_ with html, md and rst files. Word documentation has been reworked and reported in markdown. Documentation is now centralized in Unix env. A direct link from the application now exists. Using/matching recognized template in the software development industry.  
- Adding application trackers in order to output metrics and retrieve information about our application.  
- Formalization of a deployment procedure. Meant to ease delivery iterative process.
- DevOps - Jenkins pipeline creation (provisional).

### Delete
- No deletes.

### Fixed issues
- Value of configuration file was not taken into account for recipe/CSV parsing. Thanks, Marc, for highlighting it!  
- Skipping CSV lines with extra fields. --> Romain B  

### Known issues
- Measurement performances and structure.  

### Next steps
- Cloud migration.  
- Jenkins implementation.  
- (P18 recipe creation) ?

## Version 0.2.0
Released 07/08/2024  
### **TL; DR**
Main changes coming with SPQR v0.2.0:  
- **Adding and edit on CLI - build subcommand (`-l` and `-m`)**  
- **Changes on configuration file**  
- **Application logging added**
- **Validateur de données d'entrée**

See detail below.

---

### Changements majeurs
1) Fichier de config JSON :
- Ajout champ "polarity" clear/dark pour le masque
- "mp_template" peut maintenant prendre deux templates pour line ou space de résine. Cf doc ou example.json
- Renommage des champs "parser" → "coord_file" et inversion "n_rows_cols" → "n_cols_rows" pour être plus cohérent avec X/Y.
(mettre à jour vos .json de travail existant !)
- Les champs optionnels peuvent ne plus apparaître (écrits avec des valeurs vides précédemment)
2) La syntaxe de l’option -l/--line_selection a évolué pour permettre une section d’intervalles multiples (avec valeurs indiquées comprises). Ex :  spqr build -c config.json -l 1-20 40-50
3) Ajout d’une option -m pour écrire le fichier de mesure intermédiaire (format csv)

Rappel : on peut maintenant utiliser une recette Hitachi existante (CSV) comme source de coordonnées.

### Ajouts QA
- Tests unitaires, d’intégration et end-to-end
- Logging
- Validateur de données d’entrée

### Correctifs et support utilisateur
- Correction des bugs de rotation EP, colonnes Type, sections dupliquées, renommage gauges OPCField
- Suppression des points de mesure invalides
- Amélioration du parsing pour les ssfiles n’ayant pas le même nombre de colonnes pour chaque ligne : on conserve l’information
- Hot fix utilisateur (plus de doublons de points de mesure, gestion des rulers calibre sans section “<comment>”)


## Version 0.1.0 ?
Released 10/07/2024  
### **TL; DR**
Main changes coming with SPQR v0.1.0:  
- **Application passed in CLI**
- **Now working with configuration file**
- **Application deployed to Crolles' env**
- **2 new coordinate sources (CSV and OPCField)**

See detail below.

---

### Nouveautés majeures
- Ajout de 2 nouvelles sources de coordonnées pour générer une recette :
recette CSV existante (reuse HSS) & OPCfield reverse (géneration de matrice)
- Ajout d'une interface en ligne de commande (CLI)
- Utilisation d'un fichier de configuration (format JSON, exemple fourni)
- Application déployée sur Crolles -> plus besoin de cloner le code source

### Quick start
•	spqr build --help
spqr build -c ./my_config.json
•	exemple de fichier de configuration →   example_config.json
•	documentation utilisateur (en construction) →   SPQR's_user_documentation.docx

### Disscussed, to implement
- OPCField reverse : possibilité de commencer la numérotation de motif autrement que ‘A1’ -> une option pourra être ajoutée
- option PHOTO 248nm à ajouter aux modes existant PH/ET/PH_HR/ET_HR
- actuellement l’autofocus est par défaut au même endroit que l’addressing -> paramètre autofocus x/y à ajouter + sanity check edge présent dans le FOV layout
- mesure des motifs à la volée : possibilité d’exporter / de modifier les résultats ? -> à étudier
- export de recette Simpl : prévu moyen/long terme si le besoin est confirmé
- (R&D) classification auto des motifs : sous-projet IA à envisager
- gérer plusieurs sources pour une même recette et pouvoir sélectionner finement les motifs : brainstorming nécessaire pour définir la spec

### Next steps
Court terme : prendre 2 templates MP pour width/space, ajouter sanity checks, export résultats de mesure
Moyen terme : mieux gérer les layers (targets, visible, in layout), manger rapport LMC, …
