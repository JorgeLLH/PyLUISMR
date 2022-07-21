import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import solve_ivp
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import Menu
#Regular expressions
import re


plt.style.use('seaborn-poster')

def simulate_function():

    #F = lambda t, s: np.cos(t)
    F=text_Box.get(1.0, tk.END+"-1c")
    #clean input
    F=re.sub('\n', ', ', F)
    #Simulation setup
    t_start=start_Box.get(1.0, tk.END+"-1c")
    t_stop=stop_Box.get(1.0, tk.END+"-1c")
    t_step=step_Box.get(1.0, tk.END+"-1c")
    #
    if len(F) == 0 :
        messagebox.showerror("Error", "No system of equations.")
    else:
        #arange: (start, stop, step)
        #    t_eval = np.arange(0, np.pi, 0.1)
        t_eval = np.arange(eval(t_start), eval(t_stop), eval(t_step))
        sol = solve_ivp(eval(F), [0, np.pi], [0], t_eval=t_eval)

        plt.figure(figsize = (12, 4))
        plt.subplot(121)
        plt.plot(sol.t, sol.y[0])
        plt.xlabel('t')
        plt.ylabel('S(t)')
        plt.subplot(122)
        plt.plot(sol.t, sol.y[0] - np.sin(sol.t))
        plt.xlabel('t')
        plt.ylabel('S(t) - sin(t)')
        plt.tight_layout()
        plt.show()

root = tk.Tk()
frm = ttk.Frame(root, padding=10)
frm.grid()
#
# create a menubar
menubar = Menu(root)
root.config(menu=menubar)

# create a menu
file_menu = Menu(menubar)

# add a menu item to the menu
file_menu.add_command(
    label='Exit',
    command=root.destroy
)


# add the File menu to the menubar
menubar.add_cascade(
    label="File",
    menu=file_menu
)
#
#Simulation setup
ttk.Label(frm, text="Define-> 1)Start 2)Stop 3)Step").grid(column=0, row=0)
start_Box = tk.Text(frm, height=1, width=5)
start_Box.grid(column=1, row=0)
stop_Box = tk.Text(frm, height=1, width=5)
stop_Box.grid(column=2, row=0)
step_Box = tk.Text(frm, height=1, width=5)
step_Box.grid(column=3, row=0)
ttk.Button(frm, text="Simulate!", command=simulate_function).grid(column=4, row=0)
#Simulation setup end

#User equations
ttk.Label(frm, text="System of equations to simulate:").grid(column=0, row=1)
text_Box = tk.Text(frm, height=10, width=30)
text_Box.grid(columnspan=4, row=2)
#User equations end

#Quit
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=4, row=3)

#Window customization
root.title('PyLIUSMR')
root.iconbitmap('pyLUISMR.ico')
#Window customization end

root.mainloop()
