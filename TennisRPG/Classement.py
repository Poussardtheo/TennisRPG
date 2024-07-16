from collections import OrderedDict


class Classement:
    def __init__(self, joueurs):
        self.joueurs = joueurs
        self.classement_elo = OrderedDict()
        self.classement_atp = OrderedDict()
        self.classement_atp_race = OrderedDict()
        self.initialiser_classements()

    def initialiser_classements(self):
        classement = sorted(
            self.joueurs.values(), key=lambda joueur: joueur.elo, reverse=True
        )
        self.classement_elo = OrderedDict(
            (joueur, i) for i, joueur in enumerate(classement, 1)
        )
        self.classement_atp = OrderedDict(
            (joueur, i) for i, joueur in enumerate(classement, 1)
        )
        self.classement_atp_race = OrderedDict(
            (joueur, i) for i, joueur in enumerate(classement, 1)
        )

    def afficher_classement(self, top_n=100, type="atp"):
        print(f"\nClassement {'ELO' if type == 'elo' else 'ATP' if type == 'atp' else 'ATP Race'} :")
        if type == "elo":
            for joueur, rang in list(self.classement_elo.items())[:top_n]:
                print(
                    f"{rang}. {joueur.prenom} {joueur.nom} - ELO: {joueur.elo} - Pays: {joueur.country}"
                )
        elif type == "atp":
            for joueur, rang in list(self.classement_atp.items())[:top_n]:
                print(
                    f"{rang}. {joueur.prenom} {joueur.nom} - ATP Points: {joueur.atp_points} - Pays: {joueur.country}"
                )
        else:
            for joueur, rang in list(self.classement_atp_race.items())[:top_n]:
                print(
                    f"{rang}. {joueur.prenom} {joueur.nom} - ATP Race Points: {joueur.atp_race_points} - Pays: {joueur.country}"
                )

    def obtenir_rang(self, joueur, type="atp"):
        if type == "atp":
            return self.classement_atp[joueur]
        elif type == "atp_race":
            return self.classement_atp_race[joueur]
        else:
            return self.classement_elo[joueur]

    def update_classement(self, type="atp"):
        if type == "atp":
            sorted_joueurs = sorted(
                self.joueurs.values(), key=lambda j: j.atp_points, reverse=True
            )
        elif type == "atp_race":
            sorted_joueurs = sorted(
                self.joueurs.values(), key=lambda j: j.atp_race_points, reverse=True
            )
        else:
            sorted_joueurs = sorted(
                self.joueurs.values(), key=lambda j: j.elo, reverse=True
            )

        classement = OrderedDict()
        for rang, joueur in enumerate(sorted_joueurs, 1):
            classement[joueur] = rang

        if type == "atp":
            self.classement_atp = classement
        elif type == "atp_race":
            self.classement_atp_race = classement
        else:
            self.classement_elo = classement
    
    def reinitialiser_atp_race(self):
        self.classement_atp_race = OrderedDict((joueur, 0) for joueur in self.joueurs.values())
# from Personnage import generer_pnj
#
# POOL = generer_pnj(100)
# classement = Classement(POOL)
