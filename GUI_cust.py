import Sheet
import tkinter as tk
from tkinter.filedialog import askopenfilename
from stl import mesh
import numpy as np
from matplotlib import pyplot
from mpl_toolkits import mplot3d

my_mesh_base = []


#GUI Initialization
root = tk.Tk()
root.geometry('700x500')
root.title("Origami GUI v0.1")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        #self.number = app_number
        self.create_widgets()
        self.figure = pyplot.figure() #figure to draw on
        self.filename = ""


    def create_widgets(self):
        self.update_pl = tk.Button(self)
        self.update_pl["text"] = "Update Plot"
        self.update_pl["command"] = self.update_plot
        self.update_pl.grid(row=10, column=0)

        self.file_button = tk.Button(self)
        self.file_button["text"] = "Open File"
        self.file_button["command"] = self.open_file
        self.file_button.grid(row=0, column=0)
            #Save buttons & filename input:
        self.save_stl_button = tk.Button(self)
        self.save_stl_button["text"] = "Save .stl"
        self.save_stl_button["command"] = self.save_stl
        self.save_stl_button.grid(row=0, column=1)

        self.save_fig_button = tk.Button(self)
        self.save_fig_button["text"] = "Save figure"
        self.save_fig_button["command"] = self.save_fig
        self.save_fig_button.grid(row=0, column=2)

        self.lbl_savename= tk.Label(self, text="save as:")
        self.lbl_savename.grid(row=0, column=3)
        self.txt_savename = tk.Entry(self, width=20, textvariable = "filenameHere (.stl and .fig will be added automatically)")
        self.txt_savename.grid(row=0, column=4)




        #Row 1: mesh parameter input:
        self.lbl_format = tk.Label(self, text="Sheet Params:")
        self.lbl_format.grid(row=1, column=0)

        self.lbl_x = tk.Label(self, text="xlength:")
        self.lbl_x.grid(row=1, column=1)

        self.txt_x = tk.Entry(self, width=10)
        self.txt_x.grid(row=1, column=2)

        self.lbl_y = tk.Label(self, text="ylength:")
        self.lbl_y.grid(row=1, column=3)

        self.txt_y = tk.Entry(self, width=10)
        self.txt_y.grid(row=1, column=4)

        self.lbl_numPts = tk.Label(self, text="# of points:")
        self.lbl_numPts.grid(row=1, column=5)

        self.txt_numPts = tk.Entry(self, width=10)
        self.txt_numPts.grid(row=1, column=6)

        self.create_sheet_button = tk.Button(self)
        self.create_sheet_button["text"] = "Create Sheet"
        self.create_sheet_button["command"] = self.create_sheet
        self.create_sheet_button.grid(row=1, column=10)


        #Row 2: Fold parameter input:
        self.lbl_fold = tk.Label(self, text="y = mx+b")
        self.lbl_fold.grid(row=2, column=0)

        self.lbl_m = tk.Label(self, text="m:")
        self.lbl_m.grid(row=2, column=1)

        self.txt_m = tk.Entry(self, width=10)
        self.txt_m.grid(row=2, column=2)

        self.lbl_b = tk.Label(self, text="b:")
        self.lbl_b.grid(row=2, column=3)

        self.txt_b = tk.Entry(self, width=10)
        self.txt_b.grid(row=2, column=4)

        #Update equation based on inputs
        self.update_eqn = tk.Button(self)
        self.update_eqn["text"] = "Update Equation"
        self.update_eqn["command"] = self.update_equation
        self.update_eqn.grid(row=2, column=5)



        #Quit button
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.quit_app)
        self.quit.grid(row=10, column=10)

    def quit_app(self):
        if tk.messagebox.askokcancel(title="Quit Warning", message="Are you sure you want to quit? Work will not be saved"):
            self.master.destroy()

    def update_plot(self):
        print("Plot Updating")
        #plot_mesh(my_mesh_base)

        print("Plot Updated")


    def open_file(self):
        try:
            self.filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
            self.my_mesh_base =mesh.Mesh.from_file(self.filename)
        except:
            tk.messagebox.showwarning("Open file","Cannot open this file: \n(%s)" % self.filename)


    def save_stl(self): #Yi
        print("save stl")

    def create_sheet(self):
        if tk.messagebox.askokcancel(title="Create Warning", message="Create sheet? Current sheet will be lost."):
            print("Creating", float(self.txt_x.get()), "x", float(self.txt_y.get()), "sheet with:", self.txt_numPts.get(), "points")

    def update_equation(self):
        m = self.txt_m.get()
        b = self.txt_b.get()
        if (m == '' or b == ''):
            print("Invalid line - please enter valid m and b values")
        else:
            print("m = ", float(m), " b = ", float(b))


    def plot_mesh(self, mesh):
        figure1 = pyplot.figure()
        figure1.suptitle('My Origami')
        axes = mplot3d.Axes3D(figure1)
        axes.set_xlabel('$X$')
        axes.set_ylabel('$Y$')
        axes.set_zlabel('$Z$')
        axes.add_collection3d(mplot3d.art3d.Poly3DCollection(mesh.vectors))
        scale = mesh.points.flatten('F')
        axes.auto_scale_xyz(scale, scale, scale)
        pyplot.show()

    def save_fig(self):
        try:
            self.figure.savefig(self.txt_savename, facecolor='w', bbox_inches = 'tight')
            self.filename = self.txt_savename
        except:
            tk.messagebox.showwarning("Save file Error","Cannot save this file: \n(%s)" % self.filename)

app = Application(master=root)

# start program
app.mainloop()
