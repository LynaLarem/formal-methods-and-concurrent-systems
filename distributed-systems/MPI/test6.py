from mpi4py import MPI
from time import sleep
import random
import threading

comm = MPI.COMM_WORLD
i = comm.Get_rank()
n = comm.Get_size()

if i == 0:
    L = []
    sclib = True
    plod = None  # pour traiter les requêtes en double
    status = MPI.Status()

    while True:
        msg = comm.recv(source=MPI.ANY_SOURCE, status=status)
        source = status.Get_source()
        print(f"Coord Reçoit {msg} de {source}", flush=True)

        if msg == "demande":
            if sclib:
                comm.send("autorisation", dest=source)
                sclib = False
                plod = source
            elif source not in L and plod != source:
                L.append(source)
        elif msg == "Liberer":
            if len(L) != 0:
                sl = L.pop(0)
                comm.send("autorisation", dest=sl)
                plod = sl
            else:
                sclib = True
                plod = None

else:
    numReq = 0

    def delayed_request(nr):
        if numReq == nr:
            print(f"Processus {i} effectue une deuxieme request({nr})", flush=True)
            comm.send("demande", dest=0)

    while True:
        if i == 2 and numReq == 1:
            print(f"Processus {i} envoie une demande", flush=True)
            comm.send("demande", dest=0)
        else:
            # Déclenche une demande après 8 secondes
            timer_thread = threading.Timer(8.0, delayed_request, args=(numReq,))
            timer_thread.start()
            timer_thread.join()

        msg = comm.recv(source=0)
        print(f"Processus {i} accède à la SC", flush=True)
        sleep(random.randint(1, 3))
        comm.send("Liberer", dest=0)
        numReq += 1
