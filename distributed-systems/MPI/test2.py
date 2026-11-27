# from mpi4py import MPI
# import time
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()

# if rank == 0:
#     start_time = time.time()
#     time.sleep(2)
    
# if rank == 1:
#     time.sleep(3)
    
# if rank == 2:
#     time.sleep(5)
    
# comm.Barrier()
# if rank == 0:
#     end_time = time.time()
#     elapsed_time = end_time - start_time
#     print (f"Temps ecoule : {elapsed_time: .4f} secondes")
    
    
# from mpi4py import MPI
# import numpy
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank() 
# data = numpy.zeros(3, dtype = int)
# if rank == 0: 
#     data = numpy.arange(1, 10, 3)
    
# print(f"{rank}: avant envoi le contenue de data est : {data}")

# data = comm.bcast(data, root=0)
# print(f"{rank}: le contenue apes la reception de data est : {data}")

  
# from mpi4py import MPI
# import numpy
# comm = MPI.COMM_WORLD
# size = comm.Get_size()
# rank = comm.Get_rank()
# data = numpy.empty([size, 3], dtype = int)
# if rank == 0:
#     data = numpy.arange(size*3).reshape((size, 3))
#     print (data)
# rcvdata = numpy.zeros(3, dtype= int)
# comm.Scatter(data, rcvdata, root=0)
# print("valeur apres recevoir les donnees ", rcvdata)

#exercice a faire
from mpi4py import MPI
import numpy
comm = MPI.COMM_WORLD
rank = comm.Get_rank()  
size = comm.Get_size()  


if rank == 0:
    data = numpy.random.randint(0, 10, size=(size, 3), dtype=numpy.int32) #random.random() elle prend qu'un seul param, donc il faut utiliser randint
    print(f"Tableau genere sur le processus racine :\n{data}\n")
else:
    data = None  # Tous les autres processus doivent avoir cette variable définie


#Chaque processus recoit une partie des data
recv_data = numpy.zeros(3, dtype=numpy.int32)
comm.Scatter(data, recv_data, root=0)

#Calcul de la moy locale (de chaque processus)
moy_local = numpy.mean(recv_data)
print(f"Processus {rank} a reçu {recv_data}, Calcule la moy locale : {moy_local:.2f}")

#Le processus racine collecte toutes les moy pour calculer la moy global
moy_global = None
if rank == 0:
     moy_global = numpy.zeros(size, dtype=float)

comm.Gather(moy_local, moy_global, root=0)

#Calcul de la moyenne globale sur le processus racine
if rank == 0:
    global_mean = numpy.mean(moy_global)
    print(f"\nMoyenne globale : {global_mean:.2f}")