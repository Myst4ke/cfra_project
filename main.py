import itertools
from typing import List, Dict, Set, Tuple
import random
import time
import os

def time_it(f):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"La fonction '{f.__name__}' a pris {elapsed_time:.6f} seconde(s)")
        return result
    return wrapper

class ColourCodingStarNetworkWithPreferences:
    def __init__(self, central_player: str, leaf_players: List[str], activities: List[str], preferences: Dict[str, List[Tuple[str, int]]]):
        """
        Initialise le réseau en étoile avec des préférences pour chaque joueur.
        """
        self.central_player = central_player
        self.leaf_players = leaf_players
        self.activities = activities
        self.preferences = preferences
        self.void_activity = "void"

    def guess_center_assignment(self) -> List[Tuple[str, int]]:
        """
        Génère toutes les paires (activité, taille) possibles pour le joueur central en se basant sur ses préférences.
        """
        return self.preferences.get(self.central_player, [])
    
    
    def random_colouring(self, activities_in_use: Set[str]) -> List[Dict[str, str]]:
        """
        Génère un ensemble de configurations aléatoires pour les feuilles.
        """
        possible_colours = list(activities_in_use) + [self.void_activity]
        random_assignments = []

        for _ in range(100):
            assignment = {leaf: random.choice(possible_colours) for leaf in self.leaf_players}
            random_assignments.append(assignment)

        return random_assignments
    
    def random_colouring_opti(self, activities_in_use: Set[str], num_samples: int = 100) -> List[Dict[str, str]]:
        """
        Génère un ensemble de configurations aléatoires pour les feuilles, en tenant compte de leurs préférences.
        """
        random_assignments = []

        for _ in range(num_samples):
            assignment = {}
            for leaf in self.leaf_players:
                # Filtrer les activités disponibles selon les préférences de la feuille
                preferred_activities = [pref[0] for pref in self.preferences[leaf] if pref[0] in activities_in_use]
                possible_colours = preferred_activities + [self.void_activity]
                # Choisir une activité aléatoire parmi les préférées (ou void)
                assignment[leaf] = random.choice(possible_colours)
            random_assignments.append(assignment)

        return random_assignments



    def exhaustive_colouring(self, activities_in_use: Set[str]) -> List[Dict[str, str]]:
        """
        Génère toutes les assignations possibles (non aléatoires) pour les feuilles.
        """
        possible_colours = list(activities_in_use) + [self.void_activity]
        return [
            dict(zip(self.leaf_players, colouring))
            for colouring in itertools.product(possible_colours, repeat=len(self.leaf_players))
        ]
    
    def exhaustive_colouring_opti(self, activities_in_use: Set[str]) -> List[Dict[str, str]]:
        """
        Génère toutes les assignations possibles pour les feuilles, en tenant compte de leurs préférences.
        """
        # Préparer les options possibles pour chaque feuille en filtrant selon ses préférences
        all_options = []
        for leaf in self.leaf_players:
            preferred_activities = [pref[0] for pref in self.preferences[leaf] if pref[0] in activities_in_use]
            possible_colours = preferred_activities + [self.void_activity]
            all_options.append(possible_colours)

        # Générer toutes les combinaisons possibles des options filtrées
        return [
            dict(zip(self.leaf_players, colouring))
            for colouring in itertools.product(*all_options)
    ]

    
    def heuristic_colouring(self, activities_in_use: Set[str], num_samples: int = 100) -> List[Dict[str, str]]:
        """
        Génère un ensemble de configurations basées sur une heuristique pondérant les activités préférées.
        """
        heuristic_assignments = []

        for _ in range(num_samples):
            assignment = {}
            for leaf in self.leaf_players:
                # Récupérer les activités préférées et pondérer selon leur rang
                preferred_activities = [pref[0] for pref in self.preferences[leaf] if pref[0] in activities_in_use]
                weights = [len(self.preferences[leaf]) - i for i in range(len(preferred_activities))]
                
                # Inclure l'option "void" avec une pondération minimale
                possible_colours = preferred_activities + [self.void_activity]
                weights.append(1)  # Ajouter une pondération pour "void"
                
                # Choisir une activité pondérée
                assignment[leaf] = random.choices(possible_colours, weights=weights)[0]
            
            heuristic_assignments.append(assignment)

        return heuristic_assignments

    def is_assignment_stable(
        self, center_assignment: Tuple[str, int], activities_in_use: Set[str], leaf_assignment: Dict[str, str]
    ) -> bool:
        """
        Vérifie si une assignation est compatible et stable en respectant les préférences des joueurs.
        """
        # print(f"Testing stability for: center={center_assignment}, leaves={leaf_assignment}")
        
        # Compte des participants pour chaque activité
        activity_count = {activity: 0 for activity in activities_in_use}
        activity_count[self.void_activity] = 0

        # Assurer que l'activité centrale est incluse dans le comptage
        center_activity = center_assignment[0]
        if center_activity not in activity_count:
            activity_count[center_activity] = 0

        # Calculer le nombre de participants par activité
        for leaf, activity in leaf_assignment.items():
            activity_count[activity] += 1

        # Vérifier si le joueur central est satisfait de son assignation
        center_group_size = center_assignment[1]
        if (center_activity, center_group_size) not in self.preferences[self.central_player]:
            return False

        # Vérifier si les feuilles sont satisfaites de leurs assignations
        for leaf, activity in leaf_assignment.items():
            group_size = activity_count[activity]
            if (activity, group_size) not in self.preferences[leaf] and activity != self.void_activity:
                return False

        # Vérifier qu'aucune feuille en activité void ne veut dévier
        for leaf, activity in leaf_assignment.items():
            if activity == self.void_activity:
                for alt_activity in activities_in_use:
                    new_group_size = activity_count[alt_activity] + 1
                    if (alt_activity, new_group_size) in self.preferences[leaf]:
                        return False

        return True
    
    @time_it
    def find_nash_stable_assignment(self) -> Dict[str, str]:
        """
        Cherche une assignation stable de Nash en utilisant la technique du colour-coding.
        """
        center_guesses = self.guess_center_assignment()
        activity_guesses = [set(pref[0] for pref in self.preferences[self.central_player])]

        for center_assignment in center_guesses:
            for activities_in_use in activity_guesses:
                random_colours = self.random_colouring(activities_in_use)
                for colouring in random_colours:
                    if self.is_assignment_stable(center_assignment, activities_in_use, colouring):
                        return {**colouring, self.central_player: center_assignment[0]}

        return None
    
    @time_it
    def find_all_nash_stable_assignments(self) -> List[Dict[str, str]]:
        """
        Trouve toutes les assignations stables de Nash en utilisant la méthode exhaustive_colouring.

        :return: Liste de toutes les assignations stables de Nash trouvées.
        """
        stable_assignments = []
        center_guesses = self.guess_center_assignment()
        activity_guesses = [set(pref[0] for pref in self.preferences[self.central_player])]

        for center_assignment in center_guesses:
            for activities_in_use in activity_guesses:
                all_colours = self.exhaustive_colouring(activities_in_use)
                for colouring in all_colours:
                    if self.is_assignment_stable(center_assignment, activities_in_use, colouring):
                        stable_assignment = {**colouring, self.central_player: center_assignment[0]}
                        stable_assignments.append(stable_assignment)

        return stable_assignments



