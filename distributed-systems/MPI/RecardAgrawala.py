from mpi4py import MPI
from time import sleep
import random
from threading import Thread, Lock
from enum import Enum

class Etat(Enum):
    deh = 1
    dem = 2
    ded = 3

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

hi = 0
lasti = 0
Ri = set()
etati = Etat.deh
diffi = set()
lock = Lock()

atti = set(range(size)) #Ts les autres processus sauf soi-mm
atti.discard(rank)  #On enleve son propre rang (le processus mm))

def demanderSC():
    global hi, lasti, Ri, etati

    with lock:
        etati = Etat.dem
        hi += 1
        lasti = hi
        Ri = set(atti)

    print(f"[{rank}] Demande la SC avec horloge {lasti}")
    for j in atti:
        comm.send(["request", rank, lasti], dest=j)

    while True:
        with lock:
            if not Ri:
                break
        sleep(0.1)

    with lock:
        etati = Etat.ded

    print(f"[{rank}] Entre dans la SC")
    sleep(random.randint(1, 3))
    print(f"[{rank}] Quitte la SC")
    releaseCS()

def releaseCS():
    global etati, diffi
    with lock:
        etati = Etat.deh
        for j in diffi:
            comm.send(["permission", rank], dest=j)
        diffi.clear()

def recevoir_messages():
    global hi, lasti, Ri, etati, diffi
    while True:
        msg = comm.recv(source=MPI.ANY_SOURCE)

        if msg[0] == "request":
            sender, horloge = msg[1], msg[2]
            with lock:
                hi = max(hi, horloge) + 1
                if (etati == Etat.ded or
                   (etati == Etat.dem and (lasti, rank) < (horloge, sender))):
                    diffi.add(sender)
                else:
                    comm.send(["permission", rank], dest=sender)

        elif msg[0] == "permission":
            with lock:
                Ri.discard(msg[1])

def main():
    receiver_thread = Thread(target=recevoir_messages, daemon=True)
    receiver_thread.start()

    sleep(random.randint(1, 5))  # Laisse les autres s'initialiser
    demanderSC()

    sleep(2)  # Laisse les threads finir
    print(f"[{rank}] Terminé.")

if __name__ == "__main__":
    main()
