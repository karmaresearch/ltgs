
import glog
import os
import datetime
from utilities import computeAnswers

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
    computeAnswers(querier, predicate)