def parse_test_file(file_path: str) -> Tuple[str, List[str], List[str], Dict[str, List[Tuple[str, int]]]]:
    """
    Parse un fichier .test pour générer la configuration du réseau en étoile avec des préférences.
    """
    central_player = ""
    leaf_players = []
    activities = []
    preferences = {}

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
                activities = [activity.strip() for activity in line.split(":", 1)[1].split(",")]

            elif line.startswith("preferences:"):
                for preference_line in file:
                    preference_line = preference_line.strip()
                    if not preference_line or preference_line.startswith("#"):
                        continue

                    if ":" in preference_line:
                        player, prefs = preference_line.split(":", 1)
                        player = player.strip()

                        preferences[player] = []
                        for pref in prefs.split(">"):
                            activity, num = pref.strip(" ()").split(",")
                            preferences[player].append((activity.strip(), int(num.strip())))

    return central_player, leaf_players, activities, preferences




if __name__ == "__main__":
    test_file_path = "tests/test_4.test"

    central_player, leaf_players, activities, preferences = parse_test_file(test_file_path)

    print(f"Joueur central : {central_player}")
    print(f"Joueurs périphériques : {leaf_players}")
    print(f"Activités disponibles : {activities}")
    print(f"Préférences des joueurs : {preferences}")

    star_network = ColourCodingStarNetworkWithPreferences(
        central_player=central_player,
        leaf_players=leaf_players,
        activities=activities,
        preferences=preferences,
    )

    result = star_network.find_nash_stable_assignment()
    if result:
        print("Assignation stable de Nash trouvée :", result)
    else:
        print("Aucune assignation stable de Nash trouvée. Lancement de la recherche exhaustive")
        result = star_network.find_all_nash_stable_assignments()
        if result:
            print(f"{len(result)} assignation stable de Nash trouvée :\n{result}")
        else:
            print("Aucune assignation stable de Nash trouvée.")
