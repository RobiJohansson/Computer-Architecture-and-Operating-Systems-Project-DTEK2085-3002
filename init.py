import os
import random
import multiprocessing
import sys
from multiprocessing import shared_memory


def child_process(pipe_out):
    priority = random.randint(0, 19)
    print(f"Child process {os.getpid()} generated priority: {priority}")
    os.write(pipe_out, str(priority).encode())
    os.close(pipe_out)  # Close the write end of the pipe after writing


def init_process(shm_name):
    shm = shared_memory.SharedMemory(name=shm_name)

    pipes = [os.pipe() for _ in range(4)]  # Create pipes for 4 child processes
    processes = []

    # Use multiprocessing.Process to create child processes
    for i in range(4):
        # Close the parent's write end of the pipe before creating child process
        os.close(pipes[i][0])  # Parent closes its read end immediately
        process = multiprocessing.Process(target=child_process, args=(pipes[i][1],))
        processes.append(process)
        process.start()
        os.close(pipes[i][1])  # Parent closes its write end after starting the child process

    for process in processes:
        process.join()  # Wait for all child processes to finish

    priorities = []
    for i in range(4):
        # Parent process reads from the pipes
        priority = os.read(pipes[i][0], 1024).decode().strip()  # Strip() call here to remove potential whitespace
        if priority:  # Ensure that we actually read something
            priorities.append(int(priority))
        os.close(pipes[i][0])  # Close the read end of the pipe after reading

    print(f"Priorities received from P1-P4: {priorities}")

    shared_data = ' '.join(map(str, priorities)).encode('utf-8')
    shm.buf[:len(shared_data)] = shared_data

    shm.close()


if __name__ == "__main__":
    shm_name = sys.argv[1]
    init_process(shm_name)
