import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import yaml
from yaml.resolver import BaseResolver


def read_file(filepath: Union[str, Path]) -> Tuple[Any, str]:
    filepath = Path(filepath)
    ext = filepath.suffix
    if ext == ".json":
        return read_json(filepath), ".json"
    elif ext in [".jsonl", ".jl"]:
        return read_jsonl(filepath), ".jsonl"
    elif ext == ".txt":
        return read_txt(filepath), ".txt"
    elif ext == ".tsv":
        return read_tsv(filepath), ".tsv"
    else:
        raise TypeError(f"Given filetype ({filepath}) is not supported!")


def read_json(filepath: Union[str, Path]) -> Dict[Any, Any]:
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def read_jsonl(filepath: Union[str, Path]) -> List[Dict[Any, Any]]:
    if not os.path.exists(filepath):
        return []

    json_lines = []
    with open(filepath, encoding="utf-8") as f:
        file_lines = f.read().strip().rsplit("\n")
        for line in file_lines:
            json_lines.append(json.loads(line))
    return json_lines


def read_yaml(filepath: Union[str, Path]) -> Dict[Any, Any]:
    with open(filepath, encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_txt(filepath: Union[str, Path]) -> List[str]:
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read().rstrip().split("\n")


def read_tsv(filepath: Union[str, Path]) -> List[Dict[Any, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return [row for row in reader]


def read_csv(filepath: Union[str, Path]) -> List[Dict[Any, Any]]:
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def input_file_validator(valid_extensions: Union[Tuple[str, str, str], Tuple[str]]) -> Any:
    def extension(filename: Union[str, Path]) -> Union[str, Path]:
        if not str(filename).lower().endswith(valid_extensions):
            raise argparse.ArgumentTypeError("Not a valid filename extension")
        return filename

    return extension


def valid_filetype(arg_input_file: Union[str, Path]) -> Union[str, Path]:
    ext = Path(arg_input_file).suffix
    if ext in [".txt", ".jsonl", ".jl"]:
        return arg_input_file
    else:
        msg = f"Given filetype ({arg_input_file}) is not valid! Expected filetype: .txt / .jsonl / .jl"
        raise argparse.ArgumentTypeError(msg)


def write_jsonl(data: List[Dict[Any, Any]], filepath: Union[str, Path]):
    with open(filepath, "w", encoding="utf-8") as f:
        for datum in data:
            f.write(json.dumps(datum, ensure_ascii=False) + "\n")

def write_json(data: Union[Dict[Any, Any], List[Dict[Any, Any]]], filepath: Union[str, Path]):
    dirname = Path(filepath).absolute().parent
    create_dir(dirname)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def write_tsv(data: List[Dict[Any, Any]], filepath: Union[str, Path]):
    if not data:
        return
    dirname = Path(filepath).absolute().parent
    create_dir(dirname)
    with open(filepath, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys(), delimiter="\t")
        writer.writeheader()
        writer.writerows(data)


def write_csv(data: List[Dict[Any, Any]], filepath: Union[str, Path]):
    if not data:
        return
    dirname = Path(filepath).absolute().parent
    create_dir(dirname)
    with open(filepath, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def append_jsonl(data: Union[Dict[Any, Any], List[Dict[Any, Any]]], filepath: Union[str, Path]):
    dirname = Path(filepath).absolute().parent
    create_dir(dirname)

    if isinstance(data, dict):
        data = [data]

    with open(filepath, "a", encoding="utf-8") as f:
        for datum in data:
            f.write(json.dumps(datum, ensure_ascii=False) + "\n")


def write_yaml(data: Dict[Any, Any], filepath: Union[str, Path]):
    dirname = Path(filepath).absolute().parent
    create_dir(dirname)
    with open(filepath, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True)


def create_dir(dirname: Path):
    if not dirname.exists():
        dirname.mkdir(parents=True)
