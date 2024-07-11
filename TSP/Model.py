# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 10:46:31 2024

@author: katan
"""
from helper import get_cutset, get_powerset, find_connected_components
from docplex.mp.model import Model

class MyModel:
    def __init__(self,name_input,data_input):
        
        
        self.model_instance = Model(name_input)

        # Decision variables
        self.x = self.model_instance.binary_var_dict(data_input.E, name = 'x')
        self.y = self.model_instance.binary_var_matrix(data_input.V, data_input.V, name='y')
        

        # Objective function
        self.model_instance.minimize(
            self.model_instance.sum(self.x[i, j] * data_input.c[i, j] for (i, j) in data_input.E) +
            self.model_instance.sum(self.y[i, j] * data_input.a[i, j] for (i,j) in data_input.A))

        # Constraints
        # Degree constraint: Ensure the sum of edges adjacent to i is at least 2 times the sum of y[i,i] for all i
        self.model_instance.add_constraints(
            self.model_instance.sum(self.x[i,j] for (i,j) in get_cutset([i], data_input.E)) == 2 * self.y[i,i] 
            for i in data_input.V)
        
        # Ensure y[i, j] is less than or equal to y[j, j] for all i, j
        self.model_instance.add_constraints(self.y[i,j] <= self.y[j,j] for i in data_input.V for j in data_input.V)
        
        # Assignment constraint: Each i must be assigned to exactly one j, except for i=0
        self.model_instance.add_constraints(
            self.model_instance.sum(self.y[i, j] for j in data_input.V) == 1
            for i in data_input.V if i != 0)
        
        # Ensure y[0, j] is 0 for all j except j=0
        self.model_instance.add_constraints(
            self.y[0, j]  == 0
            for j in data_input.V if j !=0 )
        
        # Ensure y[0, 0] is 1
        self.model_instance.add_constraint(self.y[0,0] == 1)
        
        # Initial solve to get the solution
        # self.solution = self.model_instance.solve(log_output=True)
        # component_list = find_connected_components(self.model_instance, solution, data_input)

        # while len(component_list) > 1:
        #     for component in component_list:
        #         # Connectivity constraint
        #         self.model_instance.add_constraint(
        #             self.model_instance.sum(self.x[i, j] for (i, j) in get_cutset(component, data_input.E)) >=
        #             2 * self.model_instance.sum(self.y[i, j] for i in component for j in data_input.V if j not in component)
        #         )

        #     # Solve the model with updated constraints
        #     solution = self.model_instance.solve(log_output=True)
        #     component_list = find_connected_components(self.model_instance, solution, data_input)

        #for S in get_powerset(data_input.V):
        #    if len(S) > 1 and 1 not in S:
        #        self.model_instance.add_constraint(
        #            self.model_instance.sum(self.x[i,j] for (i,j) in get_cutset(S, data_input.E)) >=
        #            2 * self.model_instance.sum(self.y[i,j] for i in S for j in data_input.V if j not in S))
                
        
        
        
        
        
        
        