import itertools
from typing import List, Dict, Set, Tuple
# import os


class ColourCodingStarNetworkWithCapacities:
    def __init__(self, central_player: str, leaf_players: List[str], activities: List[str], activity_capacities: Dict[str, int]):
        """
        Initialise le réseau en étoile avec capacités explicites pour les activités.
        """
        self.central_player = central_player
        self.leaf_players = leaf_players
        self.activities = activities
        self.activity_capacities = activity_capacities
        self.void_activity = "void"

    def guess_center_assignment(self) -> List[Tuple[str, int]]:
        """
        Génère toutes les paires (activité, taille) possibles pour le joueur central.
        """
        guesses = []
        for activity in self.activities:
            max_size = self.activity_capacities.get(activity, len(self.leaf_players) + 1)
            if max_size == float("inf"):
                max_size = len(self.leaf_players) + 1

            for k in range(1, max_size + 1):
                guesses.append((activity, k))
        return guesses


    def guess_activities_in_use(self) -> List[Set[str]]:
        """
        Génère toutes les combinaisons possibles des activités utilisées par les feuilles.
        """
        activity_sets = []
        for size in range(1, len(self.activities) + 1):
            activity_sets.extend(itertools.combinations(self.activities, size))
        return [set(activity_set) for activity_set in activity_sets]

    def random_colouring(self, activities_in_use: Set[str]) -> List[Dict[str, str]]:
        """
        Génère des assignations aléatoires de couleurs (activités) aux feuilles.
        """
        possible_colours = list(activities_in_use) + [self.void_activity]
        random_assignments = []
        for _ in range(100):  # Limitation pour tester différentes assignations.
            assignment = {leaf: possible_colours[i % len(possible_colours)] for i, leaf in enumerate(self.leaf_players)}
            random_assignments.append(assignment)
        return random_assignments

    def is_assignment_stable(self, center_assignment: Tuple[str, int], activities_in_use: Set[str], leaf_assignment: Dict[str, str]) -> bool:
        """
        Vérifie si une assignation est compatible et stable.
        """
        activity_count = {activity: 0 for activity in activities_in_use}
        activity_count[self.void_activity] = 0

        # Assurer que l'activité centrale est incluse dans le comptage
        center_activity = center_assignment[0]
        if center_activity not in activity_count:
            activity_count[center_activity] = 0

        # Calculer le nombre de participants par activité
        for leaf, activity in leaf_assignment.items():
            activity_count[activity] += 1

        # Vérifier les limites de capacité pour chaque activité
        for activity, count in activity_count.items():
            if count > self.activity_capacities.get(activity, float("inf")):
                return False

        # Vérifier les contraintes pour le joueur central
        center_group_size = center_assignment[1]
        if activity_count[center_activity] != center_group_size:
            return False

        # Vérifier qu'aucune feuille en activité void ne veut dévier
        for leaf, activity in leaf_assignment.items():
            if activity == self.void_activity:
                for alt_activity in activities_in_use:
                    if alt_activity != self.void_activity and activity_count[alt_activity] < self.activity_capacities.get(alt_activity, 0):
                        return False

        return True


    def find_nash_stable_assignment(self) -> Dict[str, str]:
        """
        Cherche une assignation stable de Nash en utilisant la technique du colour-coding.
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

def parse_test_file(file_path: str) -> Tuple[str, List[str], List[str], Dict[str, int]]:
    """
    Parse un fichier .test pour générer la configuration du réseau en étoile.
    """
    central_player = ""
    leaf_players = []
    activities = []
    activity_capacities = {}

    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if line.startswith("central_player:"):
                central_player = line.split(":", 1)[1].strip()

            elif line.startswith("leaf_players:"):
                leaf_players = [player.strip() for player in line.split(":", 1)[1].split(",")]

            elif line.startswith("activities:"):
                for activity_line in file:
                    activity_line = activity_line.strip()
                    if not activity_line or activity_line.startswith("#"):
                        continue
                    if ":" not in activity_line:
                        break
                    activity, capacity = activity_line.split(":", 1)
                    activities.append(activity.strip())
                    if capacity.strip().lower() == "inf":
                        activity_capacities[activity.strip()] = float("inf")
                    else:
                        activity_capacities[activity.strip()] = int(capacity.strip())

    return central_player, leaf_players, activities, activity_capacities


if __name__ == "__main__":
    test_file_path = "tests/test_5.test"

    central_player, leaf_players, activities, activity_capacities = parse_test_file(test_file_path)

    print(f"Joueur central : {central_player}")
    print(f"Joueurs périphériques : {leaf_players}")
    print(f"Activités disponibles : {activities}")
    print(f"Capacités des activités : {activity_capacities}")

    star_network = ColourCodingStarNetworkWithCapacities(central_player, leaf_players, activities, activity_capacities)

    result = star_network.find_nash_stable_assignment()
    if result:
        print("Assignation stable de Nash trouvée :", result)
    else:
        print("Aucune assignation stable de Nash trouvée.")

