
import glog
import os
from os import listdir
from os.path import isfile, join
import datetime
from utilities import computeAnswers
    
loglevel = 0 # INFO level
main_dir = 'data/TGs/dbpedia/'
os.chdir(main_dir)

if not os.path.exists('answers/'):
    os.makedirs('answers/')

chaseProcedure = "probtgchase" # If you want to use the standard chase, use "tgchase"
typeProv = "FULLPROV"

for rule in [file for file in listdir(join(main_dir)) if isfile(join(main_dir, file)) and ".dlog" in file]:
    print('Processing file {}\n'.format(rule))
    
    start = rule.rfind('-')
    end = rule.rfind('.')
    query = rule[start+1:end]
    edb_file = 'edb-{}.conf'.format(query)
    layer = glog.EDBLayer(edb_file)
    program = glog.Program(layer)
    program.load_from_file(rule)
    r = glog.Reasoner(chaseProcedure, layer, program, typeProv=typeProv, edbCheck=False, queryCont=False)
    tg = r.get_TG()
    stats = r.create_model(0)
    predicate = query
    querier = glog.Querier(tg)
    computeAnswers(querier, predicate) 
