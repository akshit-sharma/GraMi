import argparse
from pathlib import Path

from readTimingFile import parseFile
from utils import bcolors

def commandParser():
    commands = argparse.ArgumentParser()
    commands.add_argument('--input-file', help='Input file', type=Path, required=True)
    commands.add_argument('--level', help='Level of the pattern graph', type=int, default=0)
    commands.add_argument('--verbose', help='Verbose output', action='store_true')
    commands.add_argument('--vv', help='Very verbose output', action='store_true')
    commands.add_argument('--vvv', help='Very verbose output', action='store_true')

    assert(commands.parse_args().input_file.exists())

    return commands.parse_args()

def printGraphsLevel(patternGraphs, patternSearched, level, support, v, vv):
    found = len(patternGraphs[level])
    searched = len(patternSearched[level])
    print(f"Level {level} : {found}/{searched}")
    if (v and found > 0) or vv:
        for (graph, freq) in patternSearched[level]:
            terminalColor = None
            if freq == 0:
                terminalColor = bcolors.FAIL
            elif freq >= support:
                terminalColor = bcolors.OKGREEN
            else:
                terminalColor = bcolors.WARNING
            if terminalColor != bcolors.WARNING:
                print(f"{terminalColor} {graph} {bcolors.ENDC}")
            else:
                print(f"{terminalColor} {graph}  {freq}/{support} {bcolors.ENDC}")

def main():
    arg = commandParser()
    data = parseFile(arg.input_file, arg.vvv)
    dataGraph, support, approxA, approxB, timeTaken, patternSearched, patternGraphs, finished = data['datagraph'], data['support'], data['approxA'], data['approxB'], data['timeTaken'], data['patternSearched'], data['patternGraphs'], data['finished']
    if arg.verbose:
        print(f"support is {support}")
    support = int(support)
    if arg.level == 0:
        for key in patternGraphs.keys():
            printGraphsLevel(patternGraphs, patternSearched, key, support, arg.verbose, arg.vv)
    else:
        printGraphsLevel(patternGraphs, patternSearched, arg.level, support, arg.verbose, arg.vv)

if __name__ == '__main__':
    main()
