from collections import OrderedDict


class Classement:
    def __init__(self, joueurs):
        self.joueurs = joueurs
        self.classement_elo = OrderedDict()
        self.classement_atp = OrderedDict()
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

    def afficher_classement(self, top_n=100, type="atp"):
        print(f"Classement {'ELO' if type == 'elo' else 'ATP'} :")
        if type == "elo":
            for joueur, rang in list(self.classement_elo.items())[:top_n]:
                print(
                    f"{rang}. {joueur.prenom} {joueur.nom} - ELO: {joueur.elo} - Pays: {joueur.country}"
                )
        else:
            for joueur, rang in list(self.classement_atp.items())[:top_n]:
                print(
                    f"{rang}. {joueur.prenom} {joueur.nom} - ATP Points: {joueur.atp_points} - Pays: {joueur.country}"
                )

    def obtenir_rang(self, joueur, type="atp"):
        if type == "atp":
            try:
                return self.classement_atp[joueur]
            except KeyError:
                print(joueur.prenom, joueur.nom)
        else:
            return self.classement_elo[joueur]

    def update_classement(self, type="atp"):
        if type == "atp":
            sorted_joueurs = sorted(
                self.joueurs.values(), key=lambda j: j.atp_points, reverse=True
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
        else:
            self.classement_elo = classement


# from Personnage import generer_pnj
#
# POOL = generer_pnj(100)
# classement = Classement(POOL)
