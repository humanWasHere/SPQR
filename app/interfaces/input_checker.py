from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator, DirectoryPath, FilePath

StepType = Literal["PH", "ET", "PH_HR", "ET_HR"]


class BaseRecipe(BaseModel):
    recipe_name: Optional[str] = None
    output_dir: Optional[DirectoryPath] = Path.cwd()
    layout: FilePath
    layers: list[str] = Field(min_length=1)
    step: StepType | list[StepType] = Field(min_length=1)
    magnification: int = Field(gt=0)
    polarity: Optional[Literal['clear', 'dark']] = 'clear'
    ap1_mag: Optional[int] = Field(None, gt=0)
    ap1_offset: Optional[list[float]] = Field(None, min_length=2, max_length=2)
    ap1_template: Optional[str] = ''
    ep_template: Optional[str] = ''
    eps_template: Optional[str] = ''
    mp_template: Optional[str | dict[str, str]] = ''
    offset: Optional[dict[str, float]] = None

    @field_validator('ap1_mag', 'ap1_offset', mode='before')
    def convert_empty_str(value):
        """Interpret empty string as None for optional fields that are NOT str type"""
        return None if value == '' else value


class OPCField(BaseRecipe):
    coord_file: Optional[str] = ''
    origin_x_y: list[float] = Field(min_length=2, max_length=2)
    step_x_y: list[float] = Field(min_length=2, max_length=2)
    n_cols_rows: list[int] = Field(min_length=2, max_length=2)


class CoordFile(BaseRecipe):
    coord_file: FilePath


def get_config_checker(config_recipe: dict) -> BaseModel:
    """Determine the recipe kind and return the corresponding validated model"""
    if 'coord_file' in config_recipe and config_recipe['coord_file']:
        return CoordFile(**config_recipe)
    if {'origin_x_y', 'step_x_y', 'n_cols_rows'}.issubset(config_recipe):
        return OPCField(**config_recipe)
    raise ValueError("Please provide either a 'coord_file' path or OPCfield parameters")
