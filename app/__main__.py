import argparse
import logging
import os
import shutil
from pathlib import Path

from .interfaces.logger import logger_init  # import first
from .interfaces.cli import cli, check_recipe, parse_intervals
from .interfaces.input_checker import get_config_checker
from .interfaces.tracker import global_data_tracker
# log_metrics()


def build_mode(args: argparse.Namespace) -> None:
    """Main function that manages the build CLI arguments."""
    logging.info('SPQR running in production mode')
    from .parsers.json_parser import import_json  # lazy import because pandas is slow

    if not args.config.exists() or not args.config.is_file():
        raise ValueError(f'Path does not exist or is not a file: {args.config}')
    if args.config.stat().st_size == 0:
        raise ValueError(f'File is empty: {args.config}')
    user_config = import_json(args.config)

    # Recipe selection
    build_config = check_recipe(user_config, args.recipe)
    build_model = get_config_checker(build_config)
    logging.debug(repr(build_model))
    build_config = build_model.model_dump()

    line_select = parse_intervals(args.line_select)

    if isinstance(build_config['step'], list):
        steps = build_config['step']
        for part, step in enumerate(steps):
            logging.info(f"creating recipe {build_config['recipe_name']} "
                         f"{part+1}/{len(steps)}: {step} from {steps}")
            copied_config = build_config.copy()
            copied_config['step'] = step
            copied_config['recipe_name'] = str(f"{build_config['recipe_name']}_{step}")
            create_recipe(copied_config, args.upload_rcpd, line_select, args.measure)
    else:
        create_recipe(build_config, args.upload_rcpd, line_select, args.measure)


def test_mode(args: argparse.Namespace) -> None:
    """Main function that manages the test CLI arguments."""
    logging.info('SPQR running in dev mode')
    from .parsers.json_parser import import_json  # pandas is slow

    app_config_file = Path(__file__).resolve().parents[1] / "assets" / "app_config.json"
    app_config = import_json(app_config_file)
    if not app_config:
        raise ValueError(f"File {app_config_file.name} does not exist or is empty.")

    if args.recipe:
        test_env_config = app_config[args.recipe]
        test_env_config = get_config_checker(test_env_config).model_dump()
        if args.recipe == "calibre_rulers":
            create_recipe(test_env_config, line_select=[[10, 20]])
        else:
            create_recipe(test_env_config, line_select=[[100, 110]])
    elif args.all_recipes:
        for recipe_name in app_config:
            logging.info(f"running {recipe_name} recipe")
            recipe_config = get_config_checker(app_config[recipe_name]).model_dump()
            if recipe_name == "calibre_rulers":
                create_recipe(recipe_config, line_select=[[10, 20]])
            else:
                create_recipe(recipe_config, line_select=[[100, 110]])
    # Draft auto mode (override args and use build)
    # build_mode(cli().parse_args(
    #     ['build', '-c', str(app_config_file), '-r', 'calibre_rulers', '-l', '10-20']))


def upload_mode(args: argparse.Namespace) -> None:
    """Main function that manages the upload mode of the CLI arguments."""
    from .interfaces import recipedirector as rcpd
    logging.info('SPQR running upload mode')
    if args.recipe:
        rcpd.upload_csv(args.recipe)
        logging.info(f'Recipe {args.recipe} should be on RCPD machine!')
    elif args.layout:
        rcpd.upload_gds(args.layout)
        logging.info(f'Layout {args.layout} should be on RCPD machine!')
    else:
        logging.error("Upload mode failure. Not a known command !")


