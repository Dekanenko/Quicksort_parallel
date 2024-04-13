import tkinter
from tkinter import *
from tkinter import ttk
from random import randint
from pathlib import Path
import numpy as np
import subprocess
import shlex
import xlsxwriter
import re

from .Modules.Sorters import classical_quick_sort


def init():
    root = Tk()
    root.geometry('500x500')
    root.title('Quicksort')
    mainFrame = ttk.Frame(root)
    arrayFrame = ttk.Frame(mainFrame, padding=10)
    arrayFrame.grid()
    arrayEntry = Entry(arrayFrame)
    arrayEntry.grid(column=1, row=0, padx=5)
    ttk.Label(arrayFrame, text='Enter Array').grid(column=0, row=0)
    serialSortBtn = ttk.Button(arrayFrame, text='Serial Sort', width=10)
    parallelSortBtn = ttk.Button(arrayFrame, text='Parallel Sort', width=10)

    isDesc = tkinter.BooleanVar(value=False)
    ttk.Checkbutton(arrayFrame, text='Desc', variable=isDesc, onvalue=True, offvalue=False).grid(column=0, row=1, padx=5, pady=10)
    serialSortBtn.bind('<Button-1>', lambda event: doSerialSort(arrayEntry.get(), isDesc))
    parallelSortBtn.bind('<Button-1>', lambda event: doParallelSort(arrayEntry.get(), ThreadsEntry.get(), isDesc))
    serialSortBtn.grid(column=0, row=3, columnspan=2, pady=10)
    parallelSortBtn.grid(column=0, row=4, columnspan=2, pady=10)
    ThreadsEntry = Entry(arrayFrame)
    ThreadsEntry.grid(column=1, row=2, padx=5, pady=10)
    ttk.Label(arrayFrame, text='Enter Num of processes (power of 2)').grid(column=0, row=2)

    randomArrayFrame = ttk.Frame(mainFrame, padding=10)
    randomArrayFrame.grid()
    randomArrayLengthEntry = Entry(randomArrayFrame)
    randomArrayLengthEntry.grid(column=1, row=0, padx=5)
    ttk.Label(randomArrayFrame, text='Array Length').grid(column=0, row=0)
    button = ttk.Button(randomArrayFrame, text='Get Random Array', width=15)
    button.bind('<Button-1>', lambda event: fiilRandomArray(arrayEntry, randomArrayLengthEntry.get()))
    button.grid(column=0, row=2, columnspan=2, pady=10)
    mainFrame.pack()

    root.mainloop()


def makeArray(str):
    if len(re.findall("[a-zA-Z]", str))>0:
        popup = Toplevel()
        popup.geometry('300x100')
        popup.title('Error')
        popupFrame = ttk.Frame(popup, padding=10)

        ttk.Label(popupFrame, text='Array elements must be numbers').pack(pady=10, padx=5)
        popupFrame.pack()
        arr = []
    else:
        arr = str.split(',')
        for i in range(len(arr)):
            arr[i] = int(arr[i])

    return arr


def doSerialSort(str, isDesc):
    arr = makeArray(str)
    if len(arr) == 0:
        return
    
    up_order = True if isDesc.get() == 0 else False
    elapsed_time, result = classical_quick_sort.entry_point(arr, up_order=up_order)

    popup = Toplevel()
    popup.geometry('350x150')
    popup.title('Serial sort Result')
    popupFrame = ttk.Frame(popup, padding=10)

    ttk.Label(popupFrame, text='Size').grid(column=0, row=0, padx=5)
    ttk.Label(popupFrame, text=len(arr)).grid(column=1, row=0)
    ttk.Label(popupFrame, text='Elapsed Time (sec)').grid(column=0, row=1, pady=10, padx=5)
    ttk.Label(popupFrame, text=elapsed_time).grid(column=1, row=1, pady=10)

    button = ttk.Button(popupFrame, text='Save', width=10)
    button.bind('<Button-1>', lambda event: SaveResults("Serial Sort", result, elapsed_time))
    button.grid(column=0, row=2, columnspan=2, pady=10)
    popupFrame.pack()


def SaveResults(name, arr, elapsed_time):
    workbook = xlsxwriter.Workbook(name + '.xlsx')
    worksheet = workbook.add_worksheet(name)
    worksheet.write(1, 1, name)
    worksheet.write(2, 1, "Time (sec)")
    worksheet.write(2, 2, elapsed_time)
    worksheet.write(3, 1, "Sorted Array")
    for i in range(len(arr)):
        worksheet.write(4, i + 1, arr[i])

    workbook.close()

def wrong_process_num():
    popup = Toplevel()
    popup.geometry('450x100')
    popup.title('Error')
    popupFrame = ttk.Frame(popup, padding=10)

    ttk.Label(popupFrame, text='Number of processes must be a power of 2 and bigger than 1').pack(pady=10, padx=5)
    popupFrame.pack()

def doParallelSort(str, threads, isDesc):
    # numOfThreads = '4'
    if threads.isdecimal():
        intedThreads = int(threads)
        if (intedThreads & (intedThreads-1) == 0) and intedThreads != 0 and intedThreads != 1:
            numOfThreads = threads
        else:
            wrong_process_num()
            return
    else:
        wrong_process_num()
        return
    
    arr = np.asarray(makeArray(str))
    if len(arr) == 0:
        return
    
    infoToSave = np.append([isDesc.get()], arr)
    np.save('buffer', infoToSave)
    ROOT_DIR = Path(__file__).parent.parent.as_posix()
    print(ROOT_DIR + '/run_parallel_sort.sh ' + numOfThreads)
    rc = subprocess.call(shlex.split(ROOT_DIR + '/run_parallel_sort.sh ' + numOfThreads))
    result = np.load('buffer.npy')
    size = int(result[0])
    elapsed_time = result[1]
    arr = []  # result array to save
    i = 3
    for i in range(len(result)):
        arr.append(int(result[i]))

    popup = Toplevel()
    popup.geometry('350x150')
    popup.title('Parallel sort (p='+numOfThreads+') Result')
    popupFrame = ttk.Frame(popup, padding=10)

    ttk.Label(popupFrame, text='Size').grid(column=0, row=0, padx=5)
    ttk.Label(popupFrame, text=size).grid(column=1, row=0)
    ttk.Label(popupFrame, text='Elapsed Time (sec)').grid(column=0, row=1, pady=10, padx=5)
    ttk.Label(popupFrame, text=elapsed_time).grid(column=1, row=1, pady=10)

    button = ttk.Button(popupFrame, text='Save', width=10)
    button.bind('<Button-1>', lambda event: SaveResults("Parallel Sort (p="+numOfThreads+")", arr[2:], elapsed_time))
    button.grid(column=0, row=2, columnspan=2, pady=10)
    popupFrame.pack()


def fiilRandomArray(arrayEntry, length):
    if length.isdecimal():
        lngth = int(length)
        if lngth > 0:
            arrayEntry.delete(0, END)
            arr = []
            for i in range(0, lngth):
                arr.append(str(randint(-10000, 10000)))
            arrayEntry.insert(0, ','.join(arr))
    else:
        popup = Toplevel()
        popup.geometry('300x100')
        popup.title('Error')
        popupFrame = ttk.Frame(popup, padding=10)

        ttk.Label(popupFrame, text='Array size must be a positive integer').pack(pady=10, padx=5)
        popupFrame.pack()