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
