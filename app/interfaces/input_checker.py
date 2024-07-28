from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, field_validator  # model_validator, ValidationError

StepType = Literal["PH", "ET", "PH_HR", "ET_HR"]


def validate_path(value: Path) -> Path:
    if not value.exists():
        raise ValueError(f"Path does not exist: {value}")
    return value


class BaseRecipe(BaseModel):
    recipe_name: Optional[str] = None
    output_dir: Optional[Path] = Path.cwd()
    layout: Path
    layers: list[str]
    step: StepType | list[StepType]
    magnification: int
    ap1_mag: Optional[int] = None
    ap1_offset: Optional[list[float]] = None
    ap1_template: Optional[str] = ''
    ep_template: Optional[str] = ''
    eps_template: Optional[str] = ''
    mp_template: Optional[str | dict[str, str]] = ''

    @field_validator('ap1_mag', 'ap1_offset', mode='before')
    def convert_empty_str(value):
        """Interpret empty string as None for optional fields that are NOT str type"""
        return None if value == '' else value

    @field_validator('layout', 'output_dir')
    def validate_paths(cls, value):
        return validate_path(value)


class OPCField(BaseRecipe):
    parser: Optional[str] = ''
    origin_x_y: list[float]
    step_x_y: list[float]
    n_rows_cols: list[int]


class CoordFile(BaseRecipe):
    parser: Path

    @field_validator('parser')
    def validate_parser(cls, value):
        return validate_path(value)


def get_config_checker(config_recipe: dict) -> BaseModel:
    """Determine the recipe kind and return the corresponding validated model"""
    if 'parser' in config_recipe and config_recipe['parser']:
        return CoordFile(**config_recipe)
    if {'origin_x_y', 'step_x_y', 'n_rows_cols'}.issubset(config_recipe):
        return OPCField(**config_recipe)
    raise ValueError("Please provide either a 'parser' file path or OPCfield parameters")
