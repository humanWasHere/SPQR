import logging
from pathlib import Path
from pydantic import BaseModel, ValidationError
from typing import List, Union, Dict, Optional

logger = logging.getLogger(__name__)


class CheckConfigPydantic:
    # Modèle de base pour les paramètres communs
    class BaseRecipe(BaseModel):
        recipe_name: Optional[str] = None
        output_dir: Optional[str] = None
        layout: Path
        layers: List[Union[int, float]]
        magnification: int
        step: str | List[str]

        @classmethod
        def validate_step(cls, value):
            valid_steps = {"PH", "ET", "PH_HR", "ET_HR"}
            if value not in valid_steps:
                logger.warning(f"ValueError: Invalid step value: {value}. Must be one of {valid_steps}")
                # raise ValueError(f"Invalid step value: {value}. Must be one of {valid_steps}")
            return value

    # Modèle pour OPCfield
    class OPCfield(BaseRecipe):
        parser: Optional[str] = None
        ap1_template: Optional[str] = None
        ap1_mag: Optional[int] = None
        ep_template: Optional[str] = None
        eps_template: Optional[str] = None
        mp_template: Optional[Union[str, Dict[str, str]]] = None
        origin_x_y: List[float]
        step_x_y: List[int]
        n_rows_cols: List[int]
        ap1_offset: List[float]

    # Modèle pour un autre type de recette (exemple)
    class GenepyCalibreRulers(BaseRecipe):
        parser: str

    # Fonction pour charger et valider le fichier JSON
    @staticmethod
    def validate_json_file(json_config_content: dict, recipe_type_start: str | Path | None, user_recipe_build: str | None):
        if recipe_type_start is None:
            try:
                data = json_config_content[user_recipe_build]
                recipe = CheckConfigPydantic.BaseRecipe(**data)
                return recipe
            except ValidationError as e:
                logger.warning(f"Erreur de validation: {e}")
            except Exception as e:
                logger.warning(f"Une erreur s'est produite: {e}")
        else:
            try:
                data = json_config_content[recipe_type_start]
                # ['genepy', 'calibre_rulers', 'csv', 'json']
                if recipe_type_start == "genepy" or recipe_type_start == "calibre_rulers":
                    recipe = CheckConfigPydantic.GenepyCalibreRulers(**data)
                elif recipe_type_start == "opcfield":
                    recipe = CheckConfigPydantic.OPCfield(**data)
                # TODO make validator for csv and json recipes
                else:
                    logger.warning(f"ValueError: Unknown recipe type: {recipe_type_start}")
                    raise ValueError(f"Unknown recipe type: {recipe_type_start}")
                return recipe
            except ValidationError as e:
                print("Erreur de validation:", e)
            except Exception as e:
                print("Une erreur s'est produite:", e)
