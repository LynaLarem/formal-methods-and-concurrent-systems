from time import sleep
from threading import Thread, Lock

# Initialisation du compteur et du verrou
n = 0
lock = Lock()

# Fonction pour incrémenter le compteur
def compter(val):
    global n
    with lock:  # Sécuriser l'accès au compteur
        n += val
    print(f"Le compteur est de : {n}")

# Fonction pour surveiller le compteur (thread daemon)
def surveille():
    while True:  # Boucle infinie pour la surveillance
        sleep(1)
        with lock:  # Accès sécurisé à `n`
            print(f"Surveillance : Le compteur actuel est {n}")

# Création du thread daemon pour surveiller le compteur
t4 = Thread(target=surveille, daemon=True)
t4.start()

# Création des threads pour incrémenter le compteur
t1 = Thread(target=compter, args=(10,))
t2 = Thread(target=compter, args=(10,))
t3 = Thread(target=compter, args=(10,))

# Démarrage des threads
t1.start()
t2.start()
t3.start()

# Attendre la fin des threads normaux
t1.join()
t2.join()
t3.join()

print("Tous les threads ont fini. Le programme se termine.")











 
# Processus principal du coordinateur (rank 0)
if rank == 0:
    scilib = True  # La ressource est initialement libre
    while True:
        status = MPI.Status()
        message = comm.recv(source=MPI.ANY_SOURCE, status=status)  # Attente d'un message
        source = status.Get_source()
        
        if message == "demande" and scilib:  # Si la ressource est libre
            scilib = False  # La ressource est maintenant occupée
            comm.send("autorisation", dest=source)  # Autorisation donnée au site qui a demandé
        else:
            L.append(source)  # Ajout à la file FIFO si la ressource est occupée

        if message == "liberation":
            if L:  # Si des sites attendent
                next_site = L.pop(0)  # Récupère le premier de la file FIFO
                comm.send("autorisation", dest=next_site)  # Autorisation donnée au prochain site
            else:
                scilib = True  # La ressource est maintenant libre

# Processus des sites (rank différent de 0)
else:
    # Demande de la ressource
    comm.send("demande", dest=0)
    message = comm.recv(source=0)
    if message == "autorisation":
        print(f"Le site {rank} a reçu l'autorisation d'utiliser la ressource.")
        # Utilisation de la ressource pendant 2 secondes
        time.sleep(2)
        print(f"Le site {rank} a terminé l'utilisation de la ressource.")
        # Libération de la ressource
        comm.send("liberation", dest=0)