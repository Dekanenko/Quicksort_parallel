import numpy as np
from mpi4py import MPI
import time
import classical_quick_sort
# import writer

np.random.seed(42)

def divide(arr, pivot, uporder=True):
    i = 0
    for j in range(len(arr)):
        if arr[j] <= pivot:
            arr[j], arr[i] = arr[i], arr[j]
            i += 1

    if uporder:
        return arr[:i], arr[i:]
    return arr[i:], arr[:i]


def parallel_quick_sort(arr=[]):
    sub_array = []
    if rank == 0:
        # split array
        step = 1
        if len(arr) > size:
            step = len(arr) // (size)

        for i in range(0, size-1):
            sub_array.append(arr[i*step:(i+1)*step])

        sub_array.append(arr[(i+1)*step:])

    sub_array = comm.scatter(sub_array, root=0)

    bin_size = len(np.binary_repr(size-1))
    N = bin_size
    b_rank = np.binary_repr(rank, width=N)

    while True:
        pivot = 0
        if rank % 2**N == 0:
            if len(sub_array) > 0:
                # pivot = sub_array[-1]
                pivot = np.average(sub_array)

            for i in range(1, 2**N):
                comm.send(pivot, rank+i, tag=3)
        else:
            pivot = comm.recv(source=(rank//(2**N) * 2**N), tag=3)

        s, b = divide(sub_array, pivot, uporder=UP_ORDER)

        if b_rank[bin_size-N] == "0":
            sender_rank = rank + 2**(N-1)
            tmp_arr = comm.recv(source=sender_rank, tag=2)
            comm.send(b, dest=sender_rank, tag=2)
            sub_array = np.append(s, tmp_arr)

        if b_rank[bin_size-N] == "1":
            sender_rank = rank - 2**(N-1)
            comm.send(s, dest=sender_rank, tag=2)
            tmp_arr = comm.recv(source=sender_rank, tag=2)
            sub_array = np.append(b, tmp_arr)

        N -= 1
        if N == 0:
            break

    sub_array = classical_quick_sort.quick_sort(sub_array, up_order=UP_ORDER)

    newData = comm.gather(sub_array, root=0)
    if rank == 0:
        out = []
        for elem in newData:
            out.extend(elem.tolist())

        return out



result = np.load('buffer.npy')
isDesc = result[0]
UP_ORDER = True if isDesc==0 else False
arr = []
for i in range(1, len(result)):
    arr.append(result[i])

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

dummy = np.random.randint(low=-size, high=size, size=size)
if rank == 0:
    arr_size = len(dummy)
    start = time.time()
    out = parallel_quick_sort(dummy)
    end = time.time()
else:
    parallel_quick_sort()

if rank == 0:
    arr_size = len(arr)
    start = time.time()
    out = parallel_quick_sort(arr)
    end = time.time()

    result = np.append([arr_size], [end-start])
    result = np.append(result, out)
    np.save('buffer', result)
else:
    parallel_quick_sort()


MPI.Finalize()