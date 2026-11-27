from mpi4py import MPI
from time import sleep 
import random 
from threading import Thread , Lock
from enum import Enum

#mpiexec -n 3 python c://python/suzukiEtKasami.py
class Etat (Enum):
    deh=1
    dem=2
    ded=3


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

etat = Etat.deh
jetonDispo= (rank == 0)
jeton = []
nbrq = []
for j in range(size):
    nbrq.append(0)
    jeton.append(0
                 )
def demanderSC():
    global jeton, nbrq, etat, jetonDispo
    etati= Etat.dem
    
    while not jetonDispo:
        nbrq[rank]  += 1
        
        print(f"[{rank}] Demande la SC")
        for j in set(range(size)- {i})
            comm.send(["request", rank, nbrq[rank]], dest=j)
           
        while True:
            if jetonDispo:
                break
            
        print(f"[{rank}] Entre dans la SC")
        sleep(random.randint(1,3))
        print(f"[{rank}] Quitte la SC")
        releaseCS()
        
    def recevoir_messages():
       global jeton, nbrq, etat, jetonDispo
       
       while True:
         msg = comm.recv(source=MPI.ANY_SOURCE)
         if msg[0] == "request" :
            nbrq[1]+= 1 
         else:
           if jetonDispo and etat == Etat.deh and nbrq[1] > jeton[1] :
               jetonDispo = False
               comm.send(["permission"], msg[1])
               
               
    def recevoir_jeton():
        jetonDispo = True
        
     
    def releaseSC():
        global jeton, nbrq, etat, jetonDispo
    with True:
        etat = Etat.deh
        jeton[rank] = nbrq[rank]
        
        for j in list(rang(ramk+1), size)+list(range(0,1)):
          