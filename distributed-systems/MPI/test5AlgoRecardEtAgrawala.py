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
diffi = set()
atti = set(range(size))# Tous les autres processus sauf soi-même
atti.discard(rank)  # Enlève ton propre rank proprement


lock = Lock()

def demanderSC():
    global hi
    with lock:
     etati = Etat.dem
     hi+= 1
     lasti = hi
     atti= Ri
    
    print(f"[{rank}] Demande la SC avec horloge {lasti}")
    for j in atti :
        comm.send(["request", rank, lasti], dest=j)
    
    while   True :
        with lock:
          if not atti:
            break
        sleep(0.1)
    
    etati = Etat.ded
    print(f"[{rank}] Entre dans la SC")
    sleep(random.randint(1,3))
    print(f"[{rank}] Quitte la SC")
    releaseCS()
    
def recevoir_messages():
  while True:
     msg = comm.recv(source=MPI.ANY_SOURCE)
     if msg[0] == "request" :
       hi = max(hi, msg[2])
       if  (etati == Etat.ded or ( etati == Etat.dem and (lasti, rank) < (msg[2], msg[1]))) :
           #diffi = diffi.add(msg[2])
           diffi.add(msg[1])
       else :
           comm.send(["permission"], msg[1])
           
     elif msg[0] == "permission":
        with lock:
          Ri.discard(msg[1])      
           
           
def releaseCS():
    with lock:
        etati = Etat.deh
        for j in diffi:
            comm.send(["permission"], dest=j)
        diffi.clear() 

def main():
    receiver_thread = Thread(target=recevoir_messages)
    receiver_thread.start()

    sleep(random.randint(1, 5)) 
    
    demanderSC()

    sleep(2)  

if __name__ == "__main__":
    main()

