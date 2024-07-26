# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 11:27:01 2024

@author: katan
"""
from cplex.callbacks import LazyConstraintCallback, UserCutCallback
from docplex.mp.callbacks.cb_mixin import ConstraintCallbackMixin
from helper import *
import igraph as ig
from itertools import combinations

class Callback_lazy(ConstraintCallbackMixin, LazyConstraintCallback):
    def __init__(self, env):
        """
        Initializes the Callback_lazy class.

        Args:
            model_instance: The CPLEX model instance.
            mdl: An instance of MyModel.
            data: Problem data containing attributes like `E_prime`, `V_prime`, `c_prime`, etc.

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
        sol_y = self.make_solution_from_vars(self.mdl.y.values())
        
        edges_in_solution = [(i, j) for (i, j) in self.problem_data.E if sol_x.get_value(self.mdl.x[i, j]) > 0.9]
        vertices = [i for i in self.problem_data.V if sol_y.get_value(self.mdl.y[i, i]) > 0.9]
 
        print("Edges in solution:", edges_in_solution)
        print("Vertices:", vertices)

        g = ig.Graph()
        g.add_vertices(max(vertices)+1)  # Adding the number of vertices
        g.add_edges(edges_in_solution)
         
        # Get the connected components
        components = g.connected_components(mode='weak')
        
        # Extract the component membership list and adjust back to original IDs
        component_list = [list(comp) for comp in components]
        print(component_list)
        
        if len(component_list) > 1 :
            for component in component_list:
                # Connectivity constraint
                if len(component) > 2 and 0 not in component:
                    print("Adding cut for component:", component)
                    ct_cutset = self.mdl.model_instance.sum(self.mdl.x[i, j] for (i, j) in get_cutset(component, self.problem_data.E))
                    for i in component:
                       ct =  ct_cutset >= 2*self.mdl.model_instance.sum(self.mdl.y[i, j] for j in component)
                       ct_cpx = self.linear_ct_to_cplex(ct)
                       self.add(ct_cpx[0],ct_cpx[1],ct_cpx[2])
           

