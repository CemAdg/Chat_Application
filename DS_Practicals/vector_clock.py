from multiprocessing import Process, Pipe
from time import sleep


def local_event(pid, timestamp):
    timestamp[pid-1] += 1
    print('Process {} performed local event. Lamport timestamp is {}'.format(pid, timestamp))
    return timestamp


def send_event(pipe, pid, timestamp):
    timestamp[pid-1] += 1
    pipe.send((pid, timestamp))
    print('Process {} sent message. Lamport timestamp is {}'.format(pid, timestamp))
    return timestamp


def receive_event(pipe, pid, timestamp):
    sender_id, ts = pipe.recv()
    timestamp[pid-1] += 1
    for id in range(len(timestamp)):
        timestamp[id-1] = max(ts[id-1], timestamp[id-1])
    print('Process {} received message from Process {}. Lamport timestamp is {}'.format(pid, sender_id, timestamp))
    return timestamp


def process_one(pipe12):
    pid = 1
    timestamp = [0,0,0]
    timestamp = local_event(pid, timestamp)
    timestamp = send_event(pipe12, pid, timestamp)
    # sleep(3)
    timestamp = local_event(pid, timestamp)
    timestamp = receive_event(pipe12, pid, timestamp)
    timestamp = local_event(pid, timestamp)


def process_two(pipe21, pipe23):
    pid = 2
    timestamp = [0,0,0]
    timestamp = receive_event(pipe21, pid, timestamp)
    timestamp = send_event(pipe21, pid, timestamp)
    timestamp = send_event(pipe23, pid, timestamp)
    timestamp = receive_event(pipe23, pid, timestamp)


def process_three(pipe32):
    pid = 3
    timestamp = [0,0,0]
    timestamp = receive_event(pipe32, pid, timestamp)
    timestamp = send_event(pipe32, pid, timestamp)


if __name__ == '__main__':
    one_two, two_one = Pipe()
    two_three, three_two = Pipe()

    process1 = Process(target=process_one, args=(one_two,))
    process2 = Process(target=process_two, args=(two_one, two_three))
    process3 = Process(target=process_three, args=(three_two,))

    process1.start()
    process2.start()
    process3.start()

    process1.join()
    process2.join()
    process3.join()