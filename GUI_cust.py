from Sheet import Sheet
import tkinter as tk
from tkinter.filedialog import askopenfilename
from stl import mesh
import numpy as np
from matplotlib import pyplot
from mpl_toolkits import mplot3d
from pathlib import Path

my_mesh_base = []


#GUI Initialization
root = tk.Tk()
root.geometry('700x500')
root.title("Origami GUI v0.2")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()
        self.figure = pyplot.figure() #figure to draw on

    def create_widgets(self):
        self.update_pl = tk.Button(self)
        self.update_pl["text"] = "Update Plot"
        self.update_pl["command"] = self.update_plot
        self.update_pl.grid(row=10, column=0)

            #loading removed for time
        #self.file_button = tk.Button(self)
        #self.file_button["text"] = "Open File"
        #self.file_button["command"] = self.open_file
        #self.file_button.grid(row=0, column=0)

            #Save buttons & filename input:
        self.save_stl_button = tk.Button(self)
        self.save_stl_button["text"] = "Save .stl"
        self.save_stl_button["command"] = self.save_stl
        self.save_stl_button.grid(row=0, column=1)

        self.save_fig_button = tk.Button(self)
        self.save_fig_button["text"] = "Save figure"
        self.save_fig_button["command"] = self.save_fig
        self.save_fig_button.grid(row=0, column=2)

            #removed because saving without string literals is finicky
        #self.lbl_savename= tk.Label(self, text="save as:")
        #self.lbl_savename.grid(row=0, column=3)
        #self.txt_savename = tk.Entry(self, width=20)
        #self.txt_savename.grid(row=0, column=4)




        #Row 1: mesh parameter input:
        self.lbl_format = tk.Label(self, text="Sheet Params:")
        self.lbl_format.grid(row=1, column=0)

        self.lbl_xLength = tk.Label(self, text="xlength:")
        self.lbl_xLength.grid(row=1, column=1)

        self.txt_xLength = tk.Entry(self, width=10)
        self.txt_xLength.grid(row=1, column=2)

        self.lbl_yLength = tk.Label(self, text="ylength:")
        self.lbl_yLength.grid(row=1, column=3)

        self.txt_yLength = tk.Entry(self, width=10)
        self.txt_yLength.grid(row=1, column=4)

        self.create_sheet_button = tk.Button(self)
        self.create_sheet_button["text"] = "Create Sheet"
        self.create_sheet_button["command"] = self.create_sheet
        self.create_sheet_button.grid(row=1, column=10)


        #Row 2: Fold parameter input:
        self.lbl_fold = tk.Label(self, text="Fold endpoints:")
        self.lbl_fold.grid(row=2, column=0)

        self.lbl_x1 = tk.Label(self, text="x1:")
        self.lbl_x1.grid(row=2, column=1)

        self.txt_x1 = tk.Entry(self, width=10)
        self.txt_x1.grid(row=2, column=2)

        self.lbl_y1 = tk.Label(self, text="y1:")
        self.lbl_y1.grid(row=2, column=3)

        self.txt_y1 = tk.Entry(self, width=10)
        self.txt_y1.grid(row=2, column=4)

        self.lbl_x2 = tk.Label(self, text="x2:")
        self.lbl_x2.grid(row=2, column=5)

        self.txt_x2 = tk.Entry(self, width=10)
        self.txt_x2.grid(row=2, column=6)

        self.lbl_y2 = tk.Label(self, text="y2:")
        self.lbl_y2.grid(row=2, column=7)

        self.txt_y2 = tk.Entry(self, width=10)
        self.txt_y2.grid(row=2, column=8)

        #Update equation based on inputs
        self.preview_button = tk.Button(self)
        self.preview_button["text"] = "Preview Fold"
        self.preview_button["command"] = self.preview_fold
        self.preview_button.grid(row=2, column=9)

        self.commit_button = tk.Button(self)
        self.commit_button["text"] = "Commit Fold"
        self.commit_button["command"] = self.commit_fold
        self.commit_button.grid(row=2, column=10)

        self.print_node_bool = tk.IntVar(value=1)
        self.check_button_node = tk.Checkbutton(self, text="plot nodes", variable=self.print_node_bool).grid(row=10, column=1)
        self.print_mesh_bool = tk.IntVar(value=1)
        self.check_button_mesh = tk.Checkbutton(self, text="plot mesh", variable=self.print_mesh_bool).grid(row=10, column=2)


        #Quit button
        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.quit_app)
        self.quit.grid(row=10, column=10)

    def quit_app(self):
        if tk.messagebox.askokcancel(title="Quit Warning", message="Are you sure you want to quit? Work will not be saved"):
            self.master.destroy()

    def preview_fold(self):
        print("Preview fold")
        x0 = float(self.txt_x1.get())
        x1 = float(self.txt_x2.get())
        y0 = float(self.txt_y1.get())
        y1 = float(self.txt_y2.get())
        self.sheet.preview([x0, x1], [y0, y1])
        print("now displaying fold")

    def commit_fold(self): #todo
        print("Committing Fold")
        x0 = float(self.txt_x1.get())
        x1 = float(self.txt_x2.get())
        y0 = float(self.txt_y1.get())
        y1 = float(self.txt_y2.get())

        self.sheet.addFold([x0, x1], [y0, y1])
        print("Fold Committed")


    def update_plot(self): #done
        #TODO link this to sheet.plot()
        #try:
        print("Plot Updating")
        self.sheet.updateMesh()
        self.sheet.figure = self.figure
        self.sheet.plot(self.print_node_bool.get(), self.print_mesh_bool.get())
        #except:
        #    tk.messagebox.showwarning("Update Plot","Failed to update plot")
        #else:
        print("Plot Updated")


    #def open_file(self): #Might take this out, limit user to generate a new sheet
    #    try:
    #        self.filename = askopenfilename() # show an "Open" dialog box and return the path to the selected file
    #        self.my_mesh_base =mesh.Mesh.from_file(self.filename)
    #    except:
    #        tk.messagebox.showwarning("Open file","Cannot open this file: \n(%s)" % self.filename)

    def save_stl(self): #Done

        try:
            self.sheet.mesh.save("MyOrigami.stl")
        except:
            tk.messagebox.showwarning("Save File",["Failed to save this file:", self.filename])
        else:
            print("file saved to ", "MyOrigami.stl")

    def create_sheet(self): #Done
        if tk.messagebox.askokcancel(title="Create Warning", message="Create sheet? Current sheet will be lost."):
            print("Creating", float(self.txt_xLength.get()), "x", float(self.txt_yLength.get()), " sheet")
            #try:
            self.sheet = Sheet(float(self.txt_xLength.get()), float(self.txt_yLength.get()))
            #except:
            #    tk.messagebox.showwarning("Create Sheet","Failed to create sheet")
            #else:
            print("Sheet Created")



    def update_equation(self): #TODO
        m = self.txt_m.get()
        b = self.txt_b.get()
        if (m == '' or b == ''):
            print("Invalid line - please enter valid m and b values")
        else:
            print("m = ", float(m), " b = ", float(b))



    def save_fig(self): #Done

        try:
            self.figure.savefig("MyOrigami.png", facecolor='w', bbox_inches = 'tight')
        except:
            tk.messagebox.showwarning("Save File",["Failed to save this file:", self.filename])

app = Application(master=root)

# start program
app.mainloop()
