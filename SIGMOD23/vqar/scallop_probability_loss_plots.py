from utilities2 import parseScallopLogsQueries, parseLTGsQueries, EXTRA_BIGGER_SIZE

import matplotlib.pyplot as plt
import numpy 

plt.rc('font', size=EXTRA_BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=EXTRA_BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=EXTRA_BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=EXTRA_BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=EXTRA_BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=EXTRA_BIGGER_SIZE)    # legend fontsize
plt.rc('figure', titlesize=30)  # fontsize of the figure title

fig = plt.figure(figsize=(13,7))

glog_answers_path = 'path-to-VQAR/C6/answers'
queries_lglog = parseLTGsQueries(glog_answers_path)
    
scallop_top1_file = 'path-to-all_top1_scallop.txt'  
scallop_top20_file = 'path-to-all_top20_scallop.txt'   
scallop1_times, queries_scallop_1  = parseScallopLogsQueries(scallop_top1_file)
scallop20_times, queries_scallop_20 = parseScallopLogsQueries(scallop_top20_file)

total_number_of_answers = 0 
for query in queries_lglog:
    total_number_of_answers = total_number_of_answers + len(queries_lglog[query])    

queries_wo_answers = set()
queries_w_lower_probabilities = set()
loss_scallop1_loss = []
for query in queries_scallop_1:
    if query in queries_lglog:
        answers_lglog = queries_lglog[query]
        answers_scallop1 = queries_scallop_1[query]
        for oid in answers_scallop1:
            if oid not in answers_lglog:
                queries_wo_answers.add(query)
                print('Warning: answer mismatch ' + query)
                continue
            else:
                probability_scallop = answers_scallop1[oid]
                probability_lglog = answers_lglog[oid]
                if not numpy.isclose(probability_scallop, probability_lglog):
                    if probability_scallop > probability_lglog:
                        queries_w_lower_probabilities.add(query)

                    else:
                        loss_scallop1_loss.append((probability_lglog - probability_scallop) / probability_lglog)

frequency1, bins1 = numpy.histogram(loss_scallop1_loss, bins=10)
n, bins, patches = plt.hist(loss_scallop1_loss, density=False, facecolor="blue", alpha=0.75)                
plt.xlabel('# Queries')
plt.ylabel('% Probability error')
fig.savefig('{}.png'.format('scallop_top1_error'), bbox_inches='tight')
    
loss_scallop20_loss = []
for query in queries_scallop_20:
    if query in queries_lglog:
        answers_lglog = queries_lglog[query]
        answers_scallop20 = queries_scallop_20[query]
        for oid in answers_scallop20:
            if oid not in answers_lglog:
                queries_wo_answers.add(query)
                print('Warning: answer mismatch ' + query)
                continue
            else:
                probability_scallop = answers_scallop20[oid]
                probability_lglog = answers_lglog[oid]
                if not numpy.isclose(probability_scallop, probability_lglog):
                    if probability_scallop > probability_lglog:
                        queries_w_lower_probabilities.add(query)
                    else:
                        loss_scallop20_loss.append((probability_lglog - probability_scallop) / probability_lglog)
                        
frequency2, bins2 = numpy.histogram(loss_scallop20_loss, bins=10)
n, bins, patches = plt.hist(loss_scallop20_loss, density=False, facecolor="purple", alpha=0.75)                
plt.xlabel('# Queries')
plt.ylabel('% Probability error')
fig.savefig('{}.png'.format('scallop_top20_error'), bbox_inches='tight')
        
