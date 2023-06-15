# About this README #

This README provides instructions to build and use the API for the lineage trigger graphs C++ library.

## Folder structure ##

This folder contains the following: 

* Python scripts to reproduce the SIGMOD'23 experiments (folder _SIGMOD23_).
* Linux shell scripts to reproduce the SIGMOD'23 experiments (folder _scripts_).
* A Jupyter notebook with an example presenting the functionality of the library (file _Example.ipynb_).

To run the Jupyter notebook (after building the Python library), run the command

```
jupyter notebook Example.ipynb
```

If not installed, follow the instructions in https://jupyter.org/install.html. 


## Requirements ##

* Anaconda 4
* Python 3
* CMake 3.10
* gcc 8.4 (and higher)
* g++ 8.4 (and higher)


## Building the Python API ##

### 1. Install the header files and static libraries for python dev ###

```
sudo apt-get install pythonX-dev
```
where X can be either 3 or a specific Python version, e.g., 3.8

### 2. Build the LTGs library ###

```
git clone https://github.com/karmaresearch/glog.git
cd glog 
mkdir build
cd build
cmake ..
make
```

### 3. Build the Python API ###

```
git clone https://github.com/karmaresearch/glog-python.git
cd glog-python
mkdir build
cd build
cmake ..
make
```

The commands were tested on an Intel i7 processor running Ubuntu 18.04.5 LTS.

The successful execution of the instructions will produce the following:

* glog.so, a shared library for calling the engine within Python.

### 4. Install PySDD ###

This is a library for computing probabilities of formulas. Notice that it is not required to build the ltgs API. However, it is needed to reproduce the experiments from the SIGMOD 2023 submission. See https://pypi.org/project/PySDD/ for a documentation. To install it run the following command: 

```
pip install pysdd
```

## Using the Python API ##

The Python API provides the following functionality: 

* Compute a (probabilistic) model using LTGs.
* Get all the facts for a given predicate. 
* Collect and visualize the provenance trees of the derived facts. 
* Get the leaves of derivation trees. 
* Execute queries over a model. 

To call the library within a Python script, set the _PYTHONPATH_ environment variable to point to the folder including the *glog.so* library. Alternatively, import the ltgs library using the sys.path.insert command. 

```
import sys
sys.path.insert(0, path-to-ltgs-shared-library)
import glog
```

### Computing a probabilistic model ###

```
# Path to the data configuration file
edb_file = 'data/TGs/lubm/lubm_100/edb.conf'
    
# Create the edb layer based on the input data 
layer = glog.EDBLayer(edb_file)

# Path to the rules file
# The rules have been already transformed using magic sets, as we are in the QA setting in which we want to compute the probabilities of atoms. 
# Here we consider Q1 from LUBM
rules = 'data/TGs/lubm/rules/LUBM_L_Q1_magic.dlog'

# Create a program based on the input rules
program = glog.Program(layer)
program.load_from_file(rules)
print("N. rules", program.get_n_rules())

# This is where we specify the type of reasoning we want to do, we can also call the non-probabilistic engine by providing the arguments "tgchase" and "NODEPROV". 
chaseProcedure = "probtgchase"
typeProv = "FULLPROV"
reasoner = glog.Reasoner(chaseProcedure, layer, program, typeProv=typeProv, edbCheck=False, queryCont=False)

# Get the probabilistic TG-based reasoner
tg = reasoner.get_TG()

# Run the reasoning process
# The first argument above denotes the logging level. There is a second optional argument which controls the reasoning depth. By default, reasoning runs until completion.  
statistics = reasoner.create_model(0)  
```

The _reasoner.create_model()_ function returns an object that provides the following statistics: 

* max\_mem\_mb: pick memory consumption in MB.
* n\_derivations: total number of different derivations. In the probabilistic setting, the same fact may be derived in many different ways. In contrast to the non-probabilistic setting, we need to maintain all these different derivations. 
* n\_edges, n\_nodes: total number of edges and nodes in the resulting probabilistic TG.
* runtime\_ms: total time in ms to compute the probabilistic model.


### Computing a non-probabilistic model ###

The Python commands are as above. The only difference is the arguments to the _glog.Reasoner()_ function. 
To perform non-probabilistic reasoning _without maintaining the provenance_, we only need to call the function by setting 

```
chaseProcedure = "tgchase"
typeProv = "NODEPROV"
```

To perform non-probabilistic reasoning _with maintaining the provenance_, we only need to call the function by setting 

```
chaseProcedure = "tgchase"
typeProv = "FULLPROV"
```


