from stl import mesh
import numpy as np

class Sheet(mesh.Mesh):
    def __init__(self, length, width):
        self.length = length
        self.width = width
        self.vertices = np.array([
            [0, 0, 0],
            [self.length, 0, 0],
            [0, self.width, 0],
            [self.length, self.width, 0]
        ])
        self.faces = np.array([
            [0, 1, 2],
            [3, 1, 2]
        ])
        self.number_of_folds = 0
        self.fold_stack = []
        self.fold_stack_storage = []

    def description(self):
        return "Length = {}; Width = {}".format(self.length, self.width)

    #def getLength(self):
     #   return self.length

    def changeLength(self, length):
        self.length = length

    def changeWidth(self, width):
        self.width = width

    def doFold(self,fold):
        pass

    def addFold(self, fold):
        self.fold_stack.append(fold)

    def popFold(self, fold):
        return self.fold_stack.pop()


    #inner class Fold:
    class Fold:
        def __init__(self, m, b):
            self.m = m
            self.b = b
