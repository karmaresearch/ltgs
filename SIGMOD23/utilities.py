import math
from typing import List, Tuple, Dict
from problog.sdd_formula import SDDManager
import datetime
import os
from os import listdir
from os.path import join, isfile

def computeAnswers(querier, predicate:str):    
    results = open('answers/{}.txt'.format(predicate), 'w')
    nodes = querier.get_node_details_predicate(predicate)
    if nodes != "{}":
        tuples = querier.get_facts_coordinates_with_predicate(predicate)
        previous_answer = None
        for tuple in tuples:
            current_answer = tuple[0]
            terms = list()
            for argument in current_answer:
                terms.append(querier.get_term_name(argument))
            if previous_answer != current_answer:
                results.write('{}\n'.format(','.join(terms)))
                previous_answer = current_answer

def computeLineage(querier, predicate:str)->Tuple[List[Tuple], List[List[List[Tuple]]]]:    
    #print("Lineage computation...")
    nodes = querier.get_node_details_predicate(predicate)
    if nodes != "{}":
        tuples = querier.get_facts_coordinates_with_predicate(predicate)
        previous_answer = None
        lineage_per_answer = list()
        answers = list()
        for t in tuples:
            current_answer = t[0]
            current_answer = _decode_term(querier, current_answer)
            coordinates = t[1]
            node = coordinates[0]
            factid = coordinates[1]
            leaves = querier.get_leaves(node, factid)
            if previous_answer != current_answer:
                #atoms_per_answer.append(set()) 
                lineage_per_answer.append(list())
                answers.append(current_answer)
                previous_answer = current_answer
            position = len(lineage_per_answer) 
                            
            ### Collapsing ###
            for l in leaves:
                # Eliminate from the lineage the KG facts
                minimal_l = list()
                for leaf in l:
                    decoded = _decode_atom(querier, leaf)
                    ''' HACK!!!'''
                    if not decoded[0] in ["e_is_a", "e_oa_rel"]:
                        minimal_l.append(decoded)
                    ''' END OF HACK!!!'''
                lineage_per_answer[position-1].append(minimal_l)
                
        return (answers, lineage_per_answer) 
    else:
        return None    

def _decode_term(querier,terms:Tuple)->Tuple:
    decoded = ()
    for term in terms:
        decoded = decoded + (querier.get_term_name(term),)
    return decoded
    
def _decode_atom(querier,atom:Tuple)->Tuple:
    return (querier.get_predicate_name(atom[0]),) + _decode_term(querier,atom[1:])

def _create_SDD(lineage:List[List[Tuple]])->float:

    manager = SDDManager()
    nodedict = {}
    literaldict = {}
    index = 1
    for proof in lineage:
        for atom in proof:
            if atom not in nodedict:
                node = manager.literal(index)
                nodedict[atom] = node
                literaldict[atom] = index
                index = index + 1 
                
    formula = None
    for _, proof in enumerate(lineage):
        conjunction = None
        for atom in proof:
            node = nodedict[atom]
            if conjunction == None:
                conjunction = node 
            else:
                conjunction = conjunction.conjoin(node)
        if formula == None:
            formula = conjunction
        else:
            formula = formula.disjoin(conjunction)          
    #print("End of circuit computation...")
    return formula, literaldict

def _getProbability(database, predicate, t):
    rows = database[predicate] 
    for row in rows:
        if row[:len(t)] == t:
            if len(row) == len(t):
                return 1;
            else:
                return float(row[-1])
    return None

def computeProbability(querier, predicate:str, answers:List[Tuple], lineage_per_answer:List[List[List[Tuple]]], database:Dict = None, output_dir:str = 'answers')->float:

    results = open('{}/{}.probabilities.txt'.format(output_dir, predicate), 'w')
    
    time_to_wmc = 0
    for i, lineage in enumerate(lineage_per_answer):
        
        answer = answers[i]
        print('Answer ' + ','.join(answer))
        
        start = datetime.datetime.now()
        if len(lineage) > 1:
            
            formula, literaldict = _create_SDD(lineage)       
                    
            wmc = formula.wmc(log_mode = True)
            
            for atom, literal in literaldict.items():
                
                probability = 0.5
                if database != None:
                    probability = _getProbability(database, atom[0], atom[1:])
    
                    if probability == None:
                        raise Exception('Probability not found')
                
                # Positive literal weight
                wmc.set_literal_weight(literal, math.log(probability))
                # Negative literal weight
                wmc.set_literal_weight(-literal, math.log(1-probability))
        
            w = wmc.propagate()
            total_probability = math.exp(w)
        else:
            total_probability = 1
            t_disjunct = lineage[0]
            for atom in set(t_disjunct):
                
                probability = 0.5
                if database != None:
                    probability = _getProbability(database, atom[0], atom[1:])
                    if probability == None:
                        raise Exception('Probability not found')
                
                total_probability = total_probability * probability
        
        end = datetime.datetime.now()
        duration = end - start
        time_to_wmc = time_to_wmc + duration.total_seconds() * 1000
            
        results.write('{} {}\n'.format(','.join(answer), total_probability))
        
    results.close()
    
    return time_to_wmc

