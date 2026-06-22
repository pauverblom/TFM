import numpy as np

def find_nodes_vectorized(xi_r, x_val):
    nodes_x = []
    nonzero_idx = np.nonzero(xi_r)[0]
    
    if len(nonzero_idx) > 0:
        xi_nonzero = xi_r[nonzero_idx]
        x_nonzero = x_val[nonzero_idx]
        
        sign_changes = np.where(np.sign(xi_nonzero[:-1]) != np.sign(xi_nonzero[1:]))[0]
        
        for idx in sign_changes:
            i1 = nonzero_idx[idx]
            i2 = nonzero_idx[idx+1]
            
            if i2 - i1 == 1:
                x0, x1 = x_val[i1], x_val[i2]
                y0, y1 = xi_r[i1], xi_r[i2]
                x_node = x0 - y0 * (x1 - x0) / (y1 - y0)
                nodes_x.append(x_node)
            else:
                mid_idx = (i1 + i2) // 2
                nodes_x.append(x_val[mid_idx])
    return nodes_x

print(find_nodes_vectorized(np.array([-1, 0, 1]), np.array([0, 1, 2])))
print(find_nodes_vectorized(np.array([-1, -0.0, 1]), np.array([0, 1, 2])))
print(find_nodes_vectorized(np.array([-1, 0, 0, 1]), np.array([0, 1, 2, 3])))
print(find_nodes_vectorized(np.array([-1, 0, -1]), np.array([0, 1, 2])))
print(find_nodes_vectorized(np.array([1, 1, 1]), np.array([0, 1, 2])))

