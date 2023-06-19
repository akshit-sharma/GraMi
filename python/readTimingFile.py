from patternGraph import parsePatternGraph
import math

def coroutine(file):
    with open(file, 'r') as f:
        for line in f:
            yield line
    return None

def metaFileParser(fileCoro):
    def timeTaken(line):
        if line.strip() == "Time's up!":
            return math.inf
        second = line.split()[1].strip()
        if second == "Label:":
            return math.inf
        return float(second)
    support = next(fileCoro).split()[1]
    approxA = next(fileCoro).split()[1]
    approxB = next(fileCoro).split()[1]
    if fileCoro == None:
        return support, approxA, approxB, math.inf
    try:
        timeTakenVar = timeTaken(next(fileCoro))
    except StopIteration:
        timeTakenVar = 0
    return support, approxA, approxB, timeTakenVar

def getPatternGraphs(fileCoro, support):
    # map of pattern graphs with key as num of nodes of pattern graph
    patternGraphsZero = {}
    patternGraphs = {}
    # pattern startigns with [-]+Looking into frequency of: [v] [[:num:]]+ [[:num:]]+
    # and ends with new line
    pattern = None
    isDone = False
    for line in fileCoro:
        if len(line) == 0:
            break
        lineSplit = line.strip().split()
        if not (line[0] == '-' or (len(lineSplit) > 0 and lineSplit[0] == 'Freq:') or (len(lineSplit) > 0 and lineSplit[0] == 'Done')):
            continue
        if line[0] == '-':
            pattern = parsePatternGraph(fileCoro, line)
            if pattern.size() not in patternGraphs:
                patternGraphs[pattern.size()] = []
            if pattern.size() not in patternGraphsZero:
                patternGraphsZero[pattern.size()] = []
        if lineSplit[0] == 'Freq:':
            if pattern == None:
                freq = 0
            else:
                freq = int(lineSplit[1])
                if freq >= support:
                    patternGraphs[pattern.size()].append((pattern, freq))
                patternGraphsZero[pattern.size()].append((pattern, freq))
            pattern = None
        if lineSplit[0] == "Done":
            isDone = True
            break
    return patternGraphsZero, patternGraphs, isDone

def parseFile(file, vvv):
    if (vvv):
        print("processing file {}".format(file))
    fileCoro = coroutine(file)
    support, approxA, approxB, timeTaken = metaFileParser(fileCoro)
    # assert freq, approxA, approxB, timeTaken are same as file name
    filename = file.stem
    # remove .time suffix from file, might have more . in the name
    # from 0 to -4 is the datagraph name
    datagraph = '-'.join(filename.split('-')[0:-4])
    assert type(support) == str
    assert support == filename.split('-')[-4], "support: ({}) filename: ({})".format(support, filename.split('-')[-4])
    assert approxA == filename.split('-')[-3], "approxA: {} filename: {}".format(approxA, filename.split('-')[-3])
    assert "grami" == filename.split('-')[-2], "grami filename: {}".format(filename.split('-')[-2])
    assert approxB == filename.split('-')[-1], "approxB: {} filename: {}".format(approxB, filename.split('-')[-1])
    if timeTaken == 0:
        return {'datagraph': datagraph, 'support' : support, 'approxA': approxA, 'approxB': approxB, 'timeTaken': timeTaken, 'patternSearched': {}, 'patternGraphs': {}, 'finished': False}

    patternSearched, patternGraphs, finished = getPatternGraphs(fileCoro, int(support))
    return {'datagraph': datagraph, 'support' : support, 'approxA': approxA, 'approxB': approxB, 'timeTaken': timeTaken, 'patternSearched': patternSearched, 'patternGraphs': patternGraphs, 'finished': finished}
