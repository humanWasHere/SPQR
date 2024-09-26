import argparse
import logging
import os
import sys
from pathlib import Path

from .parsers.json_parser import import_json

from .interfaces.logger import logger_init  # import first
from .interfaces.cli import check_recipe, parse_intervals, cli
# log_metrics()


def build_mode(args: argparse.Namespace) -> None:
    """Main function that manages the build CLI arguments."""
    logging.info('SPQR running in production mode')
    from .parsers.json_parser import import_json  # pandas is slow
    from .interfaces.input_checker import get_config_checker

    if not args.user_config.exists() or not args.user_config.is_file():
        raise ValueError(f'Path does not exist or is not a file: {args.user_config}')
    if args.user_config.stat().st_size == 0:
        raise ValueError(f'File is empty: {args.user_config}')

    # TODO validate whole JSON
    user_config = import_json(args.user_config)

    # Recipe selection
    build_config = check_recipe(user_config, args.user_recipe)
    build_model = get_config_checker(build_config)
    logging.debug(repr(build_model))
    build_config = build_model.model_dump()

    if isinstance(build_config['step'], list):
        steps = build_config['step']
        for part, step in enumerate(steps):
            logging.info(f"creating recipe {build_config['recipe_name']} "
                         f"{part+1}/{len(steps)}: {step} from {steps}")
            copied_config = build_config.copy()
            copied_config['step'] = step
            copied_config['recipe_name'] = str(f"{build_config['recipe_name']}_{step}")
            create_recipe(copied_config, args.upload_rcpd, parse_intervals(args.line_selection), args.mesurement_file)
    else:
        create_recipe(build_config, args.upload_rcpd, parse_intervals(args.line_selection), args.mesurement_file)


def test_mode(args: argparse.Namespace) -> None:
    """Main function that manages the test CLI arguments."""
    logging.info('SPQR running in dev mode')
    from .parsers.json_parser import import_json  # pandas is slow
    from .interfaces.input_checker import get_config_checker

    app_config_file = Path(__file__).resolve().parents[1] / "assets" / "app_config.json"
    app_config = import_json(app_config_file)
    if not app_config:
        raise ValueError(f"File {app_config_file.name} does not exist or is empty.")

    if args.recipe:
        test_env_config = app_config[args.recipe]
        test_env_config = get_config_checker(test_env_config).model_dump()
        if args.recipe == "calibre_rulers":
            create_recipe(test_env_config, line_selection=[[10, 20]])
        else:
            create_recipe(test_env_config, line_selection=[[100, 110]])
    elif args.all_recipes:
        for recipe_name in app_config:
            logging.info(f"running {recipe_name} recipe")
            recipe_config = get_config_checker(app_config[recipe_name]).model_dump()
            if recipe_name == "calibre_rulers":
                create_recipe(recipe_config, line_selection=[[10, 20]])
            else:
                create_recipe(recipe_config, line_selection=[[100, 110]])
    # TODO for loop to run all test dev recipes with arg -a
    # Draft auto mode (override args and use build)
    # build_mode(cli().parse_args(
    #     ['build', 'c', str(app_config_file), 'r', 'calibre_rulers', 'l', '10-20']))


def upload_mode(args: argparse.Namespace) -> None:
    """Main function that manages the upload mode of the CLI arguments."""
    from .interfaces import recipedirector as rcpd
    logging.info('SPQR running upload mode')
    if args.user_recipe:
        rcpd.upload_csv(args.user_recipe)
        logging.info(f'Recipe {args.user_recipe} should be on RCPD machine!')
    elif args.user_layout:
        rcpd.upload_gds(args.user_layout)
        logging.info(f'Layout {args.user_layout} should be on RCPD machine!')
    else:
        logging.error("Upload mode failure. Not a known command !")


def modification_mode(args: argparse.Namespace) -> None:
    """Main function that modificates a recipe with CLI arguments."""
    from .export_hitachi.hss_editor import RecipeModificator
    logging.info('SPQR running modification mode')
    if args.recipe_to_modify_path:
        assert Path(args.recipe_to_modify_path).is_file(), logging.error("Specified -r file is not a file or a directory")
    if args.user_configuration_path:
        assert Path(args.user_configuration_path).is_file(), logging.error("Specified -c file is not a file or a directory")
    assert str(args.recipe_name) in import_json(args.user_configuration_path), logging.error("recipe name doesn't exists or is not in user configuration file.")
    if args.recipe_to_modify_path and args.user_configuration_path and args.recipe_name:
        recipe_modificator_instance = RecipeModificator(recipe=Path(args.recipe_to_modify_path),
                                                        json_conf=import_json(args.user_configuration_path),
                                                        recipe_name_conf=str(args.recipe_name))
        result = recipe_modificator_instance.run_recipe_modification()
        return result


