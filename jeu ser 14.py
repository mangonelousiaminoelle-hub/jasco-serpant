import pygame
import math
import random
import sys
import os
import json
import threading
import winsound
import time

pygame.init()
pygame.font.init()

LARGEUR, HAUTEUR = 1280, 720
FPS = 60
ECRAN = pygame.display.set_mode((LARGEUR, HAUTEUR))
pygame.display.set_caption("JASCO SERPENT")
HORLOGE = pygame.time.Clock()
FICHIER_DONNEES = "sauvegarde_snake.json"

SKINS_CATALOGUE = {
    "Galaxie Spatiale": {
        "prix": 0, "debloque": True,
        "couleurs_serpent": [("#8A2BE2", "#4B0082", "#E6E6FA"), ("#00FFFF", "#008B8B", "#E0FFFF")],
        "couleur_yeux": (0, 255, 255), "couleur_langue": (255, 0, 127),
        "ui_principale": (0, 255, 255), "ui_secondaire": (138, 43, 226), "ui_fond": (5, 5, 12)
    },
    "Nébuleuse Rose": {
        "prix": 40, "debloque": False,
        "couleurs_serpent": [("#FF007F", "#99004C", "#FF99DD"), ("#FF66CC", "#CC0088", "#FFFFFF")],
        "couleur_yeux": (255, 255, 255), "couleur_langue": (0, 255, 255),
        "ui_principale": (255, 0, 127), "ui_secondaire": (255, 102, 204), "ui_fond": (10, 2, 7)
    },
    "Cyberpunk": {
        "prix": 100, "debloque": False,
        "couleurs_serpent": [("#FF2A6D", "#B81347", "#FF6699"), ("#05D9E8", "#008B9B", "#65F5FF")],
        "couleur_yeux": (5, 217, 232), "couleur_langue": (255, 42, 109),
        "ui_principale": (5, 217, 232), "ui_secondaire": (255, 42, 109), "ui_fond": (8, 11, 16)
    },
    "Supernova Or": {
        "prix": 200, "debloque": False,
        "couleurs_serpent": [("#FFD700", "#B8860B", "#FFF8DC"), ("#FFA500", "#CC7A00", "#FFE4B5")],
        "couleur_yeux": (255, 255, 255), "couleur_langue": (255, 0, 0),
        "ui_principale": (255, 215, 0), "ui_secondaire": (255, 165, 0), "ui_fond": (20, 16, 3)
    },
    "Trou Noir": {
        "prix": 400, "debloque": False,
        "couleurs_serpent": [("#FF3300", "#990000", "#FF6633"), ("#FF9900", "#CC6600", "#FFCC00")],
        "couleur_yeux": (255, 204, 0), "couleur_langue": (255, 255, 255),
        "ui_principale": (255, 51, 0), "ui_secondaire": (255, 153, 0), "ui_fond": (15, 3, 3)
    }
}

