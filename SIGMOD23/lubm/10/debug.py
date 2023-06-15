
import glog
import os
import datetime
from utilities import computeLineage, computeProbability

loglevel = 2
size = 10
main_dir = 'data/TGs/lubm/lubm_{}/'.format(size)
os.chdir(main_dir)

if not os.path.exists('answers/'):
    os.makedirs('answers/')
    
for i in [1,2,3,4,5,6,7,8,9,10,11,12,13,14]:
    edb_file = 'edb.conf'
    rules = 'path-to-experiments/TGs/lubm/rules/LUBM_L_Q' + str(i) + '_magic.dlog'
    
    a = glog.EDBLayer(edb_file)
    program = glog.Program(a)
    program.load_from_file(rules)
    print("N. rules", program.get_n_rules())
    chaseProcedure = "probtgchase"
    typeProv = "FULLPROV"
    r = glog.Reasoner(chaseProcedure, a, program, typeProv=typeProv, edbCheck=False, queryCont=False)
    tg = r.get_TG()
    stats = r.create_model(0)

    predicate = 'q' + str(i)
    querier = glog.Querier(tg)

    print("Computing the leaves ...")
    start = datetime.datetime.now()
    ret = computeLineage(querier, predicate)
    end = datetime.datetime.now()
    duration = end - start
    time_to_compute_leaves = duration.total_seconds() * 1000
    print(time_to_compute_leaves)
    if ret != None:
        (answers, lineage_per_answer) = ret 
        print("Computing probability ...") 
        time_to_compute_probability = computeProbability(querier, predicate, answers, lineage_per_answer) 
        with open('LUBM-QA-{}.txt'.format(size), 'a') as file:
            file.write('Q' + str(i) + ' ' + stats + ' leaves_ms ' + str(time_to_compute_leaves) + ' probability_ms ' + str(time_to_compute_probability) + '\n')  
    else: 
        with open('LUBM-QA-{}.txt'.format(size), 'a') as file:
            file.write('Q' + str(i) + ' ' + stats + ' is empty ' + '\n')  
