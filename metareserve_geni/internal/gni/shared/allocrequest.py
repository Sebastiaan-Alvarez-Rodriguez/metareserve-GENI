from enum import Enum
import itertools

class AllocRequest(object):
    '''Object to contain GENI python2 reservation requests.'''
    def __init__(self):
        self.nodes = []


    def add(self, name, hw_type='c6525-25g', img='urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD'):
        '''Adds node to request. Note: The `name` of the node must be unique. Note: `name` may not contain '|'.
        Args:
            name: Used as node name. GENI will use this name as hostname for the spawned node.
            hw_type (optional str): Name of hardware node type to allocate.
            img (optional str): Name of image to deploy on hardware.'''
        name = str(name)
        if '|' in name:
            raise ValueError('Node name "{}" includes illegal character "|"!'.format(name))
        if any(x.isupper() for x in name):
            print('[WARNING] Node name "{}" contains uppercase letters. Transformed to lowercase, because GENI does not understand stuff otherwise.'.format(name))
        self.nodes.append(Node(name.lower(), hw_type, img))


    def list(self):
        '''Returns part of or all stored requested nodes, sorted by node name.'''
        return sorted(self.nodes, key=lambda x: x.name)


    def __str__(self):
        return '\n'.join(str(node) for node in self.list())


    def __len__(self):
        '''Returns total number of nodes in request.'''
        return len(self.nodes)


    @staticmethod
    def from_string(string):
        ar = AllocRequest()
        for y in string.split():
            ar.nodes.append(Node.from_string(y))
        return ar


class Node(object):
    '''Object to store individual node requests.'''
    def __init__(self, name, hw_type='c6525-25g', img='urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD'):
        self.name = name
        self.hw_type = hw_type
        self.img = img


    def __str__(self):
        return '|'.join(str(x) for x in (self.name, self.hw_type, self.img))


    @staticmethod
    def from_string(string):
        return Node(*string.split('|', 2))