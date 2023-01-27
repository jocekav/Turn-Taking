import random

class State:
    def init(self, id, is_active):
        self.id = id
        self.is_active = is_active

class Transition_Probability:
    def init(self, beat_interval=1):
        self.beat_interval = beat_interval

        self.probabilities = {
            'similarity': 0,
            'density': 0,
            'dynamics': 0,
            'elapsed_beats': 0,
            'interupt_length': 0,
            'gaze': 0
        }

    def update_similarity(self):
        # compute user input similarity metric

        # PLACE HOLDER
        self.probabilities['similarity'] = random.randrange(0, 100) / 100.0
    
    def update_density(self):
        # compute user input density metric

        # PLACE HOLDER
        self.probabilities['density'] = random.randrange(0, 100) / 100.0
    
    def update_dynamics(self):
        # compute user input dynamics metric

        # PLACE HOLDER
        self.probabilities['dynamics'] = random.randrange(0, 100) / 100.0
    
    def update_elapsed_beats(self):
        # compute elapsed number of beats
        longest_turn = 20.0
        self.probabilities['elapsed_beats'] = (self.probabilities['elapsed_beats'] + self.beat_interval) / longest_turn
    
    def update_interupt_length(self):
        # compute user input interupt metric

        # PLACE HOLDER
        self.probabilities['interupt_length'] = random.randrange(0, 50)
    
    def update_gaze(self):
        # compute user input gaze metric

        # PLACE HOLDER
        self.probabilities['gaze'] = random.randrange(0, 1)

    def update_probabilities(self):
        self.update_density()
        self.update_dynamics()
        self.update_elapsed_beats()
        self.update_interupt_length()
        self.update_gaze()
        self.update_similarity()
    
    def reset_probabilities(self):
        self.probabilities['similarity'] = 0
        self.probabilities['density'] = 0
        self.probabilities['dynamics'] = 0
        self.probabilities['elapsed_beats'] = 0
        self.probabilities['interupt_length'] = 0
        self.probabilities['gaze'] = 0

    def get_probabilities(self):
        return self.probabilities

class State_Machine:
    def init(self):

        self.leader = self.create_leader()
        self.follower = self.create_follower()

        self.current_state = self.follower
        self.transition_probability = Transition_Probability()

    def transition(self):
        if self.current_state == self.leader:
            self.current_state = self.follower
        elif self.current_state == self.follower:
            self.current_state = self.leader
    
    def create_leader(self):
        leader = State('leader', False)
        return leader
    
    def create_follower(self):
        follower = State('follower', False)
        return follower
    
    def check_state(self):
        check_prob = 0.8
        self.transition_probability.update_probabilities()
        probabilities = self.transition_probability.get_probabilities()
        probability = 0
        if self.current_state.id == 'leader':
            dynamics = probabilities['dynamics']
            interupt = probabilities['interupt_length']
            similarity = probabilities['similarity']
            turn_length = probabilities['elapsed_beats']
            gaze = probabilities['gaze']
            probability = (dynamics + interupt + similarity + turn_length) * gaze
        elif self.current_state == self.follower:
            dynamics = probabilities['dynamics']
            density = probabilities['density']
            similarity = probabilities['similarity']
            turn_length = probabilities['elapsed_beats']
            gaze = probabilities['gaze']
            probability = (dynamics + density + similarity + + turn_length) * gaze
        if probability > check_prob:
            self.transition_probability.reset_probabilities()
            self.transition()


