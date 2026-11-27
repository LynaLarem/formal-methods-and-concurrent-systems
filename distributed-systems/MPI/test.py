#TP1 TEST1
# from mpi4py import MPI
# com = MPI.COMM_WORLD  #(importer un communicateur qui est un ensemble de data)
# rank = com.Get_rank()
# size = com.Get_size()
# print ("I'm the ", str(rank), "process of ", str(size), "processes")



# #test2 point a point synch
# from mpi4py import MPI
# com = MPI.COMM_WORLD
# rank = com.Get_rank()
# TAG = 99
# if rank ==0:
#     message = "hello"
#     com.send(message, dest = 1, tag = TAG)
#     print (str(rank), "envoie ", message, "vers", "1")
    
# if rank ==1:
#     tok = com.recv(source = MPI.ANY_SOURCE, tag = TAG)  #source = MPI.ANY_SOURCE ou source =0 (la dedieme recoit que du precess0)
#     print (str(rank), "recoit", tok, "de", "0")
    
    
# #test3 envoi tab en resoit que la premiere case point a point synch
# from mpi4py import MPI
# import numpy
# comm = MPI.COMM_WORLD
# rank = comm.Get_rank()
# if rank ==0:
#    tab = numpy.arange(1, 10, 3)
#    comm.send(tab, dest = 1)
#    print (str(rank), "envoie ", tab, "vers", "1")
    
# if rank ==1:
#     tok = numpy.empty(3, dtype = int)
#     comm.Recv(tok, source = 0)
#     print (str(rank), "recoit", tok, "de", "0")
    
    
    #TP1 TEST4 Acynch
    
    
    
    mpiexec -n 3 py C:\python\test4.py