#python3
# generate data graph with clique

import argparse
import random
from pathlib import Path

def commandParser():
    parser = argparse.ArgumentParser(description='Generate data graph with clique')
    parser.add_argument('--nodes', type=int, help='number of nodes')
    parser.add_argument('--output', type=Path, help='output file name', required=True)
    parser.add_argument('--vertex-labels', type=int, help='number of vertex labels', default=1)
    parser.add_argument('--edge-labels', type=int, help='number of edge labels', default=1)
    parser.add_argument('--bidirectional', action='store_false', help='generate bidirectional graph')
    parser.add_argument('--seed', type=int, help='random seed', default=0)

    return parser.parse_args()

def main(args):
    number_of_nodes = args.nodes
    # reset random seed
    random.seed(args.seed)
    def node_label():
        return random.randint(0, args.vertex_labels-1)
    def edge_label():
        return random.randint(0, args.edge_labels-1)

    with open(args.output, 'w') as f:
        f.write(f'# t 1\n')
        for i in range(0, number_of_nodes):
            f.write(f'v {i} {node_label()}\n')
        for i in range(0, number_of_nodes):
            for j in range(i+1, number_of_nodes):
                f.write(f'e {i} {j} {edge_label()}\n')
                if args.bidirectional:
                    f.write(f'e {j} {i} {edge_label()}\n')


if __name__ == '__main__':
    args = commandParser()
    main(args)

