from mpi4py import MPI
from time import sleep 
import random 
from threading import Thread , Lock
from enum import Enum

#mpiexec -n 3 python c://python/test5AlgoRecardEtAgrawala.py

class Etat (Enum):
    deh=1
    dem=2
    ded=3


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

hi = 0
lasti = None
Ri = set()
etati = Etat.deh
L = []


lock = Lock()


def demanderSC():
    global hi
    with lock:
        etati = Etat.dem
        hi += 1
        lasti = hi
         
        
    print(f"[{rank}] Demande la SC avec horloge {lasti}")

    comm.send(["request", rank, lasti], dest=(rank + 1) % size)

    while True:
        with lock:
            if not atti:  
                break
        sleep(0.1)
    
    etati = Etat.ded
    print(f"[{rank}] Entre dans la SC")
    sleep(random.randint(1, 3)) 
    print(f"[{rank}] Quitte la SC")
    releaseCS()



def recevoir_messages():
    while True:
        msg = comm.recv(source=MPI.ANY_SOURCE)
        if msg[2] != i:
            hi = max(hi, msg[2])
            if (etati == Etat.ded or
                (etati == Etat.dem and (lasti, rank) < (msg[2], msg[1]))):
               
                L.append(msg)
            else:
               
                comm.send(["request", msg[1], msg[2]], dest=(rank + 1) % size)

        #entrer dans la sc
        if msg[0] == "request" and msg[1] == rank:
            with lock:
                print(f"[{rank}] Permission accordée apres le parcours de l'anneau")
                break  
            
def release()