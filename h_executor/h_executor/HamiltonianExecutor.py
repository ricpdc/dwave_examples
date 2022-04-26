'''
Created on 22 abr 2022

@author: Alarcos
'''

# Import the functions and packages that are used
from dwave.system import EmbeddingComposite, DWaveSampler

import dwave.inspector

from dimod import BinaryQuadraticModel

import re
import os
from glob import glob

PATH = "../../dwave_examples/"
NUM_READS = 10

hamiltonian_files = [y for x in os.walk(PATH) for y in glob(os.path.join(x[0], '*/hamiltonian_expressions/*.txt'))]

print("Files to be processed")
print(hamiltonian_files)

#hamiltonian_files = {'C:/Users/Alarcos/git/dwave_examples/dwave_examples/nurse-scheduling/hamiltonian_expressions/LeapHybridSampler.sample.181_20220422_170111.txt'}

for file_path in hamiltonian_files:

    print('Processing file: ' + file_path)

    try:
        #open a hamiltonian file
        hamiltonian_file = open(file_path, "r")
        #read whole file to a string
        H = hamiltonian_file.read()
        #close file
        hamiltonian_file.close()
    
        print('Processing expression: ' + H)
        
        
        
        H = H.replace(' ', '')
        H = H.replace('H=', '')
        
        expressions = re.findall(r"([+-]?[^-+]+)", H)
        
        
        problem_definition = {}
        offset = None
        
        for expression in expressions:
            e = expression.split('*')
            
            if len(e) == 1:
                offset = float(e[0])
            
            else:
            
                c = 2*float(e[0])
                v1 = e[1]
                if len(e)>2:
                    v2 = e[2]
                else:
                    v2 = v1
                print(v1, v2, str(c))
                problem_definition[(v1, v2)] = c
            
                
            
            
        print("Problem definition:")   
        print(problem_definition)
        
        
        # Define the sampler that will be used to run the problem
        sampler = EmbeddingComposite(DWaveSampler())
        
        label="HE_"+file_path

        sampleset = None
        
        # Run the problem on the sampler
        if offset is not None:
            print("Offset: " + str(offset))
            bqm = BinaryQuadraticModel.from_qubo(problem_definition, offset=offset)
            sampleset = sampler.sample(bqm, num_reads = NUM_READS, label=label)
        else:
            sampleset = sampler.sample_qubo(problem_definition, num_reads = NUM_READS, label=label)    
        
        # Print the results and show inspector
        if sampleset is not None:
            print(sampleset)
            dwave.inspector.show(sampleset)
    
    
    except IndexError:
        print (IndexError)
    except:
        print("Something else went wrong")
        
print("End of program!")