Notice that _all_ the commands that will follow apply both to the probabilistic and the non-probabilistic case. 
However, to collect and visualize provenance trees in the non-probabilistic case, we need to run the reasoner with the options

```
chaseProcedure = "tgchase"
typeProv = "FULLPROV"
```

### Getting all the facts for a given predicate ###

To do this, we need to create a _querier_ object. The object is created using the _Querier_ function with arguments the TG computed by the reasoner:

```
querier = glog.Querier(tg)
```

The command below returns all the nodes storing facts for the _GraduateStudent_ predicate

```
querier = glog.Querier(tg)
predicate = 'GraduateStudent'
nodes = querier.get_node_details_predicate(predicate)
nodes = json.loads(nodes)
```

We can iterate through the nodes and print the facts inside the nodes using the commands below: 

```
for node in nodes:
    #print("Get facts in node", node, "...")
    facts = querier.get_facts_in_TG_node(int(node['id']))
    facts = json.loads(facts)
    for i, fact in enumerate(facts):
        print(fact)
```

### Collecting and visualizing the provenance trees of the derived facts ###

To get the derivation tree of the i-th fact stored within a given node, we need to call the command below: 

```
derivation_tree = querier.get_derivation_tree(int(node.get('id')),i)
```
Continuing with the for loop from above, the code visualizes the derivation trees of the facts stored within the nodes. 

```
for node in nodes:
    #print("Get facts in node", node, "...")
    facts = querier.get_facts_in_TG_node(int(node['id']))
    facts = json.loads(facts)
    for i, fact in enumerate(facts):
        derivation_tree = querier.get_derivation_tree(int(node.get('id')),i)
        derivation_tree = json.loads(derivation_tree)
        display(JSON(derivation_tree, expanded=True))
```

To get the root fact of a derivation tree, run the following command: 

```
root = derivation_tree.get('fact')
```

### Getting the leaves of derivation trees ###

To get the leaves (encoded in an integer form for reducing the latency) of the i-th fact in a given node run the following command:

```
leaves = querier.get_leaves(int(node.get('id')),i)
```

_Remark:_ the command below returns all the information associated with a given predicate P, i.e., the node where P-facts are stored, the offset of those facts, as well as their leaves. This command is used for our experiments to optimize the performance.  

```
tuples = querier.get_facts_coordinates_with_predicate(predicate)
```


### Executing queries over a model ###

Suppose that we want to execute the following query over a (probabilistic) model:

```
"Q1(X,Y) :- GraduateStudent(X), takesCourse(X,Y)"
```

Then, we simply need to run the following commands:

```
query = "Q1(X,Y) :- GraduateStudent(X), takesCourse(X,Y)"
queryId = program.add_rule(query)
ts, stats_query = reasoner.execute_rule(queryId)
print("The rule that we executed returnd {:n} answers".format(n_answers))
```

### Storing the probabilistic model ###

The easiest way to dump the probabilistic model in a folder is via the command line interface. For instance, the command below 
computes the probabilistic model for the _lubm\_10_ database using the rules in the file _LUBM\_L\_Q1\_magic.dlog_ and stores the model in different files, one per predicate, inside the folder _probabilistic\_model\_LUBM10\_Q1_.

```
glog tgchase --edb data/TGs/lubm/lubm_10/edb.conf --rules data/TGs/lubm/rules/LUBM_L_Q1_magic.dlog --logLevel info --querycont 0 --edbcheck 0 --storemat_path probabilistic_model_LUBM10_Q1 --storemat_format files --decompressmat 1 2>&1 | tee logs.txt 
```

Instructions for using the command line interfaces can be found in https://github.com/karmaresearch/glog. 

## Reproducing the experiments from SIGMOD'23 submission ##

### Scripts ###

The Python scripts to reproduce the experiments are inside the _SIGMOD23_ folder. 

### Datasets ###

The data to test the performance of the engine are in https://drive.google.com/drive/folders/17JjrXS0IRtjDVFAr07kdrYpXdI-wD8bg?usp=drive_link.

### Reproducing the experiments using the Python API ###

We provide an example of using the Python library for running Q1 from the LUBM-100 benchmark. 
LUBM\_PATH denotes the path to the lubm folder after unzipping the contents of contents of https://drive.google.com/drive/folders/1CEfyaGlZ9BIToSKy0RUMT5K_NZSFym8V?usp=drive_link.

