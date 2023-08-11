import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Menu
#Regular expressions
import re as rexs
#19Oct
from PIL import Image, ImageTk
import os
from tkinter import filedialog
#import sv_ttk #Themes from https://github.com/rdbende/Sun-Valley-ttk-theme
from sympy import *

##--------------------------------------------------------

# Open equations
def fileOpen():
    text_Box.delete("1.0", "end")
    tf = filedialog.askopenfilename(
        initialdir=os.getcwd(), 
        title="Open model file", 
        filetypes=(("Text Files", "*.txt"),)
        )
    tf = open(tf)  # or tf = open(tf, 'r')
    data = tf.read()
    text_Box.insert(tk.END, data)
    tf.close()

#Save equations
def saveIntegration():
    # Open the save file dialog
    filename = filedialog.asksaveasfilename(defaultextension=".txt")
    
    if filename is not None:  # asksaveasfilename returns `None` if dialog closed with "cancel".
        # Get text from the text widget
        all_text = text_Box.get("1.0", tk.END+"-1c")  # gets all text from the textbox
        with open(filename, 'w') as file:
            file.write(all_text)
    
#click results listboxes------------------
def clickEvent(event):
    cs = results_list_Box.get(results_list_Box.curselection())
    print(results_list_Box.curselection()[0])
    clicked_position=results_list_Box.curselection()[0]
    plot_results_function(sol, clicked_position)
    ##Plot FFT if requested
    if (checkBox_FFT_var.get() == 1):
        plotFFT_results_function(sol, clicked_position)
#click results listboxes end--------------

#plotting FFT
def plotFFT_results_function(sol, clicked_position):
    t_start=start_Box.get(1.0, tk.END+"-1c")
    t_stop=stop_Box.get(1.0, tk.END+"-1c")
    t_step=step_Box.get(1.0, tk.END+"-1c")
    #Sampling variables
    intervals=eval(t_step)
    frequency_intervals=1/intervals
    signal_start_time=eval(t_start)
    signal_end_time=eval(t_stop)
    transform_Fourier=np.fft.fft(sol.y[(clicked_position - 1)])/len(sol.y[(clicked_position - 1)])
    transform_Fourier=transform_Fourier[range(int(len(sol.y[(clicked_position - 1)])/2))]
    points_Count=len(sol.y[(clicked_position - 1)])
    point_Values=np.arange(int(points_Count/2))
    time_Period=points_Count/frequency_intervals
    resultant_Frequencies=point_Values/time_Period
    #eval(t_start), eval(t_stop)+eval(t_step)
    #
    #plt.style.use('seaborn-poster')
    if (clicked_position - 1) > -1:
        plt.figure(figsize = (12, 4))
        plt.plot(resultant_Frequencies, 2*abs(transform_Fourier))
        #19Oct
        plt.savefig('FFT_pyLUISMR.png')
        # setup new window
        new_window = tk.Toplevel(root)
        new_window.iconbitmap('pyLUISMR.ico')
        # get image
        image = ImageTk.PhotoImage(Image.open('FFT_pyLUISMR.png'))
        # load image
        panel = tk.Label(new_window, image=image)
        panel.image = image
        panel.pack()
        #plt.show()
    else:
        messagebox.showinfo('information', 'Click on a variable to plot its values')
#plotting FFT end
    
#plotting function------------------------
def plot_results_function(sol, clicked_position):
    #old
    #plt.figure(figsize = (12, 4))
    #plt.subplot(121)
    #plt.plot(sol.t, sol.y[0])
    #plt.xlabel('t')
    #plt.ylabel('S(t)')
    #plt.subplot(122)
    #plt.plot(sol.t, sol.y[0] - np.sin(sol.t))
    #plt.xlabel('t')
    #plt.ylabel('S(t) - sin(t)')
    #plt.tight_layout()
    #plt.show()
    #old end
    #plt.style.use('seaborn-poster')
    if (clicked_position - 1) > -1:
        plt.figure(figsize = (12, 4))
        plt.plot(sol.t, sol.y[(clicked_position - 1)])
        #19Oct
        plt.savefig('FIG_pyLUISMR.png')
        # setup new window
        new_window = tk.Toplevel(root)
        new_window.iconbitmap('pyLUISMR.ico')
        # get image
        image = ImageTk.PhotoImage(Image.open('FIG_pyLUISMR.png'))
        # load image
        panel = tk.Label(new_window, image=image)
        panel.image = image
        panel.pack()
        #plt.show()
    else:
        messagebox.showinfo('information', 'Click on a variable to plot its values')
