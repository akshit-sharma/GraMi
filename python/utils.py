
def numInstances(patternGraphs):
    num = 0
    for key in patternGraphs.keys():
        num += len(patternGraphs[key])
    return num

def maxLevel(patternGraphs):
    maxLevel = 0
    for key in patternGraphs.keys():
        maxLevel = max(maxLevel, key)
    return maxLevel

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

