# Implémentation de l'algorithme de Karp & Miller
# Arbre de couverture des réseaux de Petri

# Représentation d'un marquage : liste d'entiers ou "w" (omega)


class Noeud:
    """
    Classe représentant un nœud de l'arbre de couverture
    """

    def __init__(self, marquage, parent=None, transition=None):
        self.marquage = marquage # Marquage au niveau de ce nœud
        self.parent = parent     # Réference au nœud parent (pour retracer le chemin)
        self.transition = transition   # Transition utilisee pour arriver à ce marquage depuis le parent
        self.etat = "new"      # new, old, dead-end
        self.fils = []         # enfants dans l'arbre
        
        #Memoriser les marquages du chemin directement dans le nœud (pour eviter de recalculer plusieurs fois le chemin racine-noud)
        if parent is None:
            self.chemin_marques = {tuple(marquage)}
        else:
            self.chemin_marques = parent.chemin_marques | {tuple(marquage)}

#Fonctions utilitaires
def tirer_transition(marquage, transition):
    """
    Calcule le marquage après tir d'une transition :
    M' = M - pre + post
    """
    pre = transition["pre"]
    post = transition["post"]
    nouveau = []

    for i in range(len(marquage)):
        if marquage[i] == "w":  # Si le marquage est infini, il reste infini
            nouveau.append("w")
        else:
            nouveau.append(marquage[i] - pre[i] + post[i])  #sinon appliquer la formule

    return nouveau


def chemin_vers_racine(noeud):
    """
    Retourne la liste des marquages depuis la racine jusqu'au noeud
    utilisation :
    - vérifier si un marquage est déjà présent (old)
    -introduire ω lorsqu'un marquage couvre un ancêtre
    """
    chemin = []
    courant = noeud

    while courant is not None:
        chemin.append(courant.marquage)
        courant = courant.parent

    chemin.reverse()
    return chemin


def marquages_identiques(m1, m2):
    """
    Vérifie si deux marquages sont identiques
    """
    if len(m1) != len(m2):
        return False

    for i in range(len(m1)):
        if m1[i] != m2[i]:
            return False

    return True


def marquage_deja_vu(noeud, marquage):
    """
    Verifie si un marquage existe deja sur le chemin racine → noeud
    Pour: 
    -  evite d'explorer un marquage deja vu sur le chemin → evite les boucles infinies dans l'arbre
    """
    if noeud is None:
        return False
    return tuple(marquage) in noeud.chemin_marques


def transition_tirable(marquage, transition):
    """
    Verifie si une transition est tirable depuis un marquage
    """
    pre = transition["pre"]

    for i in range(len(pre)):
        if marquage[i] == "w":
            continue
        if marquage[i] < pre[i]:
            return False

    return True


def transitions_tirables(marquage, liste_transitions):
    """
    Liste des transitions tirables depuis un marquage
    """
    return [t for t in liste_transitions if transition_tirable(marquage, t)]



def marquage_couvre(m1, m2):
    """
    
    Vérifie si m1 couvre m2 --> condition pour introduire W (Retourne True si m1 >= m2)
    Importance -->pour transformer des reseaux infinis en arbres finis (karp&miller)
    """
    for i in range(len(m1)):
        if m1[i] == "w":
            continue
        if m2[i] == "w":
            return False
        if m1[i] < m2[i]:
            return False

    return True


def introduire_w(m_prime, m_double_prime):
    """
    Introduit W là où m' > m''
    Donc c Remplacer les valeurs croissantes par W pour representer des places non bornees
    """
    nouveau = m_prime.copy()

    for i in range(len(m_prime)):
        if m_prime[i] == "w":
            continue
        if m_double_prime[i] == "w":
            continue
        if m_prime[i] > m_double_prime[i]:
            nouveau[i] = "w"

    return nouveau


def karp_miller(m0, transitions):
    
    """
    Etapes: 
    1- on cree la racine de l'arbre avec le marquage initial M0 
    2- on boucle tant qu'il reste des nœuds "new" (pile) donc qu'il ne sont pas encore explores 
    3- on verifie si le marquage a deja ete vu → old (pour evite boucle infinie) 
    4- on cherche les transitions tirables 
    - marquer dead-end si aucune transition n'est tirable 
    6- pour chaque transition tirable: 
         -tire la transition → nouveau marquage m' 
         -vérifie si m_prime couvre un ancetre → introduit W si nécessaire 
         -crée un enfant dans l'arbre, relie le parent 
         -si l'enfant n'a pas deja ete vu → ajoute à la pile pour exploration 
    7- si aucun fils n'est ajoute il n'y a aucune transition tirable depuis ce marquage), marquer dead-end.
    """
    #1- on cree la racine de l'arbre avec le marquage initial M0
    racine = Noeud(m0)
    pile = [racine]

    #2- on boucle tant qu'il reste des nœuds "new" (pile) donc qu'il ne sont pas encore explores
    while pile:
        noeud = pile.pop()
        #3- on verifie si le marquage a deja ete vu → old (pour evite boucle infinie)
        if marquage_deja_vu(noeud.parent, noeud.marquage):
            noeud.etat = "old"
            continue

        #4- on cherche les transitions tirables
        noeud.etat = "old"
        tirables = transitions_tirables(noeud.marquage, transitions)

        # 5- marquer dead-end si aucune transition n'est tirable 
        if not tirables:
            noeud.etat = "dead-end"
            continue

        ## indique si au moins un nouveau fils a ete ajoute
        nouveau_fils = False

        # 6- pour chaque transition tirable
        for t in tirables:
        
            #-tire la transition → nouveau marquage m'
            m_prime = tirer_transition(noeud.marquage, t)

            #-vérifie si m_prime couvre un ancetre → introduit W si nécessaire
            for ancetre in chemin_vers_racine(noeud):
                if marquage_couvre(m_prime, ancetre) and not marquages_identiques(m_prime, ancetre):
                    m_prime = introduire_w(m_prime, ancetre)


            # -crée un enfant dans l'arbre, relie le parent
            enfant = Noeud(m_prime, noeud, t["nom"])
            noeud.fils.append(enfant)

            #-si l'enfant n'a pas deja ete vu → ajoute à la pile pour exploration
            if not marquage_deja_vu(noeud, m_prime):
                pile.append(enfant)
                nouveau_fils = True
            else:
                enfant.etat = "old"


        #7- si aucun fils n'est ajoute il n'y a aucune transition tirable depuis ce marquage), marquer dead-end
        if not nouveau_fils:
            noeud.etat = "dead-end"

    return racine
        

