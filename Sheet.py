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

        node0.isEdge = True
        node1.isEdge = True
        node2.isEdge = True
        node3.isEdge = True


        self.nodes = [node0, node1, node2, node3]


        #self.vertices = np.array([
        #    node0.data,
        #    node1.data,
        #    node2.data,
        #    node3.data
        #])
        self.updateMesh()
        self.number_of_folds = 0
        self.fold_stack = []
        self.fold_stack_storage = []

    def description(self):
        return "Length = {}; Width = {}".format(self.length, self.width)

    def updateMesh(self):
        self.getLoops()
        #for i,val in enumerate(self.loops):
        #    print(i,",",val.labels)
        self.getVertices()
        self.getFaces()
        print("num faces:", len(self.faces))
        self.mesh = mesh.Mesh(np.zeros(self.faces.shape[0],dtype=mesh.Mesh.dtype))
        try:
            for i, f in enumerate(self.faces):
                for j in range(3):
                    self.mesh.vectors[i][j] = self.vertices[f[j],:]
        except:
            print("clean your vertices")

    def getVertices(self):
        temp = np.array([self.nodes[i].data for i in range(len(self.nodes))])
        self.vertices =temp

    def getFaces(self):
        self.faces = []
        faces = []
        for i in range(len(self.loops)):
            faces = self.loops[i].getFaces()
            for j in range(len(faces)):
                self.faces.append(faces[j])
        self.faces = np.array(self.faces)


    def getLoops(self):
        self.loops = []
        #check loops starting at every node
        for i in range(len(self.nodes)):
            temp =Loop(self.nodes[i])

            if not self.loops: #if loops is empty
                self.loops.append(temp)
            else:
                add_bool = True
                for i in range(len(self.loops)):
                    if not (not_intersect(temp.labels_sorted, self.loops[i].labels_sorted)):#if they're the same
                        add_bool = False
                if add_bool:
                    self.loops.append(temp)

    def undoFold(self): #TODO - implement undoFold if there is time
        pass

    def addFold(self, x, y):
        myfold = Fold(x,y)
        self.fold_stack.append(myfold)
        self.number_of_folds += 1
        ##check for intersection
        for i in range(len(self.loops)): #check each loop
            working_nodes = []

            for j in range (len(self.loops[i].line_segs)): #check each line seg in loop
                #print([i,j])
                line_seg = self.loops[i].line_segs[j]
                temp = crossCheck([x[0], x[1],line_seg[0], line_seg[1]], [y[0], y[1], line_seg[2], line_seg[3]])
                if not temp: #catch if lines don't cross
                    pass
                    #do nothing
                else:
                    #todo add logic for new nodes from the same fold being linked - HOW TO ORDER NEW NODES????
                    #add nodes where intersection happens
                    #self.addNode(temp)
                    newlabel = len(self.nodes)
                    node = Node([temp[0], temp[1], 0], newlabel)
                    if j == len(self.loops[i].line_segs)-1: #loop index so node 0 isn't left out
                        j2 = 0
                    else:
                        j2 = j+1

                    exists = node.data == self.loops[i].nodes[j].data or node.data == self.loops[i].nodes[j2].data

                    if (exists): #if node already exists as the first node it's linked to
                        if node.data == self.loops[i].nodes[j].data:
                            node = self.loops[i].nodes[j]
                            if node not in working_nodes:
                                working_nodes.append(node)

                        else: #already exists as 2nd node
                            node = self.loops[i].nodes[j2]
                            if node not in working_nodes:
                                working_nodes.append(node)
                    else: #doesn't exist - splice it and remove connections it destroys
                        self.addNode(node)
                        if node not in working_nodes:
                            working_nodes.append(node)
                        #remove the newly destroyed connections from each of the other 2 nodes
                        self.loops[i].nodes[j].removeConnect(self.loops[i].nodes[j2])
                        self.loops[i].nodes[j2].removeConnect(self.loops[i].nodes[j])


                        #add connections, it's ok if its the same node or if connection already there, addConnect handles it
                        node.addConnect(self.loops[i].nodes[j])
                        self.loops[i].nodes[j].addConnect(node)
                        node.addConnect(self.loops[i].nodes[j2])
                        self.loops[i].nodes[j2].addConnect(node)



            #add connections, it's ok if they already have these connections, addConnect takes care of it
            working_nodes[1].addConnect(working_nodes[0])
            working_nodes[0].addConnect(working_nodes[1])

        self.doFold()

    def doFold(self):
        pass
        #flip around fold line
        #TODO HOW TO CHOOSE WHICH SIDE TO FLIP?
        #CHeck angle relative to a fixed point on fold line to differentiate each line, choose positive???

    def addNode(self, node):
        if node not in self.nodes:
            self.nodes.append(node)

    def popFold(self, fold):
        temp = self.fold_stack.pop()
        self.fold_stack_storage.append(temp)

    def preview(self, x, y):
        x = np.linspace(x[0], x[1], 100)
        y = np.linspace(y[0], y[1], 100)
        z = np.linspace(0, 0, 100)
        self.axes.plot(x, y, z, "r", zorder = 2)
        pyplot.show()


    def plot(self, print_node = False, print_mesh = False):
        self.axes = mplot3d.Axes3D(self.figure)
        self.axes.set_xlabel('$X$')
        self.axes.set_ylabel('$Y$')
        self.axes.set_zlabel('$Z$')

        if print_mesh:
            self.axes.add_collection3d(mplot3d.art3d.Poly3DCollection(self.mesh.vectors))

        scale = self.mesh.points.flatten('F')

        if print_node:
            x = np.array([self.nodes[i].data[0] for i in range(len(self.nodes))])
            y = np.array([self.nodes[j].data[1] for j in range(len(self.nodes))])
            z = np.array([self.nodes[k].data[2] for k in range(len(self.nodes))])

            self.axes.plot(x, y, z, 'rx')
        self.axes.auto_scale_xyz(scale, scale, scale)
        pyplot.show()

