import argparse
import math
from pathlib import Path

import pandas as pd
from readTimingFile import parseFile
from utils import maxLevel, numInstances


def commandParser():
    commands = argparse.ArgumentParser()
    commands.add_argument('--latex-dir', type=Path, default=Path('./artifacts/latex'), help = 'Latex directory')
    commands.add_argument('--json-dir', type=Path, default=Path('./artifacts/json'), help = 'Json directory')
    commands.add_argument('--csv-dir', type=Path, default=Path('./artifacts/csv'), help = 'csv directory')
    commands.add_argument('--subfolder', type=Path, default=Path('individuals'), help = 'subdirectory for individual runs')
    commands.add_argument('--timings-data', type=Path, default=Path('./timings'), help = 'directory for timings data')
    commands.add_argument('--consolidated-name', type=str, default='gramiTime', help = 'name of consolidated file')
    commands.add_argument('--verbose', help='Verbose output', action='store_true')
    commands.add_argument('--vvv', help='Very verbose output', action='store_true')

    return commands.parse_args()

def writeBuffer(file, buffer):
    with open(file, 'w') as f:
        f.write(buffer)
        f.write('\n')

def main(args):
    directory = args.timings_data
    latex_subdir = args.latex_dir / args.subfolder
    json_subdir = args.json_dir / args.subfolder
    csv_subdir = args.csv_dir / args.subfolder
    latex_subdir.mkdir(parents=True, exist_ok=True)
    json_subdir.mkdir(parents=True, exist_ok=True)
    csv_subdir.mkdir(parents=True, exist_ok=True)


    consolidatedResults = []

    for file in directory.glob('*.time'):
        if 'clique' in file.name or 'test' in file.name:
            continue
        if args.verbose:
            print(f'processing {file}')
        data = parseFile(file, args.vvv)
        datagraph, support, approxA, approxB, timeTaken, _ = data['datagraph'], data['support'], data['approxA'], data['approxB'], data['timeTaken'], data['finished']
        filename = f"{datagraph}-{support}-{approxA}-grami-{approxB}"
        if timeTaken != 0 or timeTaken != math.inf:
            patternsSearched, patternsFreq = data['patternSearched'], data['patternGraphs']
            searched = numInstances(patternsSearched)
            found = numInstances(patternsFreq)
            maxLevelFound = maxLevel(patternsFreq)
            maxLevelSearched = maxLevel(patternsSearched)

            # Storing results in a data frame
            patternList = []
            for key in patternsSearched.keys():
                patternList.append((key, len(patternsFreq[key]), len(patternsSearched[key])))
            df = pd.DataFrame(patternList, columns=['num of nodes', 'found', 'searched'])
            writeBuffer(latex_subdir / f"{filename}.tex", df.to_latex(index=False))
            writeBuffer(json_subdir / f"{filename}.json", df.to_json(orient='table', index=True))
            writeBuffer(csv_subdir / f"{filename}.csv", df.to_csv(index=False))

        elif timeTaken == 0:
            found, searched, maxLevelSearched, maxLevelFound = 0, 0, 0, 0
        else:
            found, maxLevelFound = 0, 0
            searched, maxLevelSearched = float('inf'), float('inf')

        consolidatedResults.append([datagraph, support, approxA, maxLevelSearched, searched, found, maxLevelFound, timeTaken])
    df = pd.DataFrame(consolidatedResults, columns=['datagraph', 'support', 'approxA', 'Max Level Searched', 'Searched', 'Found', 'Max Level Freq', 'timeTaken (s)'])
    df = df.sort_values(by=['datagraph', 'support', 'approxA'], ascending=[True, False, False])

    writeBuffer(args.latex_dir / f"{args.consolidated_name}.tex", df.to_latex(index=False))
    writeBuffer(args.json_dir / f"{args.consolidated_name}.json", df.to_json(orient='table', index=True))
    writeBuffer(args.csv_dir / f"{args.consolidated_name}.csv", df.to_csv(index=False))


if __name__ == '__main__':
    arg = commandParser()
    main(arg)