#plotting function end----------------------
        
def simulate_function():
    ##Simulation setup
    t_start=start_Box.get(1.0, tk.END+"-1c")
    t_stop=stop_Box.get(1.0, tk.END+"-1c")
    t_step=step_Box.get(1.0, tk.END+"-1c")
    ##
    #F = lambda t, s: np.cos(t)
    F=text_Box.get(1.0, tk.END+"-1c")

    #Clean list variables-------------------
    results_list_Box.delete(1,tk.END)
    results_list_Box2.delete(1,tk.END)
    results_list_Box3.delete(1,tk.END)
    #Search&remove variable names-----------
    var_names = rexs.search(r'Vars<<.+>>Vars', F)
    if var_names != None:
        aux_var_names=rexs.sub('Vars<<', '', var_names.group())
        aux_var_names=rexs.sub('>>Vars', '', aux_var_names)
        ##split using commas
        aux_var_names=aux_var_names.split(',')
        for i_var_names in range(len(aux_var_names)):
            results_list_Box.insert((i_var_names+1),aux_var_names[i_var_names])
    F=rexs.sub('\nVars<<.+>>Vars', '', F)
    #Search&remove variable names end-------

    ##Search&remove variable initializations--------------
    x_init = rexs.search(r"Init<<.+>>Init", F)
    if x_init != None:
        auxx_init=rexs.sub('Init<<', '', x_init.group())
        auxx_init=rexs.sub('>>Init', '', auxx_init)
        x_init=auxx_init
        if len(x_init.split(',')) == 1:
            x_init='['+x_init+']'
            

    F=rexs.sub('\nInit<<.+>>Init', '', F)
    ##Search&remove variable  initializations end--------------

    ##add lambda t to the first line to simplify
    F='lambda t, '+F
    
    #clean input
    F=rexs.sub('\n', ', ', F)

    if len(F) == 0 :
        messagebox.showerror("Error", "No system of equations.")
    else:
        #arange: (start, stop, step)
        ##Added the last time step to the simulation time
        t_eval = np.arange(eval(t_start), eval(t_stop)+eval(t_step), eval(t_step))
        #change time limit------------------
        #store global results
        global sol
        ##Include the initial values array x_init
        sol = solve_ivp(eval(F), [0, eval(t_stop)], eval(x_init), t_eval=t_eval)

        ##populate list
        for i_var_results in range(len(sol.y)):
            results_list_Box2.insert((i_var_results+1),sol.y[i_var_results][0])
            results_list_Box3.insert((i_var_results+1),sol.y[i_var_results][-1])
        ##populate list end


########################################## TAB 2 functions
def handle_event(event):
    if event.keysym == 'Return':#event.state == 12 and event.keysym == 'Return':
        input_text = entry_box_tab2.get()
        if input_text == '':
            messagebox.showwarning('Warning','Empty input.')
        else:
            text_box_tab2.configure(state='normal')  # allow editing
            text_box_tab2.insert('end', f'INPUT: {input_text}\n')
            x, y, z = symbols('x y z')
            sym_solution=eval(input_text)#diff(exp(x**2), x)#limit(sin(x)/x, x, 0)
            text_box_tab2.insert('end', f'OUTPUT: '+str(sym_solution)+'\n')
            text_box_tab2.configure(state='disabled')  # prevent further editing
            entry_box_tab2.delete(0, 'end')  # clear the entry box
###########################################################
#tk root configuration----------------------
root = tk.Tk()
# configuring the grid to expand 
root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

#Create frame for tabs
frm = ttk.Frame(root, padding=10)
frm.pack(fill='both', expand=True)
##frm.grid_columnconfigure((0,1,2,3,4,5), weight=1)
##frm.grid_rowconfigure((2), weight=1)
# Create the notebook
notebook = ttk.Notebook(frm)

# Create the tabs
tab1 = ttk.Frame(notebook)
tab1.grid(sticky="nsew")
tab1.grid_columnconfigure((0,1,2,3,4,5), weight=1)
tab1.grid_rowconfigure((2), weight=1)
####
tab2 = ttk.Frame(notebook)
# Add the tabs to the notebook
notebook.add(tab1, text='Integration')
notebook.add(tab2, text='Symbolics')

