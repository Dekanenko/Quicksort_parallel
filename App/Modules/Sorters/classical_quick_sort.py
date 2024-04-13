import numpy as np
import time

np.random.seed(42)

def divide(arr, low, high, up_order=True):
    pivot = arr[high]
    
    i = low - 1
    
    for j in range(low, high):
        if up_order and arr[j] <= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
        elif not up_order and arr[j] >= pivot:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    
    arr[i+1], arr[high] = arr[high], arr[i+1]
    
    return i+1

def quick_sort(arr, low = -1, high = -1, up_order=True):
    if low == -1 and high ==- 1:
        low = 0
        high = len(arr)-1
        
    if low < high:
        division = divide(arr, low, high, up_order)

        quick_sort(arr, low=low, high=division-1, up_order=up_order)
        quick_sort(arr, low=division+1, high=high, up_order=up_order)
    
    return arr

def entry_point(arr, up_order=True):
    start_time = time.time()
    result = quick_sort(arr=arr, up_order=up_order)
    end_time = time.time()
    elapsed_time = end_time - start_time

    return elapsed_time, result