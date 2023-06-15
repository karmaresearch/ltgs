
MAT_GLOG = r'["]runtime_ms["] : ["](\d*.\d*)["]'
MAT_VLOG = r'materialization: \{(\d*.\d*)\}'
PROB_GLOG = r'wmc_ms (\d*.\d*)'
PROB_VLOG = r'wmc: \{(\d*.\d*)\}'
STEPS_GLOG = r'["]steps["] : ["](\d*)["]'
DERIVATIONS_GLOG = r'["]n_derivations["] : ["](\d*)["]'
LEAVES_GLOG = r"leaves_ms (\d*.\d*)"

MEMORY_GLOG = r'["]max_mem_mb["] : ["](\d*.\d*)["]'
MEMORY_VLOG = r'memory: \{(\d*.\d*)\}'

QID_SCALLOP = r'QID: (\d*_\d*)'
TIME_SCALLOP = r'TIME: (\d*.\d*)'
OID_SCALLOP = r'OID: (\d\-)+|'

### SET FONT SIZES
SMALL_SIZE = 22
MEDIUM_SIZE = 22
BIGGER_SIZE = 28
EXTRA_BIGGER_SIZE = 30

import re 
import numpy as np 
from os import listdir
from os.path import isfile, join

def parseLTGsLogs(filename, expression):
    with open(filename) as fp:
        queries = list()
        results = list()
        while True:
            line = fp.readline()
            if not line:
                break
            query = line.split()[0][1:]
            queries.append(query)
            matchObj = re.search(expression, line)
            if matchObj:
                results.append(float(matchObj.group(1)))
    return (queries, np.array(results))
    
def parseLTGsQueries(inpath):
    queries_answers = dict()
    files = [file for file in listdir(inpath) if isfile(join(inpath, file))]
    for fname in files:
        end = fname.rfind('.probabilities')
        query = fname[1:end]
        answers_parsed = dict()
        with open(join(inpath,fname)) as infile:
            for line in infile:
                if not line:
                    break  
                line = line.replace('\n','')
                arguments = line.split(' ')
                oid = arguments[0]
                probability = float(arguments[1])
                answers_parsed[oid] = probability
            queries_answers[query] = answers_parsed
    return queries_answers
    
def parseScallopLogs(filename):
    with open(filename) as fp:
        queries = list()
        results = list()
        while True:
            line = fp.readline()
            if not line:
                break

            matchObj = re.search(QID_SCALLOP, line)
            if matchObj:
                queries.append(matchObj.group(1))
                
            matchObj = re.search(TIME_SCALLOP, line)
            if matchObj:
                results.append(float(matchObj.group(1)))
    return (queries, np.array(results))


def parseScallopLogsQueries(filename):
    with open(filename) as fp:
        queries_times = dict()
        queries_answers = dict()
        while True:
            line = fp.readline()
            if not line:
                break

            matchObj = re.search(QID_SCALLOP, line)
            query = matchObj.group(1)
            matchObj = re.search(TIME_SCALLOP, line)
            if matchObj:
                queries_times[query] = float(matchObj.group(1))
                
            answers_parsed = dict()
            occurences = [i for i, letter in enumerate(line) if letter == '|']
            for i in range(1, len(occurences)):
                previous = occurences[i-1]
                current = occurences[i]
                answer = line[previous+1:current]
                answer = answer.split()
                oid = answer[1]
                probability = float(answer[2])
                answers_parsed[oid] = probability
            queries_answers[query] = answers_parsed
               
    return (queries_times, queries_answers)
