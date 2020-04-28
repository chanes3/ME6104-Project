from stl import mesh
import numpy as np
import math
from matplotlib import pyplot
from mpl_toolkits import mplot3d

class Sheet(mesh.Mesh):
    def __init__(self, length, width):
        self.length = length
        self.width = width
        node0 = Node([0, 0, 0], 0)
        node1 = Node([self.length, 0, 0], 1)
        node2 = Node([0, self.width, 0], 2)
        node3 = Node([self.length, self.width, 0], 3)
        node0.connected = [node1, node2]
        node1.connected = [node0, node3]
        node2.connected = [node0, node3]
        node3.connected = [node2, node1]
        self.nodes = [node0, node1, node2, node3]

        self.getLoops()
        for i,val in enumerate(self.loops):
            print(i,",",val.labels)

        self.vertices = np.array([
            node0.data,
            node1.data,
            node2.data,
            node3.data
        ])
        self.getFaces()
        self.updateMesh()
        self.number_of_folds = 0
        self.fold_stack = []
        self.fold_stack_storage = []

    def description(self):
        return "Length = {}; Width = {}".format(self.length, self.width)

    def updateMesh(self):
        self.mesh = mesh.Mesh(np.zeros(self.faces.shape[0],dtype=mesh.Mesh.dtype))
        for i, f in enumerate(self.faces):
            for j in range(3):
                self.mesh.vectors[i][j] = self.vertices[f[j],:]

    def getFaces(self):

        self.faces = self.loops[0].getFaces()


    def getLoops(self):
        self.loops = []
        arr_temp = [None] * len(self.nodes)
        arr_out = [None] *len(self.nodes)
        loop_count = 0
        #check loops starting at every node
        for i in range(len(self.nodes)):
            temp =Loop(self.nodes[i])

            if not self.loops: #if loops is empty
                self.loops.append(temp)
                loop_count +=1
            else:
                add_bool = True
                for i in range(loop_count):
                    if not (not_intersect(temp.labels_sorted, self.loops[i].labels_sorted)):#if they're the same
                        add_bool = False
                if add_bool:
                    self.loops[loop_count] = temp
                    loop_count +=1

    def undoFold(self): #TODO - implement undoFold if there is time
        pass

    def addFold(self, x, y):
        myfold = Fold(x,y)
        self.fold_stack.append(myfold)
        self.number_of_folds += 1

        ##check for intersection
        for i in range(len(self.loops)): #check each loop
            for j in range (len(self.loops[i].line_segs)): #check each line seg in loop
                line_seg = self.loops[i].line_segs[j]
                temp = self.loops.crossCheck([x,line_seg[1:2]], [y, line_seg[3:4]])
                if not temp:
                    pass
                    #do nothing
                else:
                    #add nodes where intersection happens
                    #self.addNode(temp)

                    pass

        self.doFold()

    def doFold(self):
        pass
        #flip around fold line


    def popFold(self, fold):
        temp = self.fold_stack.pop()
        self.fold_stack_storage.append(temp)

    def plot(self):
        figure1 = pyplot.figure()
        figure1.suptitle('Custom Rotation of tessa_vase_filled.stl')
        axes1 = mplot3d.Axes3D(figure1)
        axes1.set_xlabel('$X$')
        axes1.set_ylabel('$Y$')
        axes1.set_zlabel('$Z$')
        axes1.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mesh.vectors))

class Node:
    #Modified based on:https://www.geeksforgeeks.org/doubly-linked-list/
    def __init__(self, data = None, label = None, connected = None):
        self.data = data #[x, y, z] position of Node
        self.connected = connected #nodes that it is connected to
        self.label = label #for indexing relative to the overall 'web'
        self.prev = None
        self.next = None

    def __repr__(self):
        return str(self.label)

    def addConnect(self, cn): #add node
        self.connected.append(cn)

    def removeConnect(self, rm): #remove node
        self.connected.remove(rm)

    def getNextRight(self):
        #gets the next node, prioritizing going in the tightest clockwise circle
        #used to divide sheet into different parts so faces can be attached
        temp_connected = self.connected
        if self.connected is None:
            return False #node not connected to anything
        elif len(self.connected) > 1 : #get tightest clockwise loop
            #https://www.geeksforgeeks.org/python-maximum-minimum-elements-position-list/
            #angles relative to (1, 0) (x, y)
            ang = [None] * len(self.connected)

            for i in range(len(self.connected)):
                #compare each angle to +x-axis
                ang[i] = angleBetSeg([0, 1, self.data[0], (self.connected[i]).data[0]], [0, 0, self.data[1], self.connected[i].data[1]])

            if self.prev == None: #semi-arbitrarily chosen, just needs to be consistent

                return self.connected[ang.index(max(ang))]
            else:
                ang_rel = [None] * len(self.connected)

                for i in range(len(self.connected)):
                    #compare each angle to prev line seg
                    ang_rel[i] = angleBetSeg([self.prev.data[0], self.data[0], self.data[0], self.connected[i].data[0]], [self.prev.data[1], self.data[1], self.data[1], self.connected[i].data[1]])
                node_out = self.connected[ang_rel.index(min(ang_rel))]
                if node_out == self.prev: #dont allow it to go between 2 points repeatedly
                    temp = ang_rel
                    old_ind = ang_rel.index(min(ang_rel))
                    temp.pop(old_ind)
                    new_ind = ang_rel.index(max(ang_rel))
                    if new_ind >= old_ind:
                        new_ind +=1
                    node_out = self.connected[new_ind]

                return node_out