notebook.pack(fill='both', expand=True)
#tk root configuration end------------------

### create a menubar
##menubar = Menu(root)
##root.config(menu=menubar)
##
### create a menu
##file_menu = Menu(menubar, tearoff=0)
##
### add a menu items to the menu
##file_menu.add_command(label="New", command=root.destroy)
##file_menu.add_command(label="Open", command=fileOpen)
##file_menu.add_command(label="Save", command=root.destroy)
##file_menu.add_separator()
##
### add a menu item to the menu
##file_menu.add_command(
##    label='Exit',
##    command=root.destroy
##)
##
##
### add the File menu to the menubar
##menubar.add_cascade(
##    label="File",
##    menu=file_menu
##)
#
#Simulation setup
ttk.Label(tab1, text="Define-> 1)Start 2)Stop 3)Step").grid(column=0, row=0)
start_Box = tk.Text(tab1, height=1, width=5)
start_Box.grid(column=1, row=0)
start_Box.insert(tk.INSERT, '0')
stop_Box = tk.Text(tab1, height=1, width=5)
stop_Box.grid(column=2, row=0)
stop_Box.insert(tk.INSERT, '10')
step_Box = tk.Text(tab1, height=1, width=5)
step_Box.grid(column=3, row=0)
step_Box.insert(tk.INSERT, '0.001')
ttk.Button(tab1, text="Simulate!", command=simulate_function).grid(column=4, row=0)
#Simulation setup end

#User equations
ttk.Label(tab1, text="System of equations to simulate:").grid(column=0, row=1)
text_Box = tk.Text(tab1)
text_Box.grid(columnspan=4, row=2, sticky="nsew")
#text_Box.configure(state='enabled')
#listbox for results-----------------------
ttk.Label(tab1, text="Simulation results:").grid(column=4, row=1)
results_list_var = tk.StringVar()
results_list_Box = tk.Listbox(tab1, listvariable=results_list_var, exportselection=False)
results_list_Box.grid(column=4, row=2, sticky="nsew")
results_list_Box.insert(0, 'Variable name')
results_list_Box.bind('<<ListboxSelect>>', clickEvent)
##checkbox to show FFT
checkBox_FFT_var = tk.IntVar()
checkBox_FFT = tk.Checkbutton(tab1, text='Show FFT analysis',variable=checkBox_FFT_var, onvalue=1, offvalue=0)
checkBox_FFT.grid(column=5, row=1)
##
#

results_list_var2 = tk.StringVar()
results_list_Box2 = tk.Listbox(tab1, listvariable=results_list_var2, exportselection=False)
results_list_Box2.grid(column=5, row=2, sticky="nsew")
results_list_Box2.insert(0, 'Initial value')
#

results_list_var3 = tk.StringVar()
results_list_Box3 = tk.Listbox(tab1, listvariable=results_list_var3, exportselection=False)
results_list_Box3.grid(column=6, row=2, sticky="nsew")
results_list_Box3.insert(0, 'Ending value')
#listbox for results end-----------------------

#Create frame for buttons Open/Save
frmOpenSave = ttk.Frame(tab1, padding=10)
frmOpenSave.grid(column=0,row=3)
ttk.Button(frmOpenSave, text="Open", command=fileOpen).grid(column=0, row=0)
ttk.Button(frmOpenSave, text="Save as", command=saveIntegration).grid(column=1, row=0)
#User equations end

#####################################################################################
################### TAB 2
####################################################################################

entry_box_tab2 = tk.Entry(tab2, font=('CambriaMath', 11))
entry_box_tab2.pack(fill='both', expand=False)

text_box_tab2 = tk.Text(tab2, font=('CambriaMath', 11))
text_box_tab2.pack(fill='both', expand=True)

##text_box_tab2.configure(state='disabled')  # initially prevent editing

#####################################################################################
################### TAB 2 END
####################################################################################
#Quit
ttk.Button(root, text="Quit", command=root.destroy).pack()

#Window customization
root.title('PyLIUSMR')
root.iconbitmap('pyLUISMR.ico')
#sv_ttk.set_theme("light")
#Window customization end
root.bind('<Return>', handle_event) #Tab 2 
root.mainloop()













