# Reproducing the experiments on VQAR

## Data

To run the experiments, copy the following:
- ```VQAR\test\C6``` contains the C6 part of the [VQAR](https://proceedings.neurips.cc/paper/2021/hash/d367eef13f90793bd8121e2f675f0dc2-Abstract.html) testing queries.
- ```VQAR\SIGMOD23``` contains cached experimental results.


## Folder structure

- ```debug.py```. Runs TGs on queries from ```VQAR\test\C6```. Outputs a folder ```answers``` including the answers to the queries with their probabilities and file ```all_exact_results_tgs.txt``` including runtime statistics. 
- ```runtime_plots.py```. Produces runtime boxplots for TGs and Scallop. Required files are ```all_exact_results_tgs.txt``` and ```all_top1_scallop.txt``` and ```all_top20_scallop.txt```.  
- ```scallop_probability_loss_plots.py```. Produces histograms of the probability errors for Scallop top1 and top20. Required inputs are foler ```answers``` and files ```all_top1_scallop.txt``` and ```all_top20_scallop.txt```. 

### Notice


- Folder ```answers``` and file ```all_exact_results_tgs.txt``` can be produced by running [debug.py](https://github.com/karmaresearch/ltgs/blob/main/SIGMOD23/vqar/debug.py) or can be copied from ```VQAR\SIGMOD23```.
- Files ```all_top1_scallop.txt``` and ```all_top20_scallop.txt``` can be produced by running Scallop with top1 and top20 options or can be copied from ```VQAR\SIGMOD23```.
