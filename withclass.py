import tkinter as tk
from PIL import Image, ImageTk
import math

# Paramètres globaux
VITESSE = 1
PAS = 2

class Personnage:
    def __init__(self, nom, image_pil, position, anchor):
        self.nom = nom
        self.image_pil = image_pil
        self.image = ImageTk.PhotoImage(image_pil)
        self.position = position
        self.anchor = anchor
        self.largeur = image_pil.size[0]
        self.hauteur = image_pil.size[1]
        self.roses_count = {}  # {envoyeur: nombre de roses reçues}

    def get_centre(self):
        x, y = self.position
        if self.anchor == "w":
            centre_x = x + self.largeur // 2
        elif self.anchor == "e":
            centre_x = x - self.largeur // 2
        else:
            centre_x = x
        return (centre_x, y)

class Rose:
    def __init__(self, canvas, image_pil, depart, arrivee, vitesse=VITESSE, pas=PAS):
        self.canvas = canvas
        self.image_pil = image_pil
        self.depart = depart
        self.arrivee = arrivee
        self.vitesse = vitesse
        self.pas = pas
        self.images_refs = []  # éviter le ramassage par le GC
        self.step = 0
        self.image_id = None

        # Calcul du nombre d'étapes
        distance_total = math.hypot(arrivee[0] - depart[0], arrivee[1] - depart[1])
        self.nombre_etapes = int(distance_total / pas)

    def start(self, callback_fin):
        self.callback_fin = callback_fin
        self.animate()

    def animate(self):
        if self.step == 0:
            rotated = self.image_pil.rotate(0)
            rose_img = ImageTk.PhotoImage(rotated)
            self.image_id = self.canvas.create_image(self.depart[0], self.depart[1], image=rose_img)
            self.images_refs.append(rose_img)

        angle = 360 * self.step / self.nombre_etapes
        x = self.depart[0] + (self.arrivee[0] - self.depart[0]) * self.step / self.nombre_etapes
        y = self.depart[1] + (self.arrivee[1] - self.depart[1]) * self.step / self.nombre_etapes

        rotated = self.image_pil.rotate(angle, expand=True)
        rose_img = ImageTk.PhotoImage(rotated)
        self.canvas.itemconfig(self.image_id, image=rose_img)
        self.images_refs.append(rose_img)
        self.canvas.coords(self.image_id, x, y)

        self.step += 1

        if self.step <= self.nombre_etapes:
            self.canvas.after(self.vitesse, self.animate)
        else:
            self.canvas.delete(self.image_id)
            self.callback_fin()

class Jeu:
    def __init__(self, root, perso_a, perso_b):
        self.root = root
        self.queue = []
        self.rose_en_cours = False
        self.images_refs = []
        self.text_id = None

        # Fenêtre
        self.screen_width = root.winfo_screenwidth()
        self.screen_height = root.winfo_screenheight()
        self.width = int(self.screen_width * 0.8)
        self.height = int(self.screen_height * 0.8)
        root.geometry(f"{self.width}x{self.height}")
        root.title("Animation de rose")

        # Canvas
        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="lightgray")
        self.canvas.pack()

        # Utilisation des personnages passés en argument
        self.a = perso_a
        self.b = perso_b

        # Placement des personnages sur le canvas
        self.canvas.create_image(*self.a.position, image=self.a.image, anchor=self.a.anchor)
        self.canvas.create_image(*self.b.position, image=self.b.image, anchor=self.b.anchor)

    def envoyer_rose(self, envoyeur, receveur, rose_img_pil):
        self.queue.append((envoyeur, receveur, rose_img_pil))
        self.traiter_file()

    def traiter_file(self):
        if not self.rose_en_cours and self.queue:
            envoyeur, receveur, rose_img_pil = self.queue.pop(0)
            self.send(envoyeur, receveur, rose_img_pil)

    def send(self, envoyeur, receveur, rose_img_pil):
        self.rose_en_cours = True
        depart = envoyeur.get_centre()
        arrivee = receveur.get_centre()

        rose = Rose(self.canvas, rose_img_pil, depart, arrivee)
        rose.start(lambda: self.fin_envoi(envoyeur, receveur))

    def fin_envoi(self, envoyeur, receveur):
        # Mettre à jour le compteur
        nom_envoyeur = envoyeur.nom
        if nom_envoyeur not in receveur.roses_count:
            receveur.roses_count[nom_envoyeur] = 0
        receveur.roses_count[nom_envoyeur] += 1

        # Texte
        count = receveur.roses_count[nom_envoyeur]
        texte = f"{nom_envoyeur} a envoyé {count} rose" + ("s" if count > 1 else "") + f" à {receveur.nom}"

        if self.text_id is None:
            self.text_id = self.canvas.create_text(
                self.width // 2, 50,
                text=texte,
                font=("Arial", 20, "bold"),
                fill="red"
            )
        else:
            self.canvas.itemconfig(self.text_id, text=texte)

        # Fin
        self.rose_en_cours = False
        self.traiter_file()

# ----------- Code principal -----------

if __name__ == "__main__":
    root = tk.Tk()

    # Chargement des images des personnages
    perso_a_img_pil = Image.open("perso_a.png")
    perso_b_img_pil = Image.open("perso_b.png")
    rose1 = Image.open("rose1.png")
    rose2 = Image.open("rose2.png")
    rose3 = Image.open("rose3.png")
    rose4 = Image.open("rose4.png").convert("RGBA")

    # Création des personnages en dehors de Jeu
    perso_a = Personnage("A", perso_a_img_pil, (0, int(root.winfo_screenheight() * 0.8) // 2), "w")
    perso_b = Personnage("B", perso_b_img_pil, (int(root.winfo_screenwidth() * 0.8), int(root.winfo_screenheight() * 0.8) // 2), "e")

    # Création du jeu avec les personnages déjà créés
    jeu = Jeu(root, perso_a, perso_b)

    # Exemples d'envoi avec des roses différentes
    for e in range(5):
        jeu.envoyer_rose(jeu.a, jeu.b, rose2)
        jeu.envoyer_rose(jeu.b, jeu.a, rose1)
        jeu.envoyer_rose(jeu.a, jeu.b, rose4)

    root.mainloop()
