class MeleeBehaviourMixIn:
    def __init__(self):
        pass

    def target_is_stale(self):
        pass

    def has_target(self):
        pass

    def choose_best_target(self):
        pass

    def target_in_range(self):
        pass


    def target_in_range(self):
        pass


    def target_in_range(self):
        pass


    def target_in_range(self):
        pass

    def get_next_action(self):
        if self.target_is_stale or (not self.has_target):
            self.choose_best_target()

        if self.target_in_range:
            if self.can_attack:
                self.initiate_attack
