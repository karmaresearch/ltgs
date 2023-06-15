
import glog
import os
from os import listdir
from os.path import isfile, join
import datetime
from utilities import computeLineage, computeProbability
    
loglevel = 0 # INFO level
chaseProcedure = "probtgchase" # If you want to use the standard chase, use "tgchase"
typeProv = "FULLPROV"

for scenario in ['yago5_1', 'yago5_2', 'yago5_3', 'yago5_4']:
    
    main_dir = 'data/TGs/yago/yago5' + scenario
    os.chdir(main_dir)
    #Change the main_dir to 'data/TGs/yago/yago10' and the scenarios to 'yago10_1', 'yago10_2' for running experiments on yago10.
    #yago15 does not include subfolders, so we only need to change the main_dir to 'data/TGs/yago/yago15'
    
    if not os.path.exists('answers/'):
        os.makedirs('answers/')

    for rule in [file for file in listdir(join(main_dir)) if isfile(join(main_dir, file)) and ".dlog" in file]:
        print(main_dir)
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
