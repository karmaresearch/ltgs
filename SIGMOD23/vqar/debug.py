'''
The script loads the test/C6 queries from the Scallop benchmark and the 'test_C6_queries.txt' file with queries that TGs can answer exactly and outputs 
 - an answers folder with the probability of each query; and 
 - a file 'all_exact_results_glog.txt' with runtime statistics.
'''

import glog
import os
from os.path import join
import datetime
from utilities_clean import computeLineage, computeProbability, loadVQARDatabase

loglevel = 2 # INFO level
main_dir = 'path-to-VQAR/test/C6'
os.chdir(main_dir)
chaseProcedure = "probtgchase" 
typeProv = "FULLPROV"

if not os.path.exists('answers/'):
    os.makedirs('answers/')
    
with open('path-to-test_C6_queries.txt') as infile:    
    for rule in infile:
        rule = rule.replace('\n','')
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
        print("Computing the leaves ...")
        start = datetime.datetime.now()
        ret = computeLineage(querier, predicate)
        end = datetime.datetime.now()
        duration = end - start
        time_to_compute_leaves = duration.total_seconds() * 1000
        if ret != None:
            (answers, lineage_per_answer) = ret 
            
            database = loadVQARDatabase(join(main_dir,query), '\t', '_probabilities')
            if len(database) == 0:
                database = None
                print("No probabilities specified for query " + query)
            
            print("Computing probability ...") 
            time_to_wmc = computeProbability(querier, predicate, answers, lineage_per_answer, database) 
            with open('all_exact_results_tgs.txt', 'a') as file:
                file.write(query + ' ' + stats + ' leaves_ms ' + str(time_to_compute_leaves) + ' wmc_ms ' + str(time_to_wmc) + '\n')  
        else: 
            with open('all_exact_results_tgs.txt', 'a') as file:
                file.write(query + ' ' + stats + ' is empty ' + '\n')  
           
            