class Callback_user(ConstraintCallbackMixin, UserCutCallback):
    def __init__(self, env):
        """
        Initializes the Callback_lazy class.

        Args:
            model_instance: The CPLEX model instance.
            mdl: An instance of MyModel.
            data: Problem data containing attributes like `E_prime`, `V_prime`, `c_prime`, etc.

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
        print('running user callback')
        self.num_calls += 1
        sol_x = self.make_solution_from_vars(self.mdl.x.values())
        sol_y = self.make_solution_from_vars(self.mdl.y.values())
        
        edges_in_solution = [(i, j) for (i, j) in self.problem_data.E if sol_x.get_value(self.mdl.x[i, j]) > 0.0000001]
        vertices = [i for i in self.problem_data.V if sol_y.get_value(self.mdl.y[i, i]) > 0.000001]
        edges_map = map_edges(vertices, edges_in_solution)
        
        print("Edges in solution:", edges_in_solution)
        print("mapped Edges in solution:", edges_map)
        print("Vertices:", vertices)

        g = ig.Graph()
        g.add_vertices(vertices)
        g.add_edges(edges_map)
         
        # Get the connected components
        components = g.connected_components(mode='weak')
        component_list = [list(comp) for comp in components]
        print(component_list)

        if len(component_list) > 1:
            for component in component_list:
                component_unmapped = [vertices[i] for i in component]
                if len(component_unmapped) > 2 and 0 not in component_unmapped:
                    #print(component_unmapped)
                    for i in component_unmapped:
                        ct_cutset = self.mdl.model_instance.sum(self.mdl.x[i, j] for (i, j) in get_cutset(component_unmapped, self.problem_data.E))
                        ct = ct_cutset >= 2 * self.mdl.model_instance.sum(self.mdl.y[i, j] for j in component_unmapped)
                        ct_cpx = self.linear_ct_to_cplex(ct)
                        self.add(ct_cpx[0], ct_cpx[1], ct_cpx[2])                    
        else:
            print('min cut here')
            capacity = [max(1, sol_x.get_value(self.mdl.x[i, j])) for (i, j) in edges_in_solution]
            g.es["capacity"] = capacity
            cut = g.mincut()
            print('run min cut')
            g.add_vertex(self.problem_data.n)
            for v in vertices:
                if v != 0:
                    dummy_edges = []
                    dummy_capacity = []                    
                    for j in self.problem_data.V:
                        if sol_y.get_value(self.mdl.y[v, j]) > 0.000001:                            
                            dummy_edges.append((j,self.problem_data.n))
                            dummy_capacity.append(sol_y.get_value(self.mdl.y[v, j]))
                    print('finished loop')
                    dummy_vertices = vertices + [self.problem_data.n]
                    edges_map_dummy = map_edges(dummy_vertices, dummy_edges)
                    #print(dummy_edges)
                    #print(edges_map_dummy)
                    #print([v for v in g.vs])
                    g.add_edges(edges_map_dummy)
                    #print(len(dummy_vertices))
                    cut = g.mincut(0, len(vertices))
                    value = cut.value
                    partition = cut.partition
                    print("Value:", value)
                    print("Partition:",  partition)
                    g.delete_edges(edges_map_dummy)
                    if value < 2 * sol_y.get_value(self.mdl.y[v, v]):
                         print('violated sec add cut')
                         for component in partition:
                             print("Component:", component)
                             component_unmapped = [dummy_vertices[i] for i in component]
                             print("Component unmapped:", component_unmapped)
                             if self.problem_data.n in component_unmapped:
                                component_unmapped.remove(self.problem_data.n)
                             if len(component_unmapped) > 2 and 0 not in component_unmapped:
                                 ct_cutset = self.mdl.model_instance.sum(self.mdl.x[i, j] for (i, j) in get_cutset(component_unmapped, self.problem_data.E))
                                 ct = ct_cutset >= 2 * self.mdl.model_instance.sum(self.mdl.y[v, j] for j in component_unmapped)
                                 #print(self.mdl.y[v, j] for j in component_unmapped)
                                 ct_cpx = self.linear_ct_to_cplex(ct)
                                 self.add(ct_cpx[0], ct_cpx[1], ct_cpx[2])
                                 # solve a global min cut problem and if the value of the cut is less than 2 we have a violated cut
                                 
                                 
        # call funtion
        frac_edges = [(i, j) for (i, j) in self.problem_data.E if sol_x.get_value(self.mdl.x[i, j]) > 0.0000001 and sol_x.get_value(self.mdl.x[i, j]) < 0.999999]
        int_edges = [(i, j) for (i, j) in self.problem_data.E if sol_x.get_value(self.mdl.x[i, j]) >= 0.999999]
        
        print("Fractional edges:", frac_edges)
        print("Integer edges:", int_edges)
        
        # for component in components:
        #     for (i,j) in int_edges:
        #         if i or j in component:
        #             T.append(i,j)
        # if T.size()/2
        # Then add comb
        
        for component in components:
            component_unmapped = [vertices[i] for i in component]
            # Initialize T for the current component
            T = []
            for (i, j) in int_edges:
                if i in component_unmapped or j in component_unmapped:
                    T.append((i, j))
                    
            print(f"Component: {component}")
            print(f"Integer edges in component: {T}")
            
            
            # Check if T is large enough to be a potential handle
            if len(T) / 2 >= 1:  # Ensuring T has at least 2 edges to be valid
                print("T is a potential handle. Checking combinations.")
            
                
                # Construct the inequality: x(E(H)) + x(T) <= Σvi∈H yii + (|T| - 1)/2
                edges_in_component = [(i, j) for (i, j) in self.problem_data.E if i in component_unmapped and j in component_unmapped]
                #print(f"edges in component: {edges_in_component}")
                
                sum_x_EH = self.mdl.model_instance.sum(self.mdl.x[i, j] for (i, j) in edges_in_component)
                sum_x_T = self.mdl.model_instance.sum(self.mdl.x[i, j] for (i, j) in T)
                sum_y_H = self.mdl.model_instance.sum(self.mdl.y[i, i] for i in component_unmapped)
                
                inequality = sum_x_EH + sum_x_T <= sum_y_H + (len(T) - 1) / 2
                
                ct_cpx = self.linear_ct_to_cplex(inequality)
                self.add(ct_cpx[0], ct_cpx[1], ct_cpx[2])
                print(f"Added constraint: {inequality}")
                # if int_edges != []:
                #     exit()





