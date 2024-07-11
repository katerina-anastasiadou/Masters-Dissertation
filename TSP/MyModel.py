# -*- coding: utf-8 -*-
"""
Created on Wed Jul 10 14:51:26 2024

@author: katan
"""

from helper import get_cutset, get_powerset, find_connected_components
from docplex.mp.model import Model

class MyModel:
    def __init__(self, name_input, data_input):
        self.model_instance = Model(name_input)

        # Decision variables
        self.x = self.model_instance.binary_var_dict(data_input.E_prime, name='x')
        self.y = self.model_instance.binary_var_matrix(data_input.V_prime, data_input.V_prime, name='y')

        # Objective function
        self.model_instance.minimize(
            self.model_instance.sum(self.x[i, j] * data_input.c_prime[i, j] for (i, j) in data_input.E_prime) +
            self.model_instance.sum(self.y[i, j] * data_input.a[i, j] for (i, j) in data_input.A))

        # Constraints
        self.model_instance.add_constraints(
            self.model_instance.sum(self.x[i, j] for (i, j) in get_cutset([i], data_input.E_prime)) == 2 * self.y[i,i]
            for i in data_input.V_prime)

        self.model_instance.add_constraints(self.y[i, j] <= self.y[j, j] for i in data_input.V_prime for j in data_input.V_prime)

        self.model_instance.add_constraints(
            self.model_instance.sum(self.y[i, j] for j in data_input.V_prime) == 1
            for i in data_input.V_prime if i != 0)

        self.model_instance.add_constraints(
            self.y[0, j] == 0
            for j in data_input.V_prime if j != 0)

        self.model_instance.add_constraint(self.y[0, 0] == 1) 
        
        
        
        
        
        
        
        
        
        
        