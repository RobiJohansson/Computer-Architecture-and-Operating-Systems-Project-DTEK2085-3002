import time
from multiprocessing import shared_memory


def scheduler():
    shm = shared_memory.SharedMemory(create=True, size=1024)
    print(f"Scheduler created shared memory with name: {shm.name}")

    print("Waiting for init process to write data into shared memory...")

    while True:
        shared_data = bytes(shm.buf[:1024]).decode('utf-8').strip()

        # Check for new data in shared memory
        if shared_data != '\x00' * 1024:
            shared_data = shared_data.replace('\x00', '').strip()
            priorities = list(map(int, shared_data.split()))

            priorities.sort()
            print(f"Sorted priorities: {priorities}")

            break

        # Wait for a second before checking again
        time.sleep(1)

    shm.close()
    shm.unlink()


if __name__ == "__main__":
    scheduler()
