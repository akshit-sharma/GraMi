#!/bin/python3
#

import argparse
from pathlib import Path
import json
import re

def commandsParser():
    commands = argparse.ArgumentParser()
    commands.add_argument('--json-dir', type=Path, default='./artifacts/json/', help='Json directory')
    commands.add_argument('--table-schema', type=Path, default='./artifacts/tanstackv8/schema/')
    commands.add_argument('--table-data', type=Path, default='./artifacts/tanstackv8/data/')
    commands.add_argument('--verbose', action='store_true', help='Verbose')
    return commands.parse_args()

def writeBuffer(file, buffer):
    with open(file, 'w') as f:
        f.write(buffer)
        f.write('\n')

def readJsonFile(file):
    with open(file,'r') as f:
        return json.load(f)

def replace_keys(json_data):
    replace_map = {
            '#': 'num',
            'w/o': 'without',
            '\(': '', # type: ignore
            '\)': '', # type: ignore
            '\s': '_', # type: ignore
            }
    def replace(string):
        assert isinstance(string, str)
        new_string = string
        for (k, v) in replace_map.items():
            new_string = re.sub(k, v, new_string)
        return new_string

    if isinstance(json_data, dict):
        new_dict = {}
        for key, value in json_data.items():
            new_key = replace(key)

            if isinstance(value, str):
                new_val = replace(value)
            else:
                new_val = value

            if new_key != key:
                new_dict['original_key'] = key
            if new_val != value:
                new_dict['original_value'] = value
            new_dict[new_key] = new_val

        return new_dict
    elif isinstance(json_data, list):
        return [replace_keys(item) for item in json_data]
    else:
        return json_data

def typescriptType(fields):
    def typ(value):
        if value == "string" or value == 'number':
            return value
        if value == "integer":
            return "number"
        raise RuntimeError(f"Unknown type {value}")

    buffer = ""
    for field in fields:
        buffer += f"  {field['name']}: {typ(field['type'])}\n"
    return buffer

def columnAccessors(fields):
    def origName(field):
        # if original_value is there, then return it else name
        return field.get('original_value', field['name'])
    def innerAccessors(field):
        buf = ""
        if field['name'] == 'index':
            buf += f"    id: '{field['name']}',\n"
        buf += f"    header: () => <span>{origName(field)}</span>,\n"
        buf += f"    cell: info => info.getValue(),\n    footer: info => info.column.id,\n"
        return buf
    buffer = ""
    for field in fields:
        buffer += "  columnHelper.accessor('"+field['name']+"', {\n"
        buffer += innerAccessors(field)
        buffer += "  }),\n"
    return buffer

def processSchema(file, schema):
    processedSchema = replace_keys(schema)
    buffer = "import { createColumnHelper } from '@tanstack/react-table'\n\n"
    buffer += "export type ColumnType = {\n"
    buffer += typescriptType(processedSchema)
    buffer += "}\n\n"
    buffer += "const columnHelper = createColumnHelper<ColumnType>()\n\n"
    buffer += "export const defaultColumns = [\n"
    buffer += columnAccessors(processedSchema)
    buffer += "]\n\n"
    writeBuffer(file, buffer)


def processRows(file, rows):
    processedRows = replace_keys(rows)
    buffer = json.dumps(processedRows, indent=2)
    writeBuffer(file, buffer)

def processDirectory(dir, schema_dir, rows_dir):
    schema_dir.mkdir(parents=True, exist_ok=True)
    rows_dir.mkdir(parents=True, exist_ok=True)
    for file in dir.iterdir():
        if file.is_dir():
            processDirectory(file, schema_dir / file.name, rows_dir / file.name)
            continue

        assert(file.is_file())
        data = readJsonFile(file)
        schema = data['schema']['fields']
        rows = data['data']
        schema_filename = file.with_suffix('.tsx').name
        rows_filename = file.name
        processSchema(schema_dir / schema_filename, schema)
        processRows(rows_dir / rows_filename, rows)




def main(args):
    processDirectory(args.json_dir, args.table_schema, args.table_data)

if __name__ == '__main__':
    args = commandsParser()
    main(args)
