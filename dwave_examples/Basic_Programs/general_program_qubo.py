# Copyright 2020 D-Wave Systems Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# --------------------------------------------------------------------------#

# This program demonstrates a basic Ocean program that runs a QUBO problem on
# the D-Wave QPU.

# --------------------------------------------------------------------------#

# Import the functions and packages that are used
from dwave.system import EmbeddingComposite, DWaveSampler

import sys
import inspect

from matplotlib.mathtext import math_to_image

def traceit(frame, event, arg):
    function_code = frame.f_code
    function_name = function_code.co_name
    lineno = frame.f_lineno
    vars = frame.f_locals
    if event == 'call' and frame.f_code.co_name in ('sample_qubo', ) and vars['self'].__class__.__module__.find("dwave") != -1:
        source_lines, starting_line_no = inspect.getsourcelines(frame.f_code)
        loc = f"{function_name}:{lineno} {source_lines[lineno - starting_line_no].rstrip()}"
        
        print (str(vars['self'].__class__.__module__) + '.' + str(vars['self'].__class__.__qualname__) + "." + function_name)
        
        Q = vars['Q']
        print(Q)
        H = r'$\mathrm{H=';
        first = True;
        for pair in Q:                    
            if Q[pair] == 0:
                continue
            if not first and Q[pair] > 0:
                H += '+'
            first = False      
            H += ('' + str(Q[pair]) + " \cdot ")                 
            if pair[0] == pair[1]:
                H += (str(pair[0]).lower())
            else:
                H += (''.join(pair).lower())
        H += '}$'
        print(H);                
        math_to_image(H, "H.png", dpi=300, format='png')
                
        
        vars = ", ".join(f"{name} = {vars[name]}" for name in vars)
        print(f"{loc:50} ({vars})")
        

    return traceit
 
 
sys.settrace(traceit)

# Define the problem as a Python dictionary
def problemDefinition():
    a = {('B','B'): 1,
        ('K','K'): 1,
        ('A','C'): 2,
        ('A','K'): -2,
        ('B','C'): -2}
    return a

# Define the sampler that will be used to run the problem
sampler = EmbeddingComposite(DWaveSampler())

# Run the problem on the sampler and print the results
sampleset = sampler.sample_qubo(problemDefinition(),
                                 num_reads = 10,
                                 label='Example - Simple Ocean Programs: QUBO')
print(sampleset)
