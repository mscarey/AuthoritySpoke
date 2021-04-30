import json
from pathlib import Path

import yaml


def convert_json_file_to_yaml(filepath: Path):
    with open(filepath, "r") as f:
        holdings = json.load(f)
    new_name = filepath.stem + ".yaml"
    new_path = filepath.parent / new_name
    with open(new_path, "w") as wf:
        yaml.safe_dump(
            holdings, wf, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def make_yaml_holding_files():
    holding_directory = Path.cwd() / "holdings"
    for holding_file in holding_directory.iterdir():
        if holding_file.suffix == ".json":
            convert_json_file_to_yaml(holding_file)


if __name__ == "__main__":
    make_yaml_holding_files()
