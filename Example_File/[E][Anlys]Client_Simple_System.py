import socket
import sys
import numpy as np
import time
import multiprocessing as mp
from multiprocessing import shared_memory
import csv

def write_average_to_csv(avg, file_name, csv_lock):
    """
    Writes the computed average (an array-like of two values) to a CSV file.
    """
    with csv_lock:
        with open(file_name, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(avg)
        print(f"[ProcAverage] Average written to {file_name}")

def ReceiveProcess(host, port, stop_event, RawLock, DistributorLock, update_chunk, shm_shape, shm_name):
    """
    Connects to a TCP server, receives comma‐separated float data, collects a new update chunk,
    and then updates shared memory by removing the oldest rows and appending the new ones.
    """
    shm_arry = shared_memory.SharedMemory(name=shm_name)
    shm_np = np.ndarray(shm_shape, dtype=np.float64, buffer=shm_arry.buf)
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    
    temp_arry = []  # temporary storage until update_chunk rows are collected
    print("Process 1: Receiving Data")

    try:
        while not stop_event.is_set():
            # (Optionally block/wait for new data)
            data = client_socket.recv(1024)
            if not data:
                break
            rows = data.decode('utf-8').strip().split('\n')
            for row in rows:
                try:
                    values = list(map(float, row.split(',')))
                except ValueError as ve:
                    print(f"Skipping row due to conversion error: {row}")
                    continue
                temp_arry.append(values)
                if len(temp_arry) == update_chunk:
                    # Always acquire locks in the same order: DistributorLock then RawLock.
                    DistributorLock.acquire()
                    print("P1 took DistributorLock")
                    RawLock.acquire()
                    print("P1 took RawLock")
                    
                    # Shift the rolling window:
                    # Discard the oldest update_chunk rows
                    shm_np[:-update_chunk] = shm_np[update_chunk:]
                    # Append new data at the end of the buffer
                    shm_np[-update_chunk:] = np.array(temp_arry)
                    print("P1: Shared Memory Updated (rolled window)")
                    
                    # Release locks in reverse order.
                    RawLock.release()
                    print("P1 released RawLock")
                    DistributorLock.release()
                    print("P1 released DistributorLock")
                    
                    temp_arry = []
    except socket.timeout:
        print("Timeout occurred, no data received within the specified time.")
    except Exception as e:
        print(f"Process 1 produced the following error:\n\n{e}")
    finally:
        client_socket.close()

def ProcSplit(stop_event, RawLock, DistributorLock, shm_shape, shm_name, buffer_length):
    """
    Reads the entire rolling window from shared memory and splits it into two arrays
    while acquiring locks in a consistent order.
    """
    shm_arry = shared_memory.SharedMemory(name=shm_name)
    shm_np = np.ndarray(shm_shape, dtype=np.float64, buffer=shm_arry.buf)
    print("Process 2: Splitting Data")

    # Allocate full buffers based on the rolling window size
    temp_arry = np.zeros(shm_shape, dtype=np.float64)
    eda_data = np.zeros(buffer_length, dtype=np.float64)
    rsp_data = np.zeros(buffer_length, dtype=np.float64)

    try:
        while not stop_event.is_set():
            # Clear arrays
            temp_arry.fill(0)
            eda_data.fill(0)
            rsp_data.fill(0)
            
            # Acquire locks in the same order.
            DistributorLock.acquire()
            print("P2 took DistributorLock")
            RawLock.acquire()
            print("P2 took RawLock")
            
            # Copy the full data chunk (the rolling window).
            temp_arry[:] = shm_np[:]
            
            # Release the locks.
            RawLock.release()
            print("P2 released RawLock")
            DistributorLock.release()
            print("P2 released DistributorLock")
            
            # Split the data into two arrays (one for each column).
            eda_data[:] = temp_arry[:, 0]
            rsp_data[:] = temp_arry[:, 1]
            
            # (Further processing on eda_data and rsp_data can be done here.)
            time.sleep(0.5)  # Optional delay to slow down busy-looping.
    except Exception as e:
        print(f"Process 2 produced the following error:\n\n{e}")
    finally:
        print("Process 2 finished.")

def ProcAverage(stop_event, RawLock, DistributorLock, shm_shape, shm_name, buffer_length, csv_lock):
    """
    Reads the entire rolling window from shared memory, computes the column-wise average,
    prints the result, and writes it to a CSV file.
    """
    shm_arry = shared_memory.SharedMemory(name=shm_name)
    shm_np = np.ndarray(shm_shape, dtype=np.float64, buffer=shm_arry.buf)
    print("Process 3: Average Calculation")

    try:
        while not stop_event.is_set():
            # Acquire locks in the same order.
            DistributorLock.acquire()
            print("P3 took DistributorLock")
            RawLock.acquire()
            print("P3 took RawLock")
            
            # Make a local copy of the entire rolling window.
            local_chunk = np.copy(shm_np[:])
            
            RawLock.release()
            print("P3 released RawLock")
            DistributorLock.release()
            print("P3 released DistributorLock")
            
            # Compute the column-wise average over the full 10-second window.
            avg = np.mean(local_chunk, axis=0)
            print("Process 3: Average of rolling window:", avg)
            
            # Write the average to a CSV file.
            write_average_to_csv(avg, "Example_product_csv.csv", csv_lock)
            
            time.sleep(1)  # Pause before processing the next chunk.
    except Exception as e:
        print(f"Process 3 produced the following error:\n\n{e}")
    finally:
        print("Process 3 finished.")

if __name__ == '__main__':
    host = 'localhost'
    port = 12345

    # Set up parameters for a 10-second rolling window at 2000 Hz.
    buffer_length = 20000  # Total rows to store 10 seconds worth of data.
    update_chunk = 2000    # New data chunk size (e.g., we update the window every 1 second).
    shape = (buffer_length, 2)  # Two columns of data.

    dtype = np.float64

    # Locks for synchronizing shared memory and CSV access.
    RawLock = mp.Lock()
    DistributorLock = mp.Lock()
    csv_lock = mp.Lock()
    stop_event = mp.Event()

    # Create shared memory.
    shm = shared_memory.SharedMemory(create=True, size=int(np.prod(shape) * np.dtype(dtype).itemsize))
    shared_array = np.ndarray(shape, dtype=dtype, buffer=shm.buf)

    # Create processes.
    # Process 1 (Receiver) updates using 'update_chunk' rows.
    p1 = mp.Process(target=ReceiveProcess, args=(host, port, stop_event, RawLock, DistributorLock,
                                                   update_chunk, shape, shm.name))
    # Processes 2 & 3 operate on the full rolling window ('buffer_length' rows).
    p2 = mp.Process(target=ProcSplit, args=(stop_event, RawLock, DistributorLock, shape, shm.name, buffer_length))
    p3 = mp.Process(target=ProcAverage, args=(stop_event, RawLock, DistributorLock, shape, shm.name, buffer_length, csv_lock))

    try:
        # Start processes.
        p1.start()
        time.sleep(0.1)  # Ensure Process 1 initializes first.
        p2.start()
        p3.start()

        # Keep the main process running.
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Ctrl+C] detected! Cleaning up...")

        # Signal all processes to stop.
        stop_event.set()
        p1.join(timeout=5)
        print("Force killing Process 1..." if p1.is_alive() else "Process 1 terminated.")
        p2.join(timeout=5)
        print("Force killing Process 2..." if p2.is_alive() else "Process 2 terminated.")
        p3.join(timeout=5)
        print("Force killing Process 3..." if p3.is_alive() else "Process 3 terminated.")
        if p1.is_alive():
            p1.terminate()
        if p2.is_alive():
            p2.terminate()
        if p3.is_alive():
            p3.terminate()

        # Clean up shared memory.
        try:
            shm.close()
            shm.unlink()
            print("Clearing Memory")
        except Exception as e:
            print(f"Error cleaning shared memory: {e}")

        print("All processes terminated and shared memory cleaned up. Exiting...")
        sys.exit(0)

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        stop_event.set()
        time.sleep(0.1)
        p1.terminate()
        p2.terminate()
        p3.terminate()
        time.sleep(0.1)
        shm.close()
        shm.unlink()
        sys.exit(1)