def loadVQARDatabase(inpath:str, separator:str, condition:str)->Dict[str,List]:
    start = 0
    derived_data = dict()
    files = [file for file in listdir(inpath) if isfile(join(inpath, file)) and condition in file]
    for fname in files:
        print(fname)
        if condition == '_probabilities':
            end = fname.rfind(condition)
            predicate = fname[0:end]
        else:
            end = fname.rfind('.csv')
            predicate = fname[0:end]
        with open(join(inpath,fname)) as infile:
            facts = list()
            for line in infile:
                if not line:
                    break  
                line = line.replace('\n','')
                arguments = line.split(separator)
                for t in range(len(arguments)):
                    arguments[t] = arguments[t].replace('"','')
                facts.append(tuple(arguments[start:]))
            derived_data[predicate] = facts
    return derived_data

def flushCache():
    process = subprocess.Popen(shlex.split('sudo /cm/shared/package/utils/bin/drop_caches'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    process.wait()
    
def relaxed_tsetin_transformation(lineage, variables, weights):
    
    #TO AMMEND SEEMS WRONG
    #lineage = set(lineage)
    mapping = dict(zip(variables, [str(i) for i in range(1,len(variables)+1)]))
    number_of_variables = len(variables) 
    
    #Apply the substitution to the lineage 
    mapped_lineage = []
    for disjunct in lineage:
        mapped_lineage.append([*map(mapping.get, disjunct)])
        #print([*map(mapping.get, disjunct)])
    
    mapped_weights = {mapping[k]: w for k, w in weights.items()}
    
    zs = list()
    rs = list()
    clauses = list()
    #apply the relaxed tsetin transformation
    for disjunct in mapped_lineage:
        #create two fresh variables 
        z = str(number_of_variables + 1)
        r = str(number_of_variables + 2)
        number_of_variables = number_of_variables + 2
        
        #the z's should be cached
        zs.append(z)
        #the r's should be cached
        rs.append(r)
    
        clause = ['-' + X for X in disjunct]
        clause.append(z)
        clauses.append(clause)
                
        clause = ['-' + X for X in disjunct]
        clause.append(r)
        clauses.append(clause)
        
        clause = [z,r]
        clauses.append(clause)
        
    clauses.append(zs)
        
    for z in zs:
        mapped_weights[z] = 1
        mapped_weights['-' + z] = 1

    for r in rs:
        mapped_weights[r] = 1
        mapped_weights['-' + r] = -1
        
    return clauses, mapped_weights, number_of_variables
    
def MCSolver(solver_exec, querier, predicate, answers, lineage_per_answer, variables_per_answer):
    
    results = open('answers/{}.c2d.txt'.format(predicate), 'a') 
    
    output = 'answers'
    total_time = 0 
    for i, lineage in enumerate(lineage_per_answer):
           
        answer = answers[i]
        terms = list()
        for argument in answer:
            terms.append(querier.get_term_name(argument))
            #results.write('{} {}\n'.format(','.join(terms), probability))
        print('{} out of {}: {}'.format(i, len(lineage_per_answer), ','.join(terms)))
        
        start_per_answer = datetime.datetime.now()
        if len(lineage) > 1:
            
            #Open a file for writing 
            #The name of the file should be the name of the predicate
            solver_input = open('{}/{}.cnf'.format(output, predicate), 'w')
            variables = variables_per_answer[i]
            weights = dict(zip(variables, [0.5 for i in range(1,len(variables)+1)]))
            
            #Translate from DNF to CNF
            start = datetime.datetime.now()
            #clauses = list(itertools.product(*mapped_lineage))
            clauses, mapped_weights, number_of_variables = relaxed_tsetin_transformation(lineage, variables, weights)
            end = datetime.datetime.now()
            duration = end - start    
            total_time += duration.total_seconds() * 1000
            print('Time for translation {}\n'.format(duration.total_seconds() * 1000))
            
            #Write instance-specific information
            solver_input.write('p wcnf {} {}\n'.format(number_of_variables, len(clauses)))
            
            #Write the weights of the variables 
            for X,W in mapped_weights.items():
                solver_input.write('w {} {}\n'.format(X, W))
            
            #Write each CNF to the file
            for element in clauses:
                solver_input.write('{} 0\n'.format(' '.join(element)))
                
            solver_input.close()
                
            #Call the solver 
            cmd = solver_exec + ' -count ' + ' -smooth_all ' + ' -in {}/{}.cnf '.format(output, predicate)
            print(cmd)
            fout = output + "/results_" + predicate
            o = open(fout, 'wt')
            ferr = output + "/logs_" + predicate
            o2 = open(ferr, 'wt')
            o2.write('CMD: ' + cmd + '\n')
            o2.flush()
            start = datetime.datetime.now()
            process = subprocess.Popen(shlex.split(cmd), stdout=o, stderr=o2)
            process.wait()
            end = datetime.datetime.now()
            duration = end - start    
            total_time += duration.total_seconds() * 1000
            print('Time for invoking the executable {}\n'.format(duration.total_seconds() * 1000))
            flushCache()

        else:
            probability = 1
            t_disjunct = lineage[0]
            start = datetime.datetime.now()
            for fact in set(t_disjunct):
                probability = probability * 0.5
            end = datetime.datetime.now()
            duration = end - start
            total_time += duration.total_seconds() * 1000
        
        
        end_per_answer = datetime.datetime.now()
        duration = end_per_answer - start_per_answer
        time_to_wmc = duration.total_seconds() * 1000
        results.write('{} {}\n'.format(','.join(terms), str(time_to_wmc)))
            
    results.close()            
    return total_time

