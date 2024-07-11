# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 10:37:20 2024

@author: katan
"""

import numpy as np
rnd = np.random
import math

class Data:
    def __init__(self, n_input, width_input, seed_input):
        
        self.n = n_input
        self.width = width_input
        self.seed = seed_input
        
    def create_data(self):
        rnd.seed(self.seed)
        self.V = range(self.n)
        self.E = [(i,j) for i in self.V for j in self.V if i>j]
        self.A = [(i,j) for i in self.V for j in self.V]
        self.loc = {i:(rnd.random()*self.width,rnd.random()*self.width) for i in self.V}
        self.c = {(i,j): math.hypot(self.loc[i][0]-self.loc[j][0],self.loc[i][1]-self.loc[j][1]) for (i,j) in self.E}
        self.a = {(i,j): 0.5*math.hypot(self.loc[i][0]-self.loc[j][0],self.loc[i][1]-self.loc[j][1]) for (i,j) in self.A}
        
        # self.V_prime = range(self.n)  # Include dummy vertex
        # self.E_prime = [(i, j) for i in self.V_prime for j in self.V_prime if i > j]
        # self.loc[self.n] = (self.width / 2, self.width / 2)  # Dummy vertex in the center
        # self.c_prime = {(i, j): math.hypot(self.loc[i][0] - self.loc[j][0], self.loc[i][1] - self.loc[j][1]) for (i, j) in self.E_prime}
        