
import glog
import os
import datetime
from utilities import computeAnswers

loglevel = 2 # INFO level
main_dir = 'data/TGs/smokers/'
os.chdir(main_dir)
depth = 5
rules = 'rules_with_query.dlog'

if not os.path.exists('answers/'):
    os.makedirs('answers/')

for outer in range(10,21):
    for inner in [1,2,3,4,5,6,7,8,9,10]:
        print('Case: ' 'smokers-' + str(outer) + '-' + str(outer * 2) + '-' + str(inner) + '\n')
        edb_file = 'edb-' + str(outer) + '-' + str(outer * 2) + '-' + str(inner) + '.conf'
        a = glog.EDBLayer(edb_file)
        program = glog.Program(a)
        program.load_from_file(rules)
        print("N. rules", program.get_n_rules())
        
        chaseProcedure = "probtgchase" # If you want to use the standard chase, use "tgchase"
        typeProv = "FULLPROV"
        
        r = glog.Reasoner(chaseProcedure, a, program, typeProv=typeProv, edbCheck=False, queryCont=False)
        tg = r.get_TG()
        stats = r.create_model(0, depth)
            
        predicate = 'asthma'
    
        querier = glog.Querier(tg)
        computeAnswers(querier, predicate)
