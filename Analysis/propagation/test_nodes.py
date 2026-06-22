import numpy as np

def find_nodes_old(xi_r, x_val):
    crossings = np.where(np.diff(np.signbit(xi_r)))[0]
    nodes_x = []
    for i in crossings:
        x0, x1 = x_val[i], x_val[i+1]
        y0, y1 = xi_r[i], xi_r[i+1]
        if y1 - y0 != 0:
            x_node = x0 - y0 * (x1 - x0) / (y1 - y0)
            nodes_x.append(x_node)
    return nodes_x

def find_nodes_new(xi_r, x_val):
    crossings = np.where(xi_r[:-1] * xi_r[1:] < 0)[0]
    nodes_x = []
    for i in crossings:
        x0, x1 = x_val[i], x_val[i+1]
        y0, y1 = xi_r[i], xi_r[i+1]
        x_node = x0 - y0 * (x1 - x0) / (y1 - y0)
        nodes_x.append(x_node)
    
    exact_zeros = np.where(xi_r == 0)[0]
    for i in exact_zeros:
        nodes_x.append(x_val[i])
        
    return sorted(nodes_x)

x_val = np.array([0, 1, 2, 3])
xi_r = np.array([1, 0, -1, 1])

print("Old:", find_nodes_old(xi_r, x_val))
print("New:", find_nodes_new(xi_r, x_val))

xi_r2 = np.array([1, -0.0, 1, -1])
print("Old (-0.0):", find_nodes_old(xi_r2, x_val))
print("New (-0.0):", find_nodes_new(xi_r2, x_val))

