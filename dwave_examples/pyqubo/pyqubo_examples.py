'''
Created on 12 nov 2021

@author: Alarcos
'''


import pprint
import neal
from cpp_pyqubo import Spin
from cpp_pyqubo import Binary



s1, s2, s3, s4 = Spin("s1"), Spin("s2"), Spin("s3"), Spin("s4")



H = (4*s1 + 2*s2 + 7*s3 + s4)**2



model = H.compile()


qubo, offset = model.to_qubo()

pp = pprint.PrettyPrinter()

print('\n ONE \n');
pp.pprint(qubo)  # doctest: +SKIP
print(offset)



print('\n TWO \n');
linear, quadratic, offset = model.to_ising()
pp.pprint(linear) # doctest: +SKIP
pp.pprint(quadratic)
print(offset)



print('\n THREE \n');

x1, x2 = Binary('x1'), Binary('x2')
H = 2*x1*x2 + 3*x1
pp.pprint(H.compile().to_qubo())


'''Solve QUBO by dimod Sampler'''
model = H.compile()
bqm = model.to_bqm() 


sa = neal.SimulatedAnnealingSampler()
sampleset = sa.sample(bqm, num_reads=10)
decoded_samples = model.decode_sampleset(sampleset)
best_sample = min(decoded_samples, key=lambda x: x.energy)
pp.pprint(best_sample.sample) 