import tkinter as tk
from PIL import Image, ImageTk
import math

# Paramètres principaux
a = "a"
b = "b"
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

# Taille des personnages
largeur_a, hauteur_a = perso_a_img_pil.size
largeur_b, hauteur_b = perso_b_img_pil.size

# Placement initial des personnages
pos_a = (0, fenetre_height // 2)  # bord gauche
pos_b = (fenetre_width, fenetre_height // 2)  # bord droit

# Affichage des personnages
canvas.create_image(pos_a[0], pos_a[1], image=perso_a_img, anchor="w")
canvas.create_image(pos_b[0], pos_b[1], image=perso_b_img, anchor="e")

# Variables globales
sending_count = 0
images_refs = []
text_id = None
queue = []  # file d'attente
rose_en_cours = False  # pour savoir si une rose est déjà en train d'être envoyée

def envoyer_rose():
    """Demander l'envoi d'une rose (ajouter à la file)"""
    queue.append(1)
    traiter_file()

def traiter_file():
    """Envoyer une rose si aucune n'est en cours"""
    global rose_en_cours
    if not rose_en_cours and queue:
        queue.pop(0)
        send()

def send():
    global rose_en_cours
    rose_en_cours = True
    rose = None
    rose_step = 0

    # Centre exact de départ et d'arrivée
    depart_x = pos_a[0] + largeur_a // 2
    depart_y = pos_a[1]
    arrivee_x = pos_b[0] - largeur_b // 2
    arrivee_y = pos_b[1]

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
            ajouter_texte()
            fin_envoi()

    animate()

def ajouter_texte():
    global sending_count, text_id
    sending_count += 1

    texte = f"{a} vous a envoyé {sending_count} rose" + ("s" if sending_count > 1 else "")
    
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

# Exemple d'utilisation
for e in range(10):
	envoyer_rose()

root.mainloop()