# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 10:41:46 2024

@author: katan
"""
import igraph as ig
import matplotlib.pyplot as plt
import random
import math
import numpy as np
from scipy.spatial.distance import euclidean
from itertools import combinations


def get_edges(S,E):
    edges = [] 
    for (i,j) in E:
        #print (i,j)
        if i in S and j in S:
            edges.append((i,j))
    return edges

def map_edges(vertices,edges):
    # vertex_map = list(range(len(vertices)))
    edges_map = []
    for (i,j) in edges:
        edges_map.append((vertices.index(i),vertices.index(j)))
    return edges_map

def get_cutset(S,E):
    edges = []
    for (i,j) in E:
        if i in S and j not in S or i not in S and j in S:
            edges.append((i,j))
    return edges

def find_connected_components(model, solution, data):
    """
    Find connected components from the solution of the TSP model.
    
    Args:
    solution (docplex.mp.solution.Solution): The solution of the TSP model.
    E (list of tuples): List of edges.
    V (list): List of vertices.
    
    Returns:
    list of lists: Each sublist contains the nodes in one connected component.
    """
    # Build the graph from the solution
    sol = solution.get_value_dict(model.x)
    edges_in_solution = [(i, j) for (i, j) in data.E if sol[(i, j)] > 0.9]
    
    # Adjust vertex IDs to start from 0
    adjusted_edges = [(i, j) for (i, j) in edges_in_solution]
   
    # Create an igraph graph
    g = ig.Graph()
    g.add_vertices(len(data.V))  # Adding the number of vertices
    g.add_edges(adjusted_edges)
     
    # Get the connected components
    components = g.connected_components(mode='weak')
    
    # Extract the component membership list and adjust back to original IDs
    component_list = [[v for v in comp] for comp in components]
    
    return component_list

def plot_sol(data,model):
    plt.figure()
    for i in data.V:
        plt.scatter(data.loc[i][0],data.loc[i][1], c = 'black')
        plt.annotate(i, (data.loc[i][0]+2,data.loc[i][1]))
    for (i,j) in data.E:
        if model.x[i,j].solution_value > 0.9:
            plt.plot([data.loc[i][0], data.loc[j][0]], [data.loc[i][1], data.loc[j][1]], c = 'blue')
    for i in data.V:
        for j in data.V:
            if model.y[i,j].solution_value > 0.9:
                plt.plot([data.loc[i][0], data.loc[j][0]], [data.loc[i][1], data.loc[j][1]], c = 'red')
            
    plt.axis([0, data.width, 0, data.width])
    plt.grid()
    fig = plt.gcf()
    fig.set_size_inches(8, 8)
    
def generate_instance(V, alpha):
    # Step 1: Generate V vertices with coordinates in [0, 1000] x [0, 1000]
    vertices = np.random.randint(0, 1001, size=(V, 2))
    
    # Step 2: Calculate Euclidean distances and round up to nearest integer
    l_matrix = np.zeros((V, V), dtype=int)
    for i, j in combinations(range(V), 2):
        distance = np.ceil(euclidean(vertices[i], vertices[j]))
        l_matrix[i][j] = l_matrix[j][i] = int(distance)
    
    # Step 3: Define costs
    c_matrix = np.ceil(alpha * l_matrix)  # cij = ⌈lij⌉
    d_matrix = np.ceil((10 - alpha) * l_matrix) # dij = ⌈(10^α) * lij⌉
    np.fill_diagonal(d_matrix, 0)  # dii = 0 for all i in V
    
    return vertices, l_matrix, c_matrix, d_matrix
    
# def generate_vertices(V):
#     return [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(V)]

# def euclidean_distance(v1, v2):
#     return math.ceil(math.sqrt((v1[0] - v2[0]) ** 2 + (v1[1] - v2[1]) ** 2))

# def generate_distance_matrix(vertices):
#     V = len(vertices)
#     distance_matrix = [[0 if i == j else euclidean_distance(vertices[i], vertices[j]) for j in range(V)] for i in range(V)]
#     return distance_matrix

# def define_costs(distance_matrix, beta):
#     V = len(distance_matrix)
#     c = [[distance_matrix[i][j] for j in range(V)] for i in range(V)]
#     d = [[beta * distance_matrix[i][j] for j in range(V)] for i in range(V)]
#     for i in range(V):
#         d[i][i] = 0
#     return c, d

# def generate_instances(num_instances, vertices_range, betas):
#     all_instances = []
#     for V in vertices_range:
#         for beta in betas:
#             for _ in range(num_instances):
#                 vertices = generate_vertices(V)
#                 distance_matrix = generate_distance_matrix(vertices)
#                 c, d = define_costs(distance_matrix, beta)
#                 instance = {'V': V, 'beta': beta, 'vertices': vertices, 'distance_matrix': distance_matrix, 'c': c, 'd': d}
#                 all_instances.append(instance)
#     return all_instances

# def solve_instances(instances):
#     results = []
#     for instance in instances:
#         V = instance['V']
#         c = instance['c']
#         d = instance['d']
#         bac_algorithm = BranchAndCutAlgorithm(V, c, d)
#         result = bac_algorithm.solve()
#         results.append(result)
#     return results

# def run_tests():
#     vertex_counts = [50, 75, 100, 125, 150, 175, 200]
#     betas = [3, 5, 7, 9]
#     results = []
    
#     for V in vertex_counts:
#         for beta in betas:
#             for instance in range(10):  # Generate and solve 10 instances for each combination
#                 vertices = generate_vertices(V)
#                 cij, dij = calculate_costs(vertices, beta)
                
#                 start_time = time.time()
#                 result = branch_and_cut_algorithm(cij, dij, V)
#                 end_time = time.time()
                
#                 result['V'] = V
#                 result['beta'] = beta
#                 result['instance'] = instance
#                 result['time'] = end_time - start_time
                
#                 results.append(result)
#                 print(f"Finished instance {instance+1}/10 for V={V}, beta={beta}")

#     return results
