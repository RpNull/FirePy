#! /usr/env/python
from tkinter import *
import FirePy as fp
query_days=0

class gui():
    root = Tk()
    root.geometry("600x400")
    root.title('FirePy: FireEye Intel APIv3')
    root.configure(bg='teal')
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0,weight=1)
    qd_label = Label(root,text="Days to query?")
    qd_label.config(bg='teal')
    qd_label.grid(row = 0, column = 0, pady = 2)
    qd = Entry(root, width=25)
    qd.grid(row = 1, column = 0, pady = 2)

    def get_qd():
        global query_days
        query_days = int(gui.qd.get())
    IndicatorButton = Button(root, text="Query Indicators", command=lambda:[ gui.get_qd(), fp.Query.Indicator_Query(query_days)], width = 25)
    IndicatorButton.grid(row = 5, column = 0, pady = 2)
    ReportButton = Button(root, text="Query Reports", command=lambda:[ gui.get_qd(), fp.Query.Report_Query(query_days)], width = 25)
    ReportButton.grid(row = 7, column = 0, pady = 2)
    PermissionsButton = Button(root, text="Query Permissions", command=lambda:[ fp.Query.Permissions_Query() ], width = 25)
    PermissionsButton.grid(row = 9, column = 0, pady = 2)
    MergeButton = Button(root, text="Merge CSVs", command=lambda:[ fp.Admin.merge() ], width = 25)
    MergeButton.grid(row = 11, column = 0, pady = 2)


def main():
    fp.Admin.path_check()
    try:
        exp = fp.DataManager.Token()
    except Exception as e:
        print(f'Unable to fetch token, please confirm enviromental variables and API keys')
        sys.exit(0)
    expired_label = Label(gui.root,text=f"Token expires in {exp}")
    expired_label.config(bg='teal')
    expired_label.grid(row = 15, column = 0,  pady = 2)
    gui.root.mainloop()

main()