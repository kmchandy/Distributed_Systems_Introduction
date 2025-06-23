from multiprocessing import Process, SimpleQueue
import time

# Agent A: Sends messages


def agent_a(queue: SimpleQueue):
    for i in range(5):
        msg = f"Message {i} from Agent A"
        print(f"[Agent A] Sending: {msg}")
        queue.put(msg)
        time.sleep(1)
    queue.put("STOP")  # Signal Agent B to stop
    print("[Agent A] Finished sending messages.")

# Agent B: Receives messages


def agent_b(queue: SimpleQueue):
    while True:
        msg = queue.get()
        if msg == "STOP":
            print("[Agent B] Received STOP signal.")
            break
        print(f"[Agent B] Received: {msg}")


if __name__ == "__main__":
    queue = SimpleQueue()

    # Create the processes
    process_a = Process(target=agent_a, args=(queue,))
    process_b = Process(target=agent_b, args=(queue,))

    # Start the processes
    process_a.start()
    process_b.start()

    # Wait for both to complete
    process_a.join()
    process_b.join()

    print("Both agents finished.")
