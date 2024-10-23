from multiprocessing import shared_memory
import time


def scheduler():
    shm = shared_memory.SharedMemory(create=True, size=1024)
    print(f"Scheduler created shared memory with name: {shm.name}")

    input("Waiting for init process to write data into shared memory...")

    shared_data = bytes(shm.buf[:1024]).decode('utf-8').strip()

    shared_data = shared_data.replace('\x00', '').strip()

    priorities = list(map(int, shared_data.split()))

    priorities.sort()
    print(f"Sorted priorities: {priorities}")

    shm.close()
    shm.unlink()


if __name__ == "__main__":
    scheduler()
