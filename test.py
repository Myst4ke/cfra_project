import itertools
from typing import List, Dict, Set, Tuple


class ColourCodingStarNetwork:
    def __init__(self, central_player: str, leaf_players: List[str], activities: List[str]):
        """
        Initialise le réseau en étoile.

        :param central_player: Identifiant du joueur central.
        :param leaf_players: Liste des joueurs périphériques (feuilles).
        :param activities: Liste des activités disponibles.
        """
        self.central_player = central_player
        self.leaf_players = leaf_players
        self.activities = activities
        self.void_activity = "void"

    def guess_center_assignment(self) -> List[Tuple[str, int]]:
        """
        Génère toutes les paires (activité, taille) possibles pour le joueur central.
        """
        guesses = []
        for activity in self.activities:
            for k in range(1, len(self.leaf_players) + 2):  # Taille maximale inclut le joueur central.
                guesses.append((activity, k))
        return guesses

    def guess_activities_in_use(self) -> List[Set[str]]:
        """
        Génère toutes les combinaisons possibles des activités utilisées par les feuilles.
        """
        activity_sets = []
        for size in range(1, len(self.activities) + 1):  # Au moins une activité doit être utilisée.
            activity_sets.extend(itertools.combinations(self.activities, size))
        return [set(activity_set) for activity_set in activity_sets]

    def random_colouring(self, activities_in_use: Set[str]) -> List[Dict[str, str]]:
        """
        Génère des assignations aléatoires de couleurs (activités) aux feuilles.

        :param activities_in_use: Ensemble des activités à assigner.
        :return: Liste d'assignations aléatoires (feuille -> activité).
        """
        possible_colours = list(activities_in_use) + [self.void_activity]
        random_assignments = []
        for _ in range(100):  # Limitation pour tester différentes assignations.
            assignment = {leaf: possible_colours[i % len(possible_colours)] for i, leaf in enumerate(self.leaf_players)}
            random_assignments.append(assignment)
        return random_assignments

    def is_assignment_stable(
        self, center_assignment: Tuple[str, int], activities_in_use: Set[str], leaf_assignment: Dict[str, str]
    ) -> bool:
        """
        Vérifie si une assignation est compatible et stable.

        :param center_assignment: Assignation (activité, taille) du centre.
        :param activities_in_use: Ensemble des activités utilisées.
        :param leaf_assignment: Assignation des feuilles (feuille -> activité).
        :return: True si stable, False sinon.
        """
        activity_count = {activity: 0 for activity in activities_in_use}
        activity_count[self.void_activity] = 0

        # Calculer le nombre de participants par activité
        for leaf, activity in leaf_assignment.items():
            activity_count[activity] += 1

        # Vérifier les contraintes pour le joueur central
        center_activity, center_group_size = center_assignment
        if activity_count[center_activity] != center_group_size:
            return False

        # Vérifier que chaque activité est assignée à une seule feuille, sauf void
        for activity in activities_in_use:
            if activity_count[activity] != 1 and activity != center_activity:
                return False

        # Vérifier qu'aucune feuille en activité void ne veut dévier
        for leaf, activity in leaf_assignment.items():
            if activity == self.void_activity:
                for alt_activity in activities_in_use:
                    if alt_activity != self.void_activity and activity_count[alt_activity] < 2:
                        return False

        return True

    def find_nash_stable_assignment(self) -> Dict[str, str]:
        """
        Cherche une assignation stable de Nash en utilisant la technique du colour-coding.

        :return: Assignation trouvée ou None si aucune assignation n'est trouvée.
        """
        center_guesses = self.guess_center_assignment()
        activity_guesses = self.guess_activities_in_use()

        for center_assignment in center_guesses:
            for activities_in_use in activity_guesses:
                random_colours = self.random_colouring(activities_in_use)
                for colouring in random_colours:
                    if self.is_assignment_stable(center_assignment, activities_in_use, colouring):
                        return {**colouring, self.central_player: center_assignment[0]}

        return None


# Exemple d'utilisation
if __name__ == "__main__":
    # Initialiser un réseau en étoile
    central_player = "center"
    leaf_players = ["leaf1", "leaf2", "leaf3", "leaf4"]
    activities = ["hiking", "bus_trip"]

    # Créer une instance du réseau
    star_network = ColourCodingStarNetwork(central_player, leaf_players, activities)

    # Trouver une assignation stable de Nash
    result = star_network.find_nash_stable_assignment()
    if result:
        print("Assignation stable de Nash trouvée :", result)
    else:
        print("Aucune assignation stable de Nash trouvée.")
