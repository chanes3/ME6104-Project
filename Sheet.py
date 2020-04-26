from stl import mesh
import numpy as np
from matplotlib import pyplot
from mpl_toolkits import mplot3d

class Sheet():
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
        self.mesh = mesh.Mesh(np.zeros(self.faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.faces):
            for j in range(3):
                self.mesh.vectors[i][j] = self.vertices[f[j],:]

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

    def undoFold(self): #TODO - implement undoFold if there is time
        pass

    def doFold(self,fold): #TODO -
        self.number_of_folds += 1
        pass

    def addFold(self, fold):
        self.fold_stack.append(fold)

    def popFold(self, fold):
        return self.fold_stack.pop()

    def plot(self):
        figure1 = pyplot.figure()
        figure1.suptitle('Custom Rotation of tessa_vase_filled.stl')
        axes1 = mplot3d.Axes3D(figure1)
        axes1.set_xlabel('$X$')
        axes1.set_ylabel('$Y$')
        axes1.set_zlabel('$Z$')
        axes1.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mesh.vectors))


    #inner class Fold:
    class Fold:
        def __init__(self, m, b):
            self.m = m
            self.b = b