class Node:
    #Modified based on:https://www.geeksforgeeks.org/doubly-linked-list/
    def __init__(self, data = None, label = None, connected = None):
        self.data = data #[x, y, z] position of Node


        if connected != None:
            self.connected = connected
        else:
            self.connected = [] #nodes that it is connected to
        self.label = label #for indexing relative to the overall 'web'
        self.prev = None
        self.next = None
        self.isEdge = None

    def __repr__(self):
        return str(self.label)

    def addConnect(self, cn): #add node
        if cn not in self.connected and cn != self:
            self.connected.append(cn)

    def removeConnect(self, rm): #remove node
        if rm in self.connected:
            self.connected.remove(rm)
        else:
            print("Remove connection attempted for a node that wasn't connected")

    def translate(self, x, y, z):
        self.data = [self.data[0] + x, self.data[1]+y, self.data[2] + z]



    def rotateAxis(self, axis, angle):
        #angle + ccw looking down axis (from tail to tip - like an arrow)
        #axis = 2 [x,y,z] points
        #http://paulbourke.net/geometry/rotate/
        #(1) translate space so that the rotation axis passes through the origin
        #(2) rotate space about the x axis so that the rotation axis lies in the xz plane
        #(3) rotate space about the y axis so that the rotation axis lies along the z axis
        #(4) perform the desired rotation by theta about the z axis
        #(5) apply the inverse of step (3)
        #(6) apply the inverse of step (2)
        #(7) apply the inverse of step (1)
        axis_point1 = axis[[0, 2, 4]]
        axis_point2 = axis[[1, 3, 5]]
        #step 1:
        self.translate(-axis_point1) #set axis_point1 to [0, 0, 0] via translation
        #step 2:
        angle_step2 = math.degrees(np.arctan(self.data[1]/self.data[2]))
        self.data = self.data*rotation_matrix(angle_step2, 0)
        #step 3:
        theta_step3 = math.degrees(np.arctan(self))

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
        ind = 0
        first = True
        print("---------")
        while node is not None and node not in self.nodes: #keep going until the loop stops or repeats
            if first == True:
                first = False
            #print(ind)
            ind +=1
            self.nodes.append(node)
            self.labels.append(node.label)
            self.labels_sorted.append(node.label)

            node.next = node.getNextRight()
            try:
                self.line_segs.append([node.data[0], node.next.data[0], node.data[1], node.next.data[1]])
            except:
                print("Clean Yer nodes (nodes didn't have a next or the data was empty)")
            print(self.labels)
            temp = node
            node = node.next
            node.prev = temp

        node.prev = temp #prev for initial node
        self.labels_sorted.sort()


    def __repr__(self):
        return np.array(self.nodes)

    def getFaces(self):
        primary_node = self.nodes[0]
        temp = [[self.nodes[i+1].label, primary_node.label, self.nodes[i+2].label] for i in range(len(self.nodes)-2)]
        arr_out = temp


        #print(np.array(temp))
        return temp



