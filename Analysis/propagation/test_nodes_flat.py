import numpy as np

def find_nodes_robust(xi_r, x_val):
    nodes_x = []
    
    # Iterate to find crossings and ignore flat zeros
    last_nonzero_sign = 0
    last_nonzero_idx = -1
    
    for i in range(len(xi_r)):
        val = xi_r[i]
        if val != 0:
            current_sign = np.sign(val)
            if last_nonzero_sign != 0 and current_sign != last_nonzero_sign:
                # Sign changed between last_nonzero_idx and i
                # Where is the node?
                if i - last_nonzero_idx == 1:
                    # Adjacent points, interpolate normally
                    x0, x1 = x_val[last_nonzero_idx], x_val[i]
                    y0, y1 = xi_r[last_nonzero_idx], xi_r[i]
                    x_node = x0 - y0 * (x1 - x0) / (y1 - y0)
                    nodes_x.append(x_node)
                else:
                    # There are exact zeros between last_nonzero_idx and i
                    # We can pick the exact zeros! But which one?
                    # The easiest is to say the node is exactly in the middle of the zero region,
                    # or simply pick the first exact zero.
                    # In stellar oscillations, an exact zero is usually a single point.
                    # If there's an underflow flat region, a single node at the midpoint is reasonable.
                    mid_idx = (last_nonzero_idx + i) // 2
                    nodes_x.append(x_val[mid_idx])
            
            last_nonzero_sign = current_sign
            last_nonzero_idx = i
            
    return nodes_x

x_val = np.array([0, 1, 2, 3, 4, 5])
xi_r = np.array([1, 0, 0, -1, 1, 1])

print("Robust:", find_nodes_robust(xi_r, x_val))