class Loop: #a group of nodes that creates a circuit that goes back to the start
    def __init__(self, head):
        self.head = head
        node = self.head
        self.nodes = []
        self.labels = []
        self.labels_sorted = []
        self.line_segs = []

        first = True
        while node is not None and (first or node is not head): #keep going until the loop stops or repeats
            if first == True:
                first = False

            self.nodes.append(node)
            self.labels.append(node.label)
            self.labels_sorted.append(node.label)

            node.next = node.getNextRight()

            self.line_segs.append([node.data[0], node.next.data[0], node.data[1], node.next.data[1]])

            temp = node
            node = node.next
            node.prev = temp

        node.prev = temp #prev for initial node
        self.labels_sorted.sort()


    def getFaces(self):
        primary_node = self.nodes[0]
        temp = [[self.nodes[i+1].label, primary_node.label, self.nodes[i+2].label] for i in range(len(self.nodes)-2)]
        arr_out = temp


        #print(np.array(temp))
        return np.array(temp)



class Fold:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def angleBetSeg(x, y):
    #angleBetSeg(x, y)
    #takes in 2 line segments in the x-y plane and outputs the angle between them (positive = ccw, negative = cw)
    #x = [x0, x1, x2, x3]; y = [y0, y1, y2, y3]
    #https://www.mathworks.com/matlabcentral/answers/180131-how-can-i-find-the-angle-between-two-vectors-including-directional-information
    x1 = (x[1] - x[0])
    x2 = (x[3] - x[2])
    y1 = (y[1] - y[0])
    y2 = (y[3] - y[2])

    ang_out = np.arctan2(x1*y2-y1*x2,x1*x2+y1*y2)
    return ang_out

def angUnsign(x, y):
    #angleBetSeg(x, y)
    #takes in 2 line segments in the x-y plane and outputs the angle between them (positive = ccw, negative = cw)
    #x = [x0, x1, x2, x3]; y = [y0, y1, y2, y3]
    #https://www.mathworks.com/matlabcentral/answers/180131-how-can-i-find-the-angle-between-two-vectors-including-directional-information
    x1 = (x[1] - x[0])
    x2 = (x[3] - x[2])
    y1 = (y[1] - y[0])
    y2 = (y[3] - y[2])

    vec1 = [x1, y1]
    vec2 = [x2, y2]
    uv1 = vec1/np.linalg.norm(vec1)
    uv2 = vec2/np.linalg.norm(vec2)
    dot_prod = np.dot(uv1, uv2)
    angle = np.arccos(dot_prod)


def crossCheck(x, y):
    #crossCheck(x, y)
    #takes in 2 line segments in the x-y plane and outputs the point where they cross, if they cross
    #x = [x0, x1, x2, x3]; y = [y0, y1, y2, y3]
    #returns a vector containing the x, y coords of the intersection
    #if there is no intersection, returns false
    #https://stackoverflow.com/questions/3838329/how-can-i-check-if-two-segments-intersect
    x_interval1 = [np.min(x[0], x[1]), np.max(x[0], x[1])]
    x_interval2 = [np.min(x[2], x[3]), np.max(x[2], x[3])]
    y_interval1 = [np.min(y[0], y[1]), np.max(y[0], y[1])]
    y_interval2 = [np.min(y[2], y[3]), np.max(y[2], y[3])]

    if (x_interval1[1] < x_interval2[0]) and (x_interval2[0] < x_interval1[0]): #if the line segments don't share x values
        return False

    if (y_interval1[1] < y_interval2[0]) and (y_interval2[0] < y_interval1[0]): #if the line segments don't share y values
        return False

    #calculate slopes
    if (x_interval1[0] == x_interval1[1]): #check for vertical lines
        x_out = x_interval1[0] #if vertical, we know the x value
        if (x[3] != x[2]):
            m2 = (y[3] - y[2])/(x[3] - x[2])
            b2 = y[2]-m2*x[2]
            y_out = m2*x_out + b2
            return [x_out, y_out]
        else:
            return False


    elif (x_interval2[0] == x_interval2[1]): #check for vertical lines
        x_out = x_interval2[0] #if vertical, we know the x value
        if (x[3] != x[2]):
            m1 = (y[1] - y[0])/(x[1] - x[0])
            b1 = y[0]-m1*x[0]
            y_out = m1*x_out + b1
            return [x_out, y_out]
        else:
            return False

    else:
        m1 = (y[1] - y[0])/(x[1] - x[0])
        m2 = (y[3] - y[2])/(x[3] - x[2])
        if m1==m2:
            return False #parallel lines
        b1 = y[0]-m1*x[0]
        b2 = y[2]-m2*x[2]

        #solving for final point
        x_out = (b2-b1)/(m1-m2)
        y_out = m1*x_out + b1
        return [x_out, y_out]

def intersect(list1, list2):
    #https://www.geeksforgeeks.org/python-intersection-two-lists/
     # Use of hybrid method
    temp = set(list2)
    lst3 = [value for value in list1 if value in temp]
    return lst3

def not_intersect(list1, list2):
    #https://www.geeksforgeeks.org/python-intersection-two-lists/
     # Use of hybrid method
    if len(list2)>len(list1):
        temp = list2
        list2 = list1
        list1 = temp
    temp = set(list2)
    lst3 = [value for value in list1 if value not in temp]
    return lst3


#print(angleBetSeg([0, -1, -1, 0], [0, 1, 1, 2])) #-pi/2


#node0 = Node([0, 0, 0], 0)
#node1 = Node([1, 0, 0], 1)
#node2 = Node([0, 2, 0], 2)
#node3 = Node([1, 2, 0], 3)
#node0.connected = [node1, node2]
#node1.connected = [node0, node3]
#node2.connected = [node0, node3]
#node3.connected = [node2, node1]
#loop1 = Loop(node0)
#print(loop1.labels)

