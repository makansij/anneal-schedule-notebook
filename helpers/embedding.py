#    Copyright 2018 D-Wave Systems Inc.

u0 = [0, 1, 1, 1, 2, 2, 2, 3, 5,  6,  8,  9,  9,  9,  10, 10, 10, 11]
v0 = [5, 5, 7, 6, 4, 5, 6, 6, 13, 14, 13, 13, 14, 15, 12, 13, 14, 14]

def direct_embedding(nodelist, edgelist, cn=16):
    if cn != 16:
        raise ValueError("Currently enabled only on D-Wave 2000Q systems.")    
    for row in range(cn):
        for column in range(cn-1):
            offset = 8*cn*row + 8*column
            u = [offset + val for val in u0]
            v = [offset + val for val in v0]
            edges = set(zip(u, v))
            nodes = set(range(offset, offset+16))
            if not edges.issubset(edgelist) or not nodes.issubset(nodelist):
                print("Missing qubits in row {}, column {}. Trying next Chimera unit cells".format(row, column))
            else:
                print("Valid minor-embedding found for row {}, column {}.".format(row, column))
                return(nodes, edges)
