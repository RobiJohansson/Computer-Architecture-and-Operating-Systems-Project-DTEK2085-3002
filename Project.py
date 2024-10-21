import os
import random
import multiprocessing
import sys


def child_process(pipe_out):
    priority = random.randint(0, 19)
    os.write(pipe_out, str(priority).encode())
    os.close(pipe_out)
    sys.exit(0)


def write_to_shared_memory(priorities):
    # Create shared memory with enough size for 4 integers
    shm = multiprocessing.SharedMemory(create=True, size=1024)  # size is just larger than needed

    # Join the list of integers into a string and write to shared memory
    shared_data = ' '.join(map(str, priorities)).encode('utf-8')
    shm.buf[:len(shared_data)] = shared_data  # Write to shared memory

    return shm  # Return shared memory object to pass its name to scheduler


def init_process():
    pipes = [os.pipe() for _ in range(4)]  # Create 4 pipes
    pids = []

    # Fork 4 child processes (P1-P4)
    for i in range(4):
        process = multiprocessing.Process(target=child_process, args=(pipes[i][1],))
        pids.append(process)
        process.start()
        os.close(pipes[i][1])  # Close the write end in parent

    # Parent (init) process reads from all pipes
    priorities = []
    for i in range(4):
        priority = os.read(pipes[i][0], 1024).decode()  # Read the priority number
        priorities.append(int(priority))
        os.close(pipes[i][0])  # Close the pipe after reading

    print(f"Priorities received from P1-P4: {priorities}")

    # Write the priorities to shared memory and return the shared memory object
    shm = write_to_shared_memory(priorities)

    # Return the name of the shared memory segment to use in the scheduler
    return shm.name


def scheduler(memory_name):
    # Attach to the existing shared memory block created by init
    shm = multiprocessing.SharedMemory(name=memory_name)

    # Read the data from shared memory
    shared_data = bytes(shm.buf[:1024]).decode('utf-8').strip()
    priorities = list(map(int, shared_data.split()))

    # Sort the priorities
    priorities.sort()
    print(f"Sorted priorities: {priorities}")

    # Detach from shared memory
    shm.close()
    # Remove shared memory block
    shm.unlink()


if __name__ == "__main__":
    shm_name = init_process()
    print(f"Shared memory created with name: {shm_name}")

    # Call scheduler to read from shared memory and process the data
    scheduler(shm_name)
