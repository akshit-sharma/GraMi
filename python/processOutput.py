import argparse
from pathlib import Path
import pandas as pd

from tabulate import tabulate
from readTimingFile import parseFile
from utils import numInstances, maxLevel

def commandParser():
    commands = argparse.ArgumentParser()
    commands.add_argument('--input-dir', default='./timings/', help='Input folder', type=str, required=True)
    commands.add_argument('--output-file', default='./dumps/timing.pkl', help='Output file', type=str)
    commands.add_argument('--table-data-file', default='./dumps/table.txt', help='Output file', type=str)
    commands.add_argument('--verbose', help='Verbose output', action='store_true')
    commands.add_argument('--vvv', help='Very verbose output', action='store_true')

    return commands.parse_args()

def main(arg):
    directory = Path(arg.input_dir)
    execTimeList = []
    for file in directory.glob('*.time'):
        try:
            data = parseFile(file, arg.vvv)
            datagraph, support, approxA, approxB, timeTaken, patternSearched, patternGraphs, finished = data['datagraph'], data['support'], data['approxA'], data['approxB'], data['timeTaken'], data['patternSearched'], data['patternGraphs'], data['finished']
        except StopIteration as e:
            if arg.vvv:
                print(f"incomplete file {file}")
            continue
        if timeTaken == float('inf'):
            if arg.vvv:
                print("ignoring file {} as time was up".format(file))
            continue
        patternsList = []
        for key in patternSearched.keys():
            patternsList.append((key, len(patternGraphs[key]), len(patternSearched[key])))
        patterns = pd.DataFrame(patternsList, columns=['num of nodes', 'found', 'searched'])
        found = numInstances(patternGraphs)
        searched = numInstances(patternSearched)
        if searched == 0:
            if arg.vvv:
                print("ignoring file {} as no patterns were searched".format(file))
            continue
        if found == 0:
            if arg.vvv:
                print("ignoring file {} as no patterns were found".format(file))
            continue
        maxLevelFound = maxLevel(patternGraphs)
        maxLevelSearched = maxLevel(patternSearched)
        execTimeList.append((datagraph, support, approxA, approxB, timeTaken, found, searched, patterns, maxLevelFound, maxLevelSearched, finished))

    execTime = pd.DataFrame(execTimeList, columns=['datagraph', 'support', 'approxA', 'approxB', 'timeTaken (s)', 'found', 'searched', 'patterns', 'maxLevelFound', 'maxLevelSearched', 'finished'])
    execTime.to_pickle(arg.output_file)

    execTime = execTime.sort_values(by=['datagraph', 'support', 'approxA', 'approxB'], ascending=[True, False, False, False])

    trimTable = execTime[['datagraph', 'support', 'approxA', 'timeTaken (s)', 'found', 'searched', 'maxLevelFound', 'maxLevelSearched', 'finished']]
    def writeTable(file, df):
        with open(file, 'w') as f:
            f.write(df)
            f.write('\n')

    if arg.verbose:
        print(tabulate(trimTable, headers='keys', tablefmt='psql'))

    writeTable(arg.table_data_file, trimTable.to_string(index=False))

if __name__ == '__main__':
    arg = commandParser()
    main(arg)
