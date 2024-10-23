import os
import random
import sys
from multiprocessing import Process, Pipe, shared_memory


def child_process(conn):
    """Child process generates a random priority and writes it to the pipe."""
    priority = random.randint(0, 19)  # Generate random integer between 0-19
    print(f"Child process {os.getpid()} generated priority: {priority}")
    conn.send(priority)  # Write the priority to the pipe
    conn.close()  # Close the connection
    sys.exit(0)  # Terminate the child process


def init_process():
    """Parent process creates 4 child processes and communicates via pipes."""

    connections = [Pipe() for _ in range(4)]  # Create pipes for 4 child processes
    processes = []  # To track the child processes

    # Create 4 child processes
    for i in range(4):
        process = Process(target=child_process, args=(connections[i][1],))  # Create a new child process
        processes.append(process)
        process.start()  # Start the child process
        connections[i][1].close()  # Close the write end of the pipe in the parent

    priorities = []

    # Parent process reads the priorities from the pipes
    for i in range(4):
        priority = connections[i][0].recv()  # Read from pipe
        priorities.append(priority)  # Append priority to list
        connections[i][0].close()  # Close the read end of the pipe after reading

    print(f"Priorities received from P1-P4: {priorities}")

    # Write priorities to shared memory
    shm_name = input("Enter the shared memory name: ")
    existing_shm = shared_memory.SharedMemory(name=shm_name)  # replace 'shm_name' with actual name
    data_bytes = ' '.join(map(str, priorities)).encode('utf-8')
    existing_shm.buf[:len(data_bytes)] = bytes(data_bytes)

    # Wait for all child processes to finish
    for process in processes:
        process.join()


if __name__ == "__main__":
    init_process()