**Inputs**
* The database configuration file LUBM\_PATH\\lubm\_100\\edb.conf. The configuration file stores the paths to the database data.
* The rules to answer Q1, LUBM\_PATH\\rules\\LUBM\_L\_Q1\_magic.dlog. The rules are computed by applying the magic sets transformation to the rules inside LUBM\_PATH\\rules\\LUBM\_L\_csv.dlog

**Outputs**

1. A file named LUBM-QA-100.txt. The file provides the following statistics: 
* max\_mem\_mb, n\_derivations, n\_edges, n\_nodes and runtime\_ms are as described above.
* leaves\_ms: total time in ms to compute the leaves in the derivation history of each query answer.
* probability\_ms: total time in ms to compute the probability of the query answers given the leaves in the provevance of each answer.

2. A file named QX.txt including one row per answer along with its associated probability. 

To run the script, set the _PYTHONPATH_ environment variable to point to the folder including the *glog.so* library. Alternatively, import the ltgs library using the sys.path.insert command. 

```
import sys
sys.path.insert(0, path-to-ltgs-shared-library)
import glog
import os
import datetime
from utilities import computeLineage, computeProbability
# The utilities files is used to compute the lineage (function computeLineage) of an atom and then based on the lineage, its probability (function computeProbability)

# Configuration to run lubm_100
# To run lubm_10, change to main_dir = 'data/TGs/lubm/lubm_10' 
main_dir = 'data/TGs/lubm/lubm_100'
os.chdir(main_dir)

# Path to the data configuration file
edb_file = 'edb.conf'

# Path to the rules file. 
# The rules have been already transformed using magic sets, as we are in the QA setting in which we want to compute the probabilities of atoms. Here we consider Q1
rules = 'data/TGs/lubm/rules/LUBM_L_Q1_magic.dlog'
    
# Create the edb layer based on the input data 
layer = glog.EDBLayer(edb_file)

# Create a program based on the input rules
program = glog.Program(layer)
program.load_from_file(rules)
print("N. rules", program.get_n_rules())

# Specify the type of reasoning (probabilistic in our case). We can also call the non-probabilistic engine by providing the arguments "tgchase" and "NODEPROV". 
chaseProcedure = "probtgchase"
typeProv = "FULLPROV"
reasoner = glog.Reasoner(chaseProcedure, layer, program, typeProv=typeProv, edbCheck=False, queryCont=False)

# Get the probabilistic TG-based reasoner
tg = reasoner.get_TG()

# Run the reasoning process. The first argument above denotes the logging level. There is a second optional argument which controls the reasoning depth. By default, reasoning runs until completion.   
statistics = reasoner.create_model(0) 

##### At this point we have a probabilistic model and we can query it to get the provenance of the atoms and compute their probabilities #####

# Form the predicate for which we want to compute the probabilities of its atoms. In our example, the predicate is q1 (the first LUBM query).
# To run queries q2--q14, set variable predicate = 'q2', etc.   
predicate = 'q1'

# Create an object for querying the model.  
querier = glog.Querier(tg)

print("Computing the lineage ...")
start = datetime.datetime.now()

# Compute the lineage of each q1-atom. The lineage of the query is the leaves in its derivation provenance. 
ret = computeLineage(querier, predicate)
end = datetime.datetime.now()
duration = end - start
time_to_compute_leaves = duration.total_seconds() * 1000

if ret != None:
    (answers, lineage_per_answer, variables_per_answer) = ret 
    print("Computing the probability ...") 
    start = datetime.datetime.now()
    
    # Compute the probabilities of all q1-atoms returned by the querier 
    computeProbability(querier, predicate, answers, lineage_per_answer, variables_per_answer) 
    end = datetime.datetime.now()
    duration = end - start
    time_to_probability = duration.total_seconds() * 1000
    with open('LUBM-QA-100.txt', 'a') as file:
        file.write('Q1' + ' ' + statistics + ' leaves_ms ' + str(time_to_compute_leaves) + ' probability_ms ' + str(time_to_probability) + '\n')  
else: 
    with open('LUBM-QA-100.txt', 'a') as file:
        file.write('Q1' + ' ' + statistics + ' is empty ' + '\n')  
```

### Probability computation using the c2d solver ###

By default, probability is computed via pysdd. To call the c2d solver instead, first install c2d from https://zenodo.org/record/4292581/files/MC2020_Solvers.tar.bz2?download=1, and call ```MCSolver``` instead of calling ```computeProbability``` with one additional argument, that is the path to the solver, e.g., ```MC2020_Solvers/MC2020_SubmissionsSolvers/track2/c2d-wmc-solver/bin/c2d```. 
