# -*- coding: utf-8 -*-
"""
Created on Tue Apr 12 10:32:52 2022

@author: 20771401
"""

from DataClass import Data
from Model import MyModel
from helper import *
from Callback import Callback_lazy, Callback_user
#from Callback_yii import Callback_lazy, Callback_user
import igraph as ig
#%% Input data

n = 40
dataset = 1
width = 100

p  = Data(n,width,dataset)
p.create_data()

mdl = MyModel("RSP",p)

cb_lazy = mdl.model_instance.register_callback(Callback_lazy)
cb_lazy.mdl = mdl
cb_lazy.problem_data = p
cb_lazy.num_calls = 0

cb_user = mdl.model_instance.register_callback(Callback_user)
cb_user.mdl = mdl
cb_user.problem_data = p
cb_user.num_calls = 0

solution = mdl.model_instance.solve(log_output=True)

plot_sol(p,mdl)



#%% Components

#sol = solution.get_value_dict(x)
#x_solution = solution.get_value_dict(x)
#components = [[7,1,6,9,5,8],[2,4,10,3]]

#for component in components: 
#    mdl.add_constraint(mdl.sum(x[i,j] for (i,j) in get_cutset(component,E))>=2)
    
#solution = mdl.solve(log_output = True)
#print(solution)
#%% Connected Components


#%%

# # Initial solve to get the solution
# solution = mdl.solve(log_output=True)
# component_list = find_connected_components(solution, E, V)
# while len(component_list) > 1:
#     for component in component_list: 
#         mdl.add_constraint(mdl.sum(x[i,j] for (i,j) in get_cutset(component, E)) >= 2)
        
#     solution = mdl.solve(log_output=True)
    
#     # Find the connected components
#     component_list = find_connected_components(solution, E, V)

# # Add the constraints for each component
 


#%% Output

