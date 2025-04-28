import tkinter as tk
from PIL import Image, ImageTk
import math

# Paramètres principaux
vitesse = 1  # millisecondes entre chaque mouvement
pas = 2  # pixels par mouvement

# Création de la fenêtre
root = tk.Tk()
root.title("Animation de rose")

# Taille écran
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Dimensions de la fenêtre
fenetre_width = int(screen_width * 0.8)
fenetre_height = int(screen_height * 0.8)

root.geometry(f"{fenetre_width}x{fenetre_height}")

# Création du canvas
canvas = tk.Canvas(root, width=fenetre_width, height=fenetre_height, bg="lightgray")
canvas.pack()

# Chargement des images
perso_a_img_pil = Image.open("perso_a.png")
perso_b_img_pil = Image.open("perso_b.png")

perso_a_img = ImageTk.PhotoImage(perso_a_img_pil)
perso_b_img = ImageTk.PhotoImage(perso_b_img_pil)
rose_img_original = Image.open("rose.png")  # chargé en PIL pour rotation

# Placement initial des personnages
pos_a = (0, fenetre_height // 2)  # bord gauche
pos_b = (fenetre_width, fenetre_height // 2)  # bord droit

# Dictionnaires pour les personnages
a = {
    "nom": "A",
    "image": perso_a_img,
    "largeur": perso_a_img_pil.size[0],
    "hauteur": perso_a_img_pil.size[1],
    "position": pos_a,
    "anchor": "w",
    "roses_count": {}  # dictionnaire {envoyeur: nombre de roses reçues}
}
b = {
    "nom": "B",
    "image": perso_b_img,
    "largeur": perso_b_img_pil.size[0],
    "hauteur": perso_b_img_pil.size[1],
    "position": pos_b,
    "anchor": "e",
    "roses_count": {}
}

# Affichage des personnages
canvas.create_image(pos_a[0], pos_a[1], image=a["image"], anchor=a["anchor"])
canvas.create_image(pos_b[0], pos_b[1], image=b["image"], anchor=b["anchor"])

# Variables globales
images_refs = []
text_id = None
queue = []  # file d'attente
rose_en_cours = False  # pour savoir si une rose est déjà en train d'être envoyée

# ----------- Fonctions -----------

def get_centre(perso, anchor):
    x, y = perso["position"]
    largeur = perso["largeur"]

    if anchor == "w":
        centre_x = x + largeur // 2
    elif anchor == "e":
        centre_x = x - largeur // 2
    else:
        centre_x = x
    return (centre_x, y)

def envoyer_rose(envoyeur=a, receveur=b):
    """Demander l'envoi d'une rose (ajouter à la file)"""
    queue.append((envoyeur, receveur))
    traiter_file()

def traiter_file():
    """Envoyer une rose si aucune n'est en cours"""
    global rose_en_cours
    if not rose_en_cours and queue:
        envoyeur, receveur = queue.pop(0)
        send(envoyeur, receveur)

def send(envoyeur, receveur):
    """Envoyer une rose de envoyeur à receveur"""
    global rose_en_cours
    rose_en_cours = True
    rose = None
    rose_step = 0

    depart_x, depart_y = get_centre(envoyeur, envoyeur["anchor"])
    arrivee_x, arrivee_y = get_centre(receveur, receveur["anchor"])

    distance_total = math.hypot(arrivee_x - depart_x, arrivee_y - depart_y)
    nombre_etapes = int(distance_total / pas)

    def animate():
        nonlocal rose, rose_step

        if rose_step == 0:
            rotated = rose_img_original.rotate(0)
            rose_img = ImageTk.PhotoImage(rotated)
            rose = canvas.create_image(depart_x, depart_y, image=rose_img)
            images_refs.append(rose_img)

        angle = 360 * rose_step / nombre_etapes
        x = depart_x + (arrivee_x - depart_x) * rose_step / nombre_etapes
        y = depart_y + (arrivee_y - depart_y) * rose_step / nombre_etapes

        rotated = rose_img_original.rotate(angle, expand=True)
        rose_img = ImageTk.PhotoImage(rotated)
        canvas.itemconfig(rose, image=rose_img)
        images_refs.append(rose_img)
        canvas.coords(rose, x, y)

        rose_step += 1

        if rose_step <= nombre_etapes:
            canvas.after(vitesse, animate)
        else:
            canvas.delete(rose)
            ajouter_texte(envoyeur, receveur)
            fin_envoi()

    animate()

def ajouter_texte(envoyeur, receveur):
    global text_id

    # Mise à jour du compteur de roses pour ce receveur
    nom_envoyeur = envoyeur["nom"]
    if nom_envoyeur not in receveur["roses_count"]:
        receveur["roses_count"][nom_envoyeur] = 0
    receveur["roses_count"][nom_envoyeur] += 1

    # Message à afficher
    count = receveur["roses_count"][nom_envoyeur]
    texte = f"{nom_envoyeur} a envoyé {count} rose" + ("s" if count > 1 else "") + f" à {receveur['nom']}"

    if text_id is None:
        text_id = canvas.create_text(
            fenetre_width // 2, 50,
            text=texte,
            font=("Arial", 20, "bold"),
            fill="red"
        )
    else:
        canvas.itemconfig(text_id, text=texte)

def fin_envoi():
    """Fin de l'envoi d'une rose"""
    global rose_en_cours
    rose_en_cours = False
    traiter_file()

# ----------- Exemple d'utilisation -----------

for e in range(5):
    envoyer_rose(a, b)  # Envoi de A à B
    envoyer_rose(b, a)  # Envoi de B à A

root.mainloop()
