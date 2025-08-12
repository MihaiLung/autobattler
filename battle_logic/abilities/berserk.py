# from battle_logic.character import Character


class Ability:
    def __init__(self, character):
        self._character = character

    @property
    def character(self):
        return self._character

class Berserker(Ability):
    def __init__(self, character, intensity=2):
        super().__init__(character)
        self.intensity = intensity

    @property
    def current_attack_speed_multiplier(self):
        return 1+self.intensity*(1-self.character.current_health/self.character.stats.health)

    def update(self):
        self.character.attack_speed = self.character.stats.attack_speed*self.current_attack_speed_multiplier
        self.character.recompute_attack_timer()