def afficher_arbre(noeud, prefix="", est_dernier=True):

    # Determination de la branche ASCII
    branche = "└── " if est_dernier else "├── "
    transition = f"{noeud.transition} → " if noeud.transition else ""

    # Afficher l'etat uniquement si c'est un dead-end
    etat = " [dead-end]" if noeud.etat == "dead-end" else ""

    # Affichage du noeud courant
    print(prefix + branche + transition + f"{tuple(noeud.marquage)}" + etat)

    # Préparer le préfixe pour les enfants
    nouveau_prefix = prefix + ("    " if est_dernier else "│   ")

    # Affichage récursif des enfants
    for i, fils in enumerate(noeud.fils):
        est_dernier_fils = (i == len(noeud.fils) - 1)
        afficher_arbre(fils, nouveau_prefix, est_dernier_fils)
        


#tester la bornetude
def est_borne(racine):
    """
True si le reseau est borne, False sinon
    """
    pile = [racine]

    while pile:
        noeud = pile.pop()

        # Si un w apparait, le reseau est non borne
        if "w" in noeud.marquage:
            return False

        pile.extend(noeud.fils)

    return True



#test vivacite (Qasi-vivacite)
def est_vivant(racine, transitions):
    """
    Vérifie une vivacité faible :
    chaque transition apparait au moins une fois dans l'arbre
    """
    transitions_vues = set()
    pile = [racine]

    while pile:
        noeud = pile.pop()

        if noeud.transition:
            transitions_vues.add(noeud.transition)

        pile.extend(noeud.fils)

    noms_transitions = {t["nom"] for t in transitions}

    return noms_transitions.issubset(transitions_vues)

        
        
# Exemple2 de test

M0 = [1, 0, 0]

transitions = [
    # t1 
    {"nom": "t0", "pre": [1, 0, 0], "post": [0, 1, 0]}, 
    
    # t2 
    {"nom": "t1", "pre": [0, 1, 0], "post": [1, 0, 1]},

]



racine = karp_miller(M0, transitions)
print("\n 1. Affichage de l'arbre de couverture: \n")   
afficher_arbre(racine)


print("\n========================================================")


print("\n 2. Test de bornitude :\n")
if est_borne(racine):
    print("Le réseau de Petri est BORNE.")
else:
    print("Le réseau de Petri est NON BORNE.")

print("\n 3. Test de la vivacité faible(faible) :\n")
if est_vivant(racine, transitions):
    print("Le réseau est vivant (vivacité faible).")
else:
    print("Le réseau n'est pas vivant.")
    
    
print("\n==================================================================================================================")   
    
# Exemple de test

M0 = [0, 1, 0, 1, 0]


transitions = [
    # t1 
    {"nom": "t1", "pre": [1, 0, 1, 1, 0], "post": [0, 1, 0, 0, 0]}, 
    
    # t2 
    {"nom": "t2", "pre": [0, 1, 0, 0, 0], "post": [1, 0, 0, 0, 0]},

    # t3 
    {"nom": "t3", "pre": [0, 0, 0, 0, 1], "post": [0, 0, 1, 1, 0]}, 
    
     # t4  
    {"nom": "t4", "pre": [0, 0, 0, 1, 0], "post": [0, 0, 0, 0, 1]},
]

racine = karp_miller(M0, transitions)
print("\n 1. Affichage de l'arbre de couverture: \n")   
afficher_arbre(racine)


print("\n==================================================================================================================")


print("\n 2. Test de bornitude :\n")
if est_borne(racine):
    print("Le réseau de Petri est BORNE.")
else:
    print("Le réseau de Petri est NON BORNE.")

print("\n 3. Test de la vivacité faible(faible) :\n")
if est_vivant(racine, transitions):
    print("Le réseau est vivant (vivacité faible).")
else:
    print("Le réseau n'est pas vivant.")
    