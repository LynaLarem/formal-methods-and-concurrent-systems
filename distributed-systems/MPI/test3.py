from time import sleep, perf_counter
from threading import Thread, Lock
### ex1
# def task():
#     print("Le thread commence")
#     sleep(1)
# #creation du thread
# thread = Thread(target=task)
# #lncer le thread
# thread.start()
# #attendre la fin du thread
# print ("\n attendre le thread ...")
# thread.join()

###ex2
# def task(sleep_time, message):
#     sleep (sleep_time)
#     print (message)
    
# thread = Thread(target=task, args=(2, "un nv msg d'un autre thread"))
# thread.start()
# print("en attente de la in du thread ...")
# thread.join()

# ##ex3
# #creer les deux thread
# thread1 = Thread()
# thread2 = Thread()
# #afficher les noms des 2 thread
# print(thread1.name)
# print(thread2.name)


#ex4
# thread = Thread()
# print(thread.daemon) #deamon c veut dire s'execute en ariere plant (pour la changer Thread(thread.daemon= true))
# thead = Thread(daemon = True)
# print(thread.daemon)

#ex5
# #thread vivant -->is_alive()
# def task():
#     sleep(1)
# thread = Thread(target=task)
# print (thread.is_alive())
# thread.start()
# print (thread.is_alive())
# thread.join()
# print (thread.is_alive())

# #ex6
# def task():
#     print ("commencer la tache ...")
#     sleep(1)
#     print ("terminer")
# start_time = perf_counter()
# t1 = Thread(target=task)
# t2 = Thread(target=task)
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# end_time = perf_counter()
# print("les taches ont pris: ", end_time-start_time)

#ex7
n= 0
lock = Lock()
def ajouter(val, lock):
    global n 
    lock.acquire()
    a = n
    a += val
    sleep(0.1)
    n = a
    print (f'n = {n}')
    lock.release()
t1 = Thread(target= ajouter, args=(10, lock))
t2 = Thread(target= ajouter, args=(20, lock))
t1.start()
t2.start()
t1.join()
t2.join()
print (f'la valeur final est: {n}')