def edit_mode(args: argparse.Namespace) -> None:
    """Main function that modifies a recipe from the terminal."""
    from .export_hitachi.hss_editor import RecipeEditor
    from .parsers.json_parser import import_json
    logging.info('SPQR running edit mode')
    if args.recipe_file:
        assert Path(args.recipe_file).is_file(), f"Specified -r {args.recipe_file} is not a file."
    if args.config_file:
        assert Path(args.config_file).is_file(), f"Specified -c {args.config_file} is not a file."
    assert str(args.recipe_name) in import_json(args.config_file), \
        "Recipe name does not exist or is not in user configuration file."

    if args.recipe_file and args.config_file and args.recipe_name:
        recipe_editor_instance = RecipeEditor(recipe=Path(args.recipe_file),
                                              json_conf=import_json(args.config_file),
                                              recipe_name_conf=str(args.recipe_name))
        result = recipe_editor_instance.run_recipe_edit()
        return result


def init_mode(args: argparse.Namespace) -> None:
    """Main function that manages the init CLI arguments."""
    def init_function(output: Path, file_type: str) -> None:
        dict_info_condition = {
            "configuration": {
                "default_example_file_name": "user_config_ex.json",
                "default_file_name": "default_config.json",
                "extension": ".json"
            },
            "coordinate": {
                "default_example_file_name": "coordinate_file_ex.txt",
                "default_file_name": "default_coord_file.txt",
                "extension": ".txt"
            }
        }

        argument_info = dict_info_condition[file_type]

        if output.is_dir():
            output = output / argument_info["default_file_name"]
        output = output.with_suffix(argument_info["extension"])
        ex_user_config = (
            Path(__file__).resolve().parents[1] / "assets" / "init"
            / argument_info["default_example_file_name"])
        shutil.copy(ex_user_config, output)
        return output.resolve()

    logging.info('SPQR running init mode.')

    if not (args.coordinate_file or args.config_file):
        default_path = Path.cwd() / "spqr_init"
        default_path.mkdir(parents=True, exist_ok=True)
        args.coordinate_file = default_path
        args.config_file = default_path
    if args.config_file:
        file_path_one = init_function(args.config_file, "configuration")
        logging.info(f'Configuration file initialized at {file_path_one}')
    if args.coordinate_file:
        file_path_two = init_function(args.coordinate_file, "coordinate")
        logging.info(f'Coordinate file initialized at {file_path_two}')


def manage_app_launch(argv=None):
    """Read the command line and user config.json and launch the corresponding command"""
    # TODO if several dict -> several recipe -> run several recipes
    logger = logger_init()
    args = cli().parse_args(argv)

    try:
        # running tracking in create_recipe for test/build modes
        match args.running_mode:
            case 'init':
                global_data_tracker(parser=None, cli_args=args)
                init_mode(args)
            case 'edit':
                global_data_tracker(parser=None, cli_args=args)
                edit_mode(args)
            case 'upload':
                global_data_tracker(parser=None, cli_args=args)
                upload_mode(args)
            case 'test':
                test_mode(args)
            case 'build':
                build_mode(args)

    except KeyboardInterrupt:
        logging.error('Interrupted by user')
    except Exception as e:
        logger.removeHandler(logger.console_handler)  # to avoid double printing with the raise
        logging.exception(f'{e.__class__.__name__}')
        raise

    return 0


def create_recipe(json_conf: dict, upload=False, line_select=None, output_measurement=False):
    """this is the real main function which runs the flow with the measure - "prod" function"""
    # lazy import for perf issue
    os.environ['ENV_TYPE'] = "PRODUCTION"  # workaround for MAPICore.runtime.Environment

    from .data_structure import Block
    from .interfaces import recipedirector as rcpd
    from .export_hitachi.hss_creator import HssCreator
    from .measure.measure import Measure
    from .parsers import FileParser, get_parser, OPCFieldReverse
    block = Block(json_conf['layout'])

    logging.info(f"### CREATING RECIPE ### : {json_conf['recipe_name']}")
    # Parser selection
    parser = get_parser(json_conf['coord_file'])
    global_data_tracker(parser=parser.__name__, cli_args=cli().parse_args())

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
                               json_conf.get('offset'), row_range=line_select)
    output_measure = measure_instance.run_measure(
        output_dir=json_conf['output_dir'] if output_measurement else None,
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
