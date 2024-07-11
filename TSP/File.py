# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 11:27:01 2024

@author: katan
"""
from cplex.callbacks import LazyConstraintCallback, UserCutCallback
from docplex.mp.callbacks.cb_mixin import ConstraintCallbackMixin
from helper import *
import igraph as ig

class Callback_lazy(ConstraintCallbackMixin, LazyConstraintCallback):
    def __init__(self, env):
        """
        Initializes the Callback_lazy class.
 
        Args:
            env: CPLEX environment.
 
        Returns:
            None
        """
        LazyConstraintCallback.__init__(self, env)
        ConstraintCallbackMixin.__init__(self)
    def __call__(self):
        """
        Callback function to be called for lazy constraint callback.
 
        Returns:
            None
        """
        print('running lazy callback')
        self.num_calls += 1
        sol_x = self.make_solution_from_vars(self.mdl.x.values())
    
        edges_in_solution = [(i, j) for (i, j) in self.problem_data.E if sol_x.get_value(self.mdl.x[i,j]) > 0.9]
        # component_list = find_connected_components(self.model_instance, sol_x, self.problem_data)
        
        g = ig.Graph()
        g.add_vertices(len(self.problem_data.V))  # Adding the number of vertices
        g.add_edges(edges_in_solution)
         
        # Get the connected components
        components = g.connected_components(mode='weak')
        
        # Extract the component membership list and adjust back to original IDs
        component_list = [[v for v in comp] for comp in components]
      
        if len(component_list) > 1 :
            for component in component_list:
                    # Connectivity constraint
                if len(component)>2 and 0 not in component:
                   print(component)
                   ct_cutset = self.mdl.model_instance.sum(self.mdl.x[i, j] for (i, j) in get_cutset(component, self.problem_data.E))
                   for i in component:
                      ct =  ct_cutset >= self.mdl.model_instance.sum(self.mdl.y[i, j] for  j in component)
                      ct_cpx = self.linear_ct_to_cplex(ct)
                      self.add(ct_cpx[0],ct_cpx[1],ct_cpx[2])
        else:
            min_cut_value, min_cut_edges = g.mincut()
            if min_cut_value == 1:
                for (i, j) in min_cut_edges:
                    ct = self.mdl.x[0, i] >= 2
                    ct_cpx = self.linear_ct_to_cplex(ct)
                    self.add_lazy_constraint(ct_cpx[0], ct_cpx[1], ct_cpx[2])                      
   
                    
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
        #            2 * self.model_instance.sum(self

class Callback_user(ConstraintCallbackMixin, UserCutCallback):
    def __init__(self, env):
        """
        Initializes the Callback_user class.

        Args:
            env: CPLEX environment.

        Returns:
            None
        """
        UserCutCallback.__init__(self, env)
        ConstraintCallbackMixin.__init__(self)
        
    def __call__(self):
        """
        Callback function to be called for user cut callback.

        Returns:
            None
        """
        print('Running user cut callback')
        fractional_vars = [(var, var.solution_value) for var in self.mdl.x.values() if 0 < var.solution_value < 1]
        
        if fractional_vars:
            for (var, value) in fractional_vars:
                i, j = var.get_key()
                # Add a user cut constraint to force the variable to integer value
                self.add_user_cut(self.mdl.x[i, j] >= 0)
                self.add_user_cut(self.mdl.x[i, j] <= 1)
