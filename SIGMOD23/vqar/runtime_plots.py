from utilities2 import parseLTGsLogs, parseScallopLogs, EXTRA_BIGGER_SIZE, MAT_GLOG, LEAVES_GLOG, PROB_GLOG

import matplotlib.pyplot as plt
plt.rc('font', size=EXTRA_BIGGER_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=EXTRA_BIGGER_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=EXTRA_BIGGER_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=EXTRA_BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=EXTRA_BIGGER_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=EXTRA_BIGGER_SIZE)    # legend fontsize
plt.rc('figure', titlesize=30)  # fontsize of the figure title

fig = plt.figure(figsize=(13,7))

glog_file = 'path-to-all_exact_results_tgs.txt'
queries_lglog, exact_mat = parseLTGsLogs(glog_file, MAT_GLOG)
_, exact2_leaves = parseLTGsLogs(glog_file, LEAVES_GLOG)
_, exact3_prob = parseLTGsLogs(glog_file, PROB_GLOG)
exact = [x + y + z for x, y, z in zip(exact_mat, exact2_leaves, exact3_prob)]

scallop_top1_file = 'path-to-all_top1_scallop.txt'  
scallop_top20_file = 'path-to-all_top20_scallop.txt'   
queries_scallop_1, scallop1_times = parseScallopLogs(scallop_top1_file)
queries_scallop_20, scallop20_times = parseScallopLogs(scallop_top20_file)


queries_scallop_1_filtered = [i for i, e in enumerate(queries_scallop_1) if e in queries_lglog]
queries_scallop_20_filtered = [i for i, e in enumerate(queries_scallop_20) if e in queries_lglog]

scallop1_times_filtered = [scallop1_times[i] for i in queries_scallop_1_filtered]
scallop20_times_filtered = [scallop20_times[i] for i in queries_scallop_20_filtered]

c = "teal"
box1 = plt.boxplot(exact_mat, positions=[1], notch=False, patch_artist=True,
            boxprops=dict(facecolor=c, color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
            showfliers=False
            )
c = "darkviolet"
box5 = plt.boxplot(scallop1_times_filtered, positions=[3], notch=False, patch_artist=True,
            boxprops=dict(facecolor=c, color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
            showfliers=False
            )

c = "purple"
box6 = plt.boxplot(scallop20_times_filtered, positions=[4], notch=False, patch_artist=True,
            boxprops=dict(facecolor=c, color=c),
            capprops=dict(color=c),
            whiskerprops=dict(color=c),
            flierprops=dict(color=c, markeredgecolor=c),
            medianprops=dict(color=c),
            showfliers=False
            )

    

ax = plt.gca()
plt.xticks([1, 3,4], ['LTGs\nExact',"Scallop\nTop-1", 'Scallop\nTop-20'])
plt.gca().set_yscale("log")
fig.savefig('{}.png'.format('scallop_vs_ltgs_vqar'), bbox_inches='tight')
    
        