class Fold:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.nodes_affected = []
        self.transformation = []
        self.transformation_inverse = []

def rotation_matrix(theta, axis, active=False):
        #https://mail.python.org/pipermail/numpy-discussion/2017-January/076407.html
        """Generate rotation matrix for a given axis

        Parameters
        ----------

        theta: numeric, optional
            The angle (degrees) by which to perform the rotation.  Default is
            0, which means return the coordinates of the vector in the rotated
            coordinate system, when rotate_vectors=False.
        axis: int, optional
            Axis around which to perform the rotation (x=0; y=1; z=2)
        active: bool, optional
            Whether to return active transformation matrix.

        Returns
        -------
        numpy.ndarray
        3x3 rotation matrix
        """
        theta = np.radians(theta)
        if axis == 0:
            R_theta = np.array([[1, 0, 0],
                                [0, np.cos(theta), -np.sin(theta)],
                                [0, np.sin(theta), np.cos(theta)]])
        elif axis == 1:
            R_theta = np.array([[np.cos(theta), 0, np.sin(theta)],
                                [0, 1, 0],
                                [-np.sin(theta), 0, np.cos(theta)]])
        else:
            R_theta = np.array([[np.cos(theta), -np.sin(theta), 0],
                                [np.sin(theta), np.cos(theta), 0],
                                [0, 0, 1]])
        if active:
            R_theta = np.transpose(R_theta)
        return R_theta

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
    x_interval1 = [min(x[0], x[1]), max(x[0], x[1])]
    x_interval2 = [min(x[2], x[3]), max(x[2], x[3])]
    y_interval1 = [min(y[0], y[1]), max(y[0], y[1])]
    y_interval2 = [min(y[2], y[3]), max(y[2], y[3])]

    if (x_interval1[1] < x_interval2[0]) and (x_interval2[0] < x_interval1[0]): #if the line segments don't share x values
        return False

    if (y_interval1[1] < y_interval2[0]) and (y_interval2[0] < y_interval1[0]): #if the line segments don't share y values
        return False

    #calculate slopes
    if (x_interval1[0] == x_interval1[1]): #check for vertical lines
        x_out = x_interval1[0] #if vertical, we know the x value
        if (x[3] != x[2]): #if lines aren't parallel
            m2 = (y[3] - y[2])/(x[3] - x[2])
            b2 = y[2]-m2*x[2]
            y_out = m2*x_out + b2
        else:
            return False


    elif (x_interval2[0] == x_interval2[1]): #check for vertical lines
        x_out = x_interval2[0] #if vertical, we know the x value
        if (x[1] != x[0]): #if lines aren't parallel
            m1 = (y[1] - y[0])/(x[1] - x[0])
            b1 = y[0]-m1*x[0]
            y_out = m1*x_out + b1
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


        #make sure outputted point is in the range (gets lost by equations otherwise)
    if (x_out <x_interval1[0] or x_out < x_interval2[0]) or (x_out >x_interval1[1] or x_out > x_interval2[1]):
        return False
    if (y_out <y_interval1[0] or y_out < y_interval2[0]) or (y_out >y_interval1[1] or y_out > y_interval2[1]):
        return False

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

