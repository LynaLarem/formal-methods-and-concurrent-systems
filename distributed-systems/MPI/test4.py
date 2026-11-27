from mpi4py import MPI
from time import sleep  

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

if rank == 0:
    sclib = True
    L = []
    while True:
        status = MPI.Status()
        message = comm.recv(source=MPI.ANY_SOURCE, status=status) 
        source = status.Get_source()

        print(f"Le PC reçoit {message} venant de {source}",flush=True)
        if message == "demande":
            if sclib:
                sclib = False
                comm.send("autorisation", dest=source) 
            else:
                L.append(source)

        elif message == "liberation":
            if L:
                premier_L = L.pop(0)  # Retirer le premier élément de la file d'attente
                comm.send("autorisation", dest=premier_L)
            else:
                sclib = True 

if rank != 0:
    while True: 
        comm.send("demande", dest=0)
        message = comm.recv(source=0)
       
        print(f"Le site {rank} a reçu l'autorisation d'utiliser la ressource.", flush=True)
        sleep(3)  
        print(f"Le site {rank} a terminé l'utilisation de la ressource.", flush=True)
        comm.send("liberation", dest=0)


##2 coordinateurs