def init_mode(args: argparse.Namespace) -> None:
    """Main function that manages the init CLI arguments."""
    if args.config_file:
        logging.info('SPQR running init mode (user configuration example in json).')
        if args.config_file.is_dir():
            if not args.config_file.exists():
                raise ValueError(f'Path does not exist: {args.config_file}')
            args.config_file = args.config_file / "default_config.json"
        else:
            if args.config_file.suffix == ".txt":
                raise ValueError(f"File should be in .json format: {args.config_file}\nUse -t command to generate a default coordinate file in .txt")
            if args.config_file.suffix != ".json":
                raise ValueError(f'File should be in .json format: {args.config_file}')
        ex_user_config = Path(__file__).resolve().parents[1] / "assets" / "init" / "user_config_ex.json"
        ex_user_config_content = ex_user_config.read_text()
        Path(args.config_file).write_text(ex_user_config_content)
        logging.info(f'Configuration file initialized at {args.config_file}')
    elif args.coordinate_file:
        logging.info('SPQR running init mode (coordinate file example in txt).')
        if args.coordinate_file.is_dir():
            if not args.coordinate_file.exists():
                raise ValueError(f'Path does not exist: {args.coordinate_file}')
            args.coordinate_file = args.coordinate_file / "default_coord_file.txt"
        else:
            if args.coordinate_file.suffix != ".txt":
                raise ValueError(f'File should be in .txt format: {args.coordinate_file}')
            if args.coordinate_file.suffix == ".json":
                raise ValueError(f'File should be in .json format: {args.coordinate_file}')
        ex_user_config = Path(__file__).resolve().parents[1] / "assets" / "init" / "coordinate_file_ex.txt"
        ex_user_config_content = ex_user_config.read_text()
        args.coordinate_file.write_text(ex_user_config_content)
        logging.info(f'Configuration file initialized at {args.coordinate_file}')


def manage_app_launch():
    """Read the command line and user config.json and launches the corresponding command"""
    # TODO if several dict -> several recipe -> run several recipes
    # TODO make a checker of user_config.json before running the recipe
    logger_init()
    args = cli().parse_args()

    # Post process args
    if not args.running_mode:
        logging.warning("CLI app arguments should be executed as indicated in the helper below.")
        cli().print_help()
        sys.exit(1)
    # if args.line_selection is not None:
    #     args.line_selection = tuple(args.line_selection)
    try:
        if args.running_mode == 'init':
            init_mode(args)
        elif args.running_mode == 'modification':
            modification_mode(args)
        elif args.running_mode == 'upload':
            upload_mode(args)
        elif args.running_mode == 'test':
            test_mode(args)
        elif args.running_mode == 'build':
            build_mode(args)

    except KeyboardInterrupt:
        logging.error('Interrupted by user')
    except Exception as e:
        logging.exception(f'{e.__class__.__name__}')


def create_recipe(json_conf: dict, upload=False, line_selection=None, output_measurement=False):
    """this is the real main function which runs the flow with the measure - "prod" function"""
    # lazy import for perf issue
    os.environ['ENV_TYPE'] = "PRODUCTION"  # workaround for MAPICore.runtime.Environment

    from .data_structure import Block
    from .interfaces import recipedirector as rcpd
    from .interfaces.tracker import user_tracker, parser_tracker, cli_command_tracker, launched_recipe_tracker  # , monitor_spqr_errors  # , log_metrics
    from .export_hitachi.hss_creator import HssCreator
    from .measure.measure import Measure
    from .parsers import FileParser, get_parser, OPCFieldReverse
    block = Block(json_conf['layout'])

    logging.info(f"### CREATING RECIPE ### : {json_conf['recipe_name']}")
    # Parser selection
    parser = get_parser(json_conf['coord_file'])
    user_tracker()
    cli_command_tracker(sys.argv[1:])
    launched_recipe_tracker()
    parser_tracker(parser.__name__)
    # monitor_spqr_errors()
    if parser is None:
        raise ValueError("Your coordinate source may not be in a valid format")
    logging.info(f'parser is {parser.__name__}')
    selected_parser: FileParser | OPCFieldReverse
    if issubclass(parser, OPCFieldReverse):
        selected_parser = parser(
            json_conf['origin_x_y'][0], json_conf['origin_x_y'][1],
            json_conf['step_x_y'][0], json_conf['step_x_y'][1],
            json_conf['n_cols_rows'][0], json_conf['n_cols_rows'][1],
            json_conf['ap1_offset'][0], json_conf['ap1_offset'][1])
    else:
        selected_parser = parser(json_conf['coord_file'])

    # measurement
    measure_instance = Measure(selected_parser, block, json_conf['layers'],
                               json_conf.get('offset'), row_range=line_selection)
    output_measure = measure_instance.run_measure(output_dir=json_conf['output_dir'] if output_measurement else None,
                                                  recipe_name=json_conf['recipe_name'] if output_measurement else None)

    # temp fix here --> marc support
    if json_conf['ap1_offset']:
        output_measure['x_ap'] = int(json_conf['ap1_offset'][0] * 1000)
        output_measure['y_ap'] = int(json_conf['ap1_offset'][1] * 1000)

    # renaming of measure points  # TODO not here
    if isinstance(selected_parser, OPCFieldReverse):
        import numpy as np

        cd_space = (output_measure["polygon_tone"].str[:2]
                    + output_measure['min_dim'].astype(float).astype(int).astype(str))
        iso = output_measure['pitch_min_dim'] == output_measure['min_dim']
        pitch = np.where(iso, "ISO", 'P' + output_measure['pitch_min_dim']
                         .astype(float).astype(int).astype(str))
        output_measure.name = cd_space + '_' + pitch + '_' + output_measure.name.astype(str)

    # all recipe's sections creation
    runHssCreation = HssCreator(core_data=output_measure, block=block, json_conf=json_conf,
                                polarity=json_conf.get('polarity', 'clear').lower())
    recipe_path = runHssCreation.write_in_file()
    if upload:
        rcpd.upload_csv(recipe_path)
        rcpd.upload_gds(json_conf['layout'])
        # TODO if file already exists on remote, check if new file is changed
        logging.info(f"recipe named {json_conf['recipe_name']} should be on RCPD machine!")
    logging.info("### END RECIPE CREATION ###\n")


if __name__ == "__main__":
    manage_app_launch()