class EtoileFilante:
    def __init__(self):
        self.reinitialiser()

    def reinitialiser(self):
        self.x = random.randint(0, LARGEUR // 2)
        self.y = random.randint(0, HAUTEUR // 2)
        self.longueur = random.randint(50, 120)
        self.vitesse = random.uniform(15, 25)
        self.active = False

    def mettre_a_jour(self):
        if self.active:
            self.x += self.vitesse
            self.y += self.vitesse * 0.5
            if self.x > LARGEUR or self.y > HAUTEUR:
                self.reinitialiser()
        elif random.random() < 0.01:
            self.active = True

class EtoileSpatiale:
    def __init__(self):
        self.x = random.randint(0, LARGEUR)
        self.y = random.randint(0, HAUTEUR)
        self.taille = random.choice([1, 2, 3])
        self.luminosite = random.uniform(0.2, 1.0)
        self.vitesse_scintillement = random.uniform(0.02, 0.08)
        self.direction = 1

    def mettre_a_jour(self):
        self.luminosite += self.vitesse_scintillement * self.direction
        if self.luminosite >= 1.0:
            self.luminosite = 1.0
            self.direction = -1
        elif self.luminosite <= 0.2:
            self.luminosite = 0.2
            self.direction = 1

class SerpentMenuOndulant:
    def __init__(self):
        self.reinitialiser()

    def reinitialiser(self):
        self.taille = 15
        self.vitesse = random.uniform(2.0, 4.0)
        self.angle = random.uniform(0, math.pi * 2)
        self.x = random.randint(150, LARGEUR - 150)
        self.y = random.randint(150, HAUTEUR - 150)
        self.phase = random.uniform(0, 10)
        self.corps = [(self.x - i * 18, self.y) for i in range(self.taille)]

    def deplacer(self):
        self.phase += 0.1
        self.angle += math.sin(self.phase) * 0.1
        self.x += math.cos(self.angle) * self.vitesse
        self.y += math.sin(self.angle) * self.vitesse
        self.corps.insert(0, (self.x, self.y))
        self.corps.pop()
        if self.x < -100 or self.x > LARGEUR + 100 or self.y < -100 or self.y > HAUTEUR + 100:
            self.reinitialiser()

class JeuDuSerpentSpatialeHD:
    def __init__(self):
        self.argent = 0
        self.meilleur_score = 0
        self.skin_equipe = "Galaxie Spatiale"
        self.charger_donnees()

        self.etoiles = [EtoileSpatiale() for _ in range(150)]
        self.etoiles_filantes = [EtoileFilante() for _ in range(3)]
        self.serpents_menu = [SerpentMenuOndulant() for _ in range(5)]

        self.etat = "MENU"
        self.boost = False
        self.particules = []
        self.textes_flottants = []

        self.son_active = True
        self.volume = 5

        self.serpent = []
        self.direction = "Right"
        self.prochaine_direction = "Right"
        self.score = 0
        self.vies = 3
        self.invulnerable = False
        self.timer_invulnerable = 0
        self.pieces_sur_terrain = []
        self.timer_spawn_piece = 0
        self.comete = None
        self.obstacles = []
        self.pomme = [0, 0]
        self.vitesse_ticks = 100

        self.tick_animation = 0
        self.font_titre = pygame.font.SysFont("Impact", 56)
        self.font_moyen = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_petit = pygame.font.SysFont("Segoe UI", 16)

        self.lancer_musique_menu()

    def charger_donnees(self):
        if os.path.exists(FICHIER_DONNEES):
            try:
                with open(FICHIER_DONNEES, "r") as f:
                    data = json.load(f)
                    self.argent = data.get("argent", 0)
                    self.meilleur_score = data.get("meilleur_score", 0)
                    self.skin_equipe = data.get("skin_equipe", "Galaxie Spatiale")
                    debloques = data.get("skins_debloques", ["Galaxie Spatiale"])
                    for s in debloques:
                        if s in SKINS_CATALOGUE:
                            SKINS_CATALOGUE[s]["debloque"] = True
            except: pass

    def sauvegarder_donnees(self):
        debloques = [nom for nom, info in SKINS_CATALOGUE.items() if info["debloque"]]
        data = {
            "argent": self.argent,
            "meilleur_score": self.meilleur_score,
            "skin_equipe": self.skin_equipe,
            "skins_debloques": debloques
        }
        with open(FICHIER_DONNEES, "w") as f:
            json.dump(data, f)

    def jouer_melodie_menu(self):
        # Mélodie rythmée style "Khadirov Mania"
        notes = [(480, 90), (580, 90), (720, 140), (580, 90), (480, 90), (360, 180), (480, 90), (720, 200)]
        while self.etat == "MENU":
            for freq, duree in notes:
                if self.etat != "MENU": break
                if self.son_active:
                    try:
                        winsound.Beep(int(freq), duree)
                    except: pass
                time.sleep(0.025)
            time.sleep(0.2)

    def lancer_musique_menu(self):
        threading.Thread(target=self.jouer_melodie_menu, daemon=True).start()

    def jouer_son(self, type_son):
        if not self.son_active: return
        def faire_bip():
            try:
                freq = 2500 if type_son == "comete" else (2000 if type_son == "piece" else (1400 if type_son == "manger" else 280))
                duree = 60 if type_son in ["comete", "piece", "manger"] else 120
                winsound.Beep(freq, duree)
            except: pass
        threading.Thread(target=faire_bip, daemon=True).start()

    def ajouter_texte_flottant(self, x, y, texte, couleur="#FFFFFF"):
        self.textes_flottants.append([x, y, texte, couleur, 40])

    def ajouter_particules(self, x, y, couleur_hex, nombre=12):
        c = tuple(int(couleur_hex[i:i+2], 16) for i in (1, 3, 5))
        for _ in range(nombre):
            self.particules.append([x, y, random.uniform(-5, 5), random.uniform(-5, 5), random.randint(15, 30), c])

    def dessiner_espace(self, surface, theme):
        surface.fill(theme["ui_fond"])
        pulse = math.sin(self.tick_animation * 0.03) * 30
        
        s_surf = pygame.Surface((600, 600), pygame.SRCALPHA)
        pygame.draw.circle(s_surf, (*theme["ui_secondaire"], 15), (300, 300), 250 + int(pulse))
        surface.blit(s_surf, (-100, -100))

        s_surf2 = pygame.Surface((600, 600), pygame.SRCALPHA)
        pygame.draw.circle(s_surf2, (*theme["ui_principale"], 15), (300, 300), 300 - int(pulse))
        surface.blit(s_surf2, (LARGEUR - 400, HAUTEUR - 400))

        for etoile in self.etoiles:
            etoile.mettre_a_jour()
            alpha = int(etoile.luminosite * 255)
            pygame.draw.circle(surface, (alpha, alpha, alpha), (int(etoile.x), int(etoile.y)), etoile.taille)

        for ef in self.etoiles_filantes:
            ef.mettre_a_jour()
            if ef.active:
                pygame.draw.line(surface, (255, 255, 255), (ef.x, ef.y), (ef.x - ef.longueur, int(ef.y - ef.longueur * 0.5)), 2)

    def position_aleatoire(self):
        while True:
            x = random.randint(50, LARGEUR - 50)
            y = random.randint(80, HAUTEUR - 50)
            x = (x // 25) * 25
            y = (y // 25) * 25
            pos = [x, y]
            if pos not in self.serpent and pos not in self.obstacles:
                return pos

    def demarrer_jeu(self, difficulte):
        self.etat = "JEU"
        if difficulte == 1: self.vitesse_ticks, num_obs = 120, 0
        elif difficulte == 2: self.vitesse_ticks, num_obs = 90, 6
        else: self.vitesse_ticks, num_obs = 70, 14

        hx, hy = (LARGEUR // 2 // 25) * 25, (HAUTEUR // 2 // 25) * 25
        self.serpent = [[hx - i * 25, hy] for i in range(5)]
        self.direction = "Right"
        self.prochaine_direction = "Right"
        self.score = 0
        self.vies = 3
        self.invulnerable = False
        self.timer_invulnerable = 0
        self.pieces_sur_terrain = []
        self.timer_spawn_piece = 0
        self.comete = None

        self.obstacles = [self.position_aleatoire() for _ in range(num_obs)]
        self.pomme = self.position_aleatoire()

    def run(self):
        while True:
            self.tick_animation += 1
            theme = SKINS_CATALOGUE[self.skin_equipe]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    touche = event.key
                    if self.etat == "MENU":
                        if touche in [pygame.K_1, pygame.K_KP1]: self.demarrer_jeu(1)
                        elif touche in [pygame.K_2, pygame.K_KP2]: self.demarrer_jeu(2)
                        elif touche in [pygame.K_3, pygame.K_KP3]: self.demarrer_jeu(3)
                        elif touche == pygame.K_b: self.etat = "BOUTIQUE"
                    elif self.etat == "BOUTIQUE":
                        if touche in [pygame.K_ESCAPE, pygame.K_b]:
                            self.etat = "MENU"
                            self.lancer_musique_menu()
                        elif touche in [pygame.K_1, pygame.K_KP1, pygame.K_2, pygame.K_KP2, pygame.K_3, pygame.K_KP3, pygame.K_4, pygame.K_KP4, pygame.K_5, pygame.K_KP5]:
                            mapping = {pygame.K_1: 0, pygame.K_KP1: 0, pygame.K_2: 1, pygame.K_KP2: 1, pygame.K_3: 2, pygame.K_KP3: 2, pygame.K_4: 3, pygame.K_KP4: 3, pygame.K_5: 4, pygame.K_KP5: 4}
                            idx = mapping.get(touche, 0)
                            noms = list(SKINS_CATALOGUE.keys())
                            if idx < len(noms):
                                nom_skin = noms[idx]
                                info = SKINS_CATALOGUE[nom_skin]
                                if info["debloque"]:
                                    self.skin_equipe = nom_skin
                                    self.sauvegarder_donnees()
                                elif self.argent >= info["prix"]:
                                    self.argent -= info["prix"]
                                    info["debloque"] = True
                                    self.skin_equipe = nom_skin
                                    self.sauvegarder_donnees()
                    elif self.etat == "JEU":
                        if touche in [pygame.K_UP, pygame.K_z] and self.direction != "Down": self.prochaine_direction = "Up"
                        elif touche in [pygame.K_DOWN, pygame.K_s] and self.direction != "Up": self.prochaine_direction = "Down"
                        elif touche in [pygame.K_LEFT, pygame.K_q] and self.direction != "Right": self.prochaine_direction = "Left"
                        elif touche in [pygame.K_RIGHT, pygame.K_d] and self.direction != "Left": self.prochaine_direction = "Right"
                        elif touche in [pygame.K_SPACE, pygame.K_LSHIFT]: self.boost = True
                        elif touche == pygame.K_p: self.etat = "PAUSE"
                    elif self.etat == "PAUSE_IMPACT":
                        if touche in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_z, pygame.K_s, pygame.K_q, pygame.K_d]:
                            if touche in [pygame.K_UP, pygame.K_z] and self.direction != "Down": self.prochaine_direction = "Up"
                            elif touche in [pygame.K_DOWN, pygame.K_s] and self.direction != "Up": self.prochaine_direction = "Down"
                            elif touche in [pygame.K_LEFT, pygame.K_q] and self.direction != "Right": self.prochaine_direction = "Left"
                            elif touche in [pygame.K_RIGHT, pygame.K_d] and self.direction != "Left": self.prochaine_direction = "Right"
                            self.etat = "JEU"
                    elif self.etat == "PAUSE":
                        if touche == pygame.K_p: self.etat = "JEU"
                    elif self.etat == "GAMEOVER":
                        if touche == pygame.K_r:
                            self.etat = "MENU"
                            self.lancer_musique_menu()
                elif event.type == pygame.KEYUP:
                    if event.key in [pygame.K_SPACE, pygame.K_LSHIFT]:
                        self.boost = False

            if self.etat == "JEU":
                if self.invulnerable:
                    self.timer_invulnerable -= 1
                    if self.timer_invulnerable <= 0:
                        self.invulnerable = False

                self.timer_spawn_piece += 1
                if self.timer_spawn_piece > 120 and len(self.pieces_sur_terrain) < 3:
                    self.timer_spawn_piece = 0
                    if random.random() < 0.6:
                        self.pieces_sur_terrain.append(self.position_aleatoire())

                if not self.comete and random.random() < 0.005:
                    self.comete = [0.0, float(random.randint(100, HAUTEUR - 100)), 6.0, 2.0]

                if self.comete:
                    self.comete[0] += self.comete[2]
                    self.comete[1] += self.comete[3]
                    if self.comete[0] > LARGEUR or self.comete[1] > HAUTEUR:
                        self.comete = None

                self.direction = self.prochaine_direction
                hx, hy = self.serpent[0]

                if self.direction == "Up": hy -= 25
                elif self.direction == "Down": hy += 25
                elif self.direction == "Left": hx -= 25
                elif self.direction == "Right": hx += 25

                # Mode Pac-Man : Traverser les murs et ressortir de l'autre côté (si bouclier actif ou par défaut)
                if self.invulnerable:
                    if hx < 20: hx = LARGEUR - 45
                    elif hx >= LARGEUR - 20: hx = 20
                    if hy < 55: hy = HAUTEUR - 25
                    elif hy >= HAUTEUR - 20: hy = 55
                else:
                    # Murs normaux si pas de bouclier
                    if hx < 20 or hx >= LARGEUR - 20 or hy < 55 or hy >= HAUTEUR - 20:
                        self.vies -= 1
                        self.jouer_son("collision")
                        if self.vies <= 0:
                            self.etat = "GAMEOVER"
                            if self.score > self.meilleur_score:
                                self.meilleur_score = self.score
                            self.sauvegarder_donnees()
                        else:
                            self.invulnerable = True
                            self.timer_invulnerable = 40
                            hx_c, hy_c = (LARGEUR // 2 // 25) * 25, (HAUTEUR // 2 // 25) * 25
                            self.serpent = [[hx_c - i * 25, hy_c] for i in range(5)]
                            self.direction = "Right"
                            self.prochaine_direction = "Right"
                            self.etat = "PAUSE_IMPACT"
                        continue

                nouvelle_tete = [hx, hy]

                if nouvelle_tete in self.serpent or nouvelle_tete in self.obstacles:
                    if not self.invulnerable:
                        self.vies -= 1
                        self.jouer_son("collision")
                        if self.vies <= 0:
                            self.etat = "GAMEOVER"
                            if self.score > self.meilleur_score:
                                self.meilleur_score = self.score
                            self.sauvegarder_donnees()
                        else:
                            self.invulnerable = True
                            self.timer_invulnerable = 40
                            hx_c, hy_c = (LARGEUR // 2 // 25) * 25, (HAUTEUR // 2 // 25) * 25
                            self.serpent = [[hx_c - i * 25, hy_c] for i in range(5)]
                            self.direction = "Right"
                            self.prochaine_direction = "Right"
                            self.etat = "PAUSE_IMPACT"
                    if self.etat != "JEU": 
                        continue

                self.serpent.insert(0, nouvelle_tete)

                if hx == self.pomme[0] and hy == self.pomme[1]:
                    self.score += 10
                    self.jouer_son("manger")
                    self.ajouter_particules(hx + 12, hy + 12, "#FF2A6D", 15)
                    self.pomme = self.position_aleatoire()
                else:
                    self.serpent.pop()

                piece_mangee = None
                for p in self.pieces_sur_terrain:
                    if hx == p[0] and hy == p[1]:
                        piece_mangee = p
                        break
                if piece_mangee:
                    self.pieces_sur_terrain.remove(piece_mangee)
                    self.argent += 5
                    self.jouer_son("piece")
                    self.ajouter_texte_flottant(hx, hy, "+5 🪙", "#FFD700")
                    self.ajouter_particules(hx + 12, hy + 12, "#FFD700", 20)
                    self.sauvegarder_donnees()

                if self.comete:
                    if math.hypot(hx - self.comete[0], hy - self.comete[1]) < 25:
                        self.argent += 20
                        self.jouer_son("comete")
                        self.ajouter_texte_flottant(hx, hy, "+20 COMÈTE! 🌠", "#FFD700")
                        self.ajouter_particules(int(self.comete[0]), int(self.comete[1]), "#FFD700", 30)
                        self.comete = None
                        self.sauvegarder_donnees()

            # --- RENDU GRAPHIQUE ---
            self.dessiner_espace(ECRAN, theme)

            if self.etat == "MENU":
                for s in self.serpents_menu:
                    s.deplacer()
                    for i, (cx, cy) in enumerate(s.corps):
                        r = max(3, 11 - i * 0.5)
                        pygame.draw.circle(ECRAN, theme["ui_principale"], (int(cx), int(cy)), int(r))

                t_surf = self.font_titre.render("JASCO SERPENT", True, theme["ui_principale"])
                ECRAN.blit(t_surf, (LARGEUR // 2 - t_surf.get_width() // 2, 80))

                cred_surf = self.font_moyen.render(f"🪙 CRÉDITS : {self.argent} | SKIN : {self.skin_equipe.upper()}", True, (255, 215, 0))
                ECRAN.blit(cred_surf, (LARGEUR // 2 - cred_surf.get_width() // 2, 150))

                pygame.draw.rect(ECRAN, (5, 7, 20), (LARGEUR // 2 - 160, 190, 320, 45), border_radius=8)
                pygame.draw.rect(ECRAN, (255, 215, 0), (LARGEUR // 2 - 160, 190, 320, 45), 2, border_radius=8)
                b_surf = self.font_moyen.render("🛸 BOUTIQUE DES SKINS (B)", True, (255, 215, 0))
                ECRAN.blit(b_surf, (LARGEUR // 2 - b_surf.get_width() // 2, 200))

                diffs = [
                    ("1 - EXPÉDITION", "Vitesse réduite & Sans astéroïdes", theme["ui_principale"], 280),
                    ("2 - ORBITE", "Vitesse normale + 6 Astéroïdes", (255, 159, 28), 370),
                    ("3 - TROU NOIR", "Vitesse extrême + 14 Astéroïdes", theme["ui_secondaire"], 460)
                ]
                for titre, desc, col, y in diffs:
                    pygame.draw.rect(ECRAN, (5, 7, 20), (LARGEUR // 2 - 240, y, 480, 65), border_radius=10)
                    pygame.draw.rect(ECRAN, col, (LARGEUR // 2 - 240, y, 480, 65), 2, border_radius=10)
                    st = self.font_moyen.render(titre, True, col)
                    sd = self.font_petit.render(desc, True, (160, 175, 200))
                    ECRAN.blit(st, (LARGEUR // 2 - st.get_width() // 2, y + 10))
                    ECRAN.blit(sd, (LARGEUR // 2 - sd.get_width() // 2, y + 35))

                tuto = self.font_moyen.render("Touches 1, 2, 3 pour jouer | Espace: Turbo Boost", True, (255, 255, 255))
                ECRAN.blit(tuto, (LARGEUR // 2 - tuto.get_width() // 2, 630))

            elif self.etat == "BOUTIQUE":
                t_surf = self.font_titre.render("🛸 BOUTIQUE SPATIALE", True, (255, 215, 0))
                ECRAN.blit(t_surf, (LARGEUR // 2 - t_surf.get_width() // 2, 40))
                c_surf = self.font_moyen.render(f"Crédits Spatiaux : {self.argent} 🪙", True, (255, 255, 255))
                ECRAN.blit(c_surf, (LARGEUR // 2 - c_surf.get_width() // 2, 110))

                y_pos = 170
                for i, (nom, info) in enumerate(SKINS_CATALOGUE.items()):
                    est_equipe = (nom == self.skin_equipe)
                    statut = "ÉQUIPÉ" if est_equipe else ("DÉBLOQUÉ" if info["debloque"] else f"PRIX: {info['prix']} 🪙")
                    col_bord = (0, 255, 102) if est_equipe else (info["ui_principale"] if info["debloque"] else (70, 85, 105))

                    pygame.draw.rect(ECRAN, (11, 14, 38), (200, y_pos, LARGEUR - 400, 60), border_radius=8)
                    pygame.draw.rect(ECRAN, col_bord, (200, y_pos, LARGEUR - 400, 60), 2, border_radius=8)

                    nt_surf = self.font_moyen.render(f"{i+1}. {nom}", True, info["ui_principale"])
                    st_surf = self.font_moyen.render(statut, True, (255, 215, 0) if not info["debloque"] else (255, 255, 255))
                    ECRAN.blit(nt_surf, (230, y_pos + 15))
                    ECRAN.blit(st_surf, (LARGEUR - 230 - st_surf.get_width(), y_pos + 15))
                    y_pos += 75

                info_b = self.font_moyen.render("Appuie sur (1-5) pour acheter/équiper | (B ou ÉCHAP) pour quitter", True, (160, 175, 200))
                ECRAN.blit(info_b, (LARGEUR // 2 - info_b.get_width() // 2, 630))

            elif self.etat in ["JEU", "PAUSE_IMPACT", "PAUSE"]:
                for x in range(0, LARGEUR, 25): pygame.draw.line(ECRAN, (20, 24, 52), (x, 55), (x, HAUTEUR), 1)
                for y in range(55, HAUTEUR, 25): pygame.draw.line(ECRAN, (20, 24, 52), (0, y), (LARGEUR, y), 1)

                pygame.draw.rect(ECRAN, (8, 10, 28), (0, 0, LARGEUR, 55))
                pygame.draw.line(ECRAN, theme["ui_principale"], (0, 55), (LARGEUR, 55), 2)

                sc_surf = self.font_moyen.render(f"SCORE: {self.score}", True, theme["ui_principale"])
                ECRAN.blit(sc_surf, (30, 14))

                # Affichage explicite et joli des 3 cœurs ❤️❤️❤️
                vies_texte = "VIES : "
                ECRAN.blit(self.font_moyen.render(vies_texte, True, (255, 42, 109)), (220, 14))
                offset_c = 220 + self.font_moyen.size(vies_texte)[0]
                for c_idx in range(self.vies):
                    pygame.draw.circle(ECRAN, (255, 42, 109), (offset_c + c_idx * 22 + 8, 24), 7)
                
                if self.invulnerable:
                    sh_surf = self.font_moyen.render(" 🛡️ BOUCLIER PAC-MAN (ACTIF)", True, (0, 255, 102))
                    ECRAN.blit(sh_surf, (offset_c + self.vies * 22 + 5, 14))

                ar_surf = self.font_moyen.render(f"🪙 {self.argent}", True, (255, 215, 0))
                ECRAN.blit(ar_surf, (620, 14))

                top_surf = self.font_moyen.render(f"TOP: {self.meilleur_score}", True, (255, 159, 28))
                ECRAN.blit(top_surf, (LARGEUR - 150, 14))

                for obs in self.obstacles:
                    pygame.draw.rect(ECRAN, (24, 27, 48), (obs[0]+1, obs[1]+1, 23, 23), border_radius=4)
                    pygame.draw.rect(ECRAN, theme["ui_secondaire"], (obs[0]+1, obs[1]+1, 23, 23), 2, border_radius=4)

                # Pomme
                pygame.draw.circle(ECRAN, (255, 42, 109), (self.pomme[0] + 12, self.pomme[1] + 12), 11)
                pygame.draw.circle(ECRAN, (255, 255, 255), (self.pomme[0] + 8, self.pomme[1] + 8), 3)

                for px, py in self.pieces_sur_terrain:
                    pygame.draw.circle(ECRAN, (255, 215, 0), (px + 12, py + 12), 10)
                    pygame.draw.circle(ECRAN, (184, 134, 11), (px + 12, py + 12), 10, 2)

                if self.comete:
                    cx, cy = int(self.comete[0]), int(self.comete[1])
                    pygame.draw.line(ECRAN, (255, 215, 0), (cx, cy), (cx - 30, cy - 15), 3)
                    pygame.draw.circle(ECRAN, (255, 255, 255), (cx, cy), 7)
                    pygame.draw.circle(ECRAN, (255, 215, 0), (cx, cy), 7, 2)

                # Dessin du serpent sans clignotement de bouclier (le bouclier est permanent et stable pendant les 2s)
                palette = theme["couleurs_serpent"]
                for i, (sx, sy) in enumerate(self.serpent):
                    base_c, dark_c, light_c = palette[i % len(palette)]
                    c_rgb = tuple(int(base_c[j:j+2], 16) for j in (1, 3, 5))
                    d_rgb = tuple(int(dark_c[j:j+2], 16) for j in (1, 3, 5))

                    if i == 0:
                        pygame.draw.circle(ECRAN, c_rgb, (int(sx + 12), int(sy + 12)), 13)
                        pygame.draw.circle(ECRAN, d_rgb, (int(sx + 12), int(sy + 12)), 13, 2)
                        
                        # Anneau lumineux fixe du bouclier autour de la tête si actif
                        if self.invulnerable:
                            pygame.draw.circle(ECRAN, (0, 255, 102), (int(sx + 12), int(sy + 12)), 17, 2)

                        if self.direction == "Right":
                            yeux = [(sx + 17, sy + 6), (sx + 17, sy + 18)]
                            lg = (sx + 25, sy + 12)
                        elif self.direction == "Left":
                            yeux = [(sx + 7, sy + 6), (sx + 7, sy + 18)]
                            lg = (sx - 5, sy + 12)
                        elif self.direction == "Up":
                            yeux = [(sx + 6, sy + 7), (sx + 18, sy + 7)]
                            lg = (sx + 12, sy - 5)
                        else:
                            yeux = [(sx + 6, sy + 17), (sx + 18, sy + 17)]
                            lg = (sx + 12, sy + 25)

                        for ex, ey in yeux:
                            pygame.draw.circle(ECRAN, theme["couleur_yeux"], (int(ex), int(ey)), 3)
                            pygame.draw.circle(ECRAN, (0, 0, 0), (int(ex), int(ey)), 1)
                        pygame.draw.line(ECRAN, theme["couleur_langue"], (int(sx + 12), int(sy + 12)), (int(lg[0]), int(lg[1])), 2)
                    else:
                        pygame.draw.circle(ECRAN, d_rgb, (int(sx + 12), int(sy + 12)), 11)
                        pygame.draw.circle(ECRAN, c_rgb, (int(sx + 12), int(sy + 12)), 9)

                for p in self.particules[:]:
                    p[0] += p[2]; p[1] += p[3]; p[4] -= 1
                    if p[4] <= 0: self.particules.remove(p)
                    else: pygame.draw.circle(ECRAN, p[5], (int(p[0]), int(p[1])), 2)

                for tf in self.textes_flottants[:]:
                    tf[1] -= 1.0; tf[4] -= 1
                    if tf[4] <= 0: self.textes_flottants.remove(tf)
                    else:
                        tf_surf = self.font_moyen.render(tf[2], True, tf[3])
                        ECRAN.blit(tf_surf, (int(tf[0]), int(tf[1])))

                if self.etat == "PAUSE_IMPACT":
                    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
                    overlay.fill((11, 14, 38, 220))
                    ECRAN.blit(overlay, (0, 0))
                    pygame.draw.rect(ECRAN, (0, 255, 102), (LARGEUR // 2 - 250, HAUTEUR // 2 - 70, 500, 140), 2, border_radius=10)
                    t1 = self.font_titre.render("🛡️ BOUCLIER PAC-MAN", True, (0, 255, 102))
                    t2 = self.font_moyen.render("Appuie sur une FLÈCHE pour continuer", True, (255, 255, 255))
                    ECRAN.blit(t1, (LARGEUR // 2 - t1.get_width() // 2, HAUTEUR // 2 - 40))
                    ECRAN.blit(t2, (LARGEUR // 2 - t2.get_width() // 2, HAUTEUR // 2 + 15))

                elif self.etat == "PAUSE":
                    overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
                    overlay.fill((5, 5, 12, 200))
                    ECRAN.blit(overlay, (0, 0))
                    p_surf = self.font_titre.render("PAUSE SPATIALE", True, (255, 159, 28))
                    p_sub = self.font_moyen.render("Appuie sur 'P' pour reprendre", True, (255, 255, 255))
                    ECRAN.blit(p_surf, (LARGEUR // 2 - p_surf.get_width() // 2, HAUTEUR // 2 - 50))
                    ECRAN.blit(p_sub, (LARGEUR // 2 - p_sub.get_width() // 2, HAUTEUR // 2 + 10))

            elif self.etat == "GAMEOVER":
                overlay = pygame.Surface((LARGEUR, HAUTEUR), pygame.SRCALPHA)
                overlay.fill((11, 14, 38, 220))
                ECRAN.blit(overlay, (0, 0))

                pygame.draw.rect(ECRAN, (11, 14, 38), (LARGEUR // 2 - 250, HAUTEUR // 2 - 110, 500, 220), border_radius=12)
                pygame.draw.rect(ECRAN, (255, 42, 109), (LARGEUR // 2 - 250, HAUTEUR // 2 - 110, 500, 220), 3, border_radius=12)

                go_surf = self.font_titre.render("MISSION ÉCHOUÉE", True, (255, 42, 109))
                sc_surf = self.font_moyen.render(f"SCORE: {self.score} | CRÉDITS: {self.argent} 🪙", True, (255, 255, 255))
                res_surf = self.font_petit.render("Appuie sur 'R' pour revenir à la base", True, (160, 175, 200))

                ECRAN.blit(go_surf, (LARGEUR // 2 - go_surf.get_width() // 2, HAUTEUR // 2 - 70))
                ECRAN.blit(sc_surf, (LARGEUR // 2 - sc_surf.get_width() // 2, HAUTEUR // 2 - 10))
                ECRAN.blit(res_surf, (LARGEUR // 2 - res_surf.get_width() // 2, HAUTEUR // 2 + 50))

            pygame.display.flip()
            vitesse_actuelle = max(20, self.vitesse_ticks // 2) if self.boost else self.vitesse_ticks
            HORLOGE.tick(FPS if self.etat != "JEU" else (1000 // vitesse_actuelle))

if __name__ == "__main__":
    jeu = JeuDuSerpentSpatialeHD()
    jeu.run()