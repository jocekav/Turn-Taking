import random
import threading

# timer code from https://stackoverflow.com/questions/3393612/run-certain-code-every-n-seconds

class RepeatedTimer(object):
  def __init__(self, interval, function, *args, **kwargs):
    self._timer = None
    self.interval = interval
    self.function = function
    self.args = args
    self.kwargs = kwargs
    self.is_running = False
    self.next_call = time.time()
    self.start()

  def _run(self):
    self.is_running = False
    self.start()
    self.function(*self.args, **self.kwargs)

  def start(self):
    if not self.is_running:
      self.next_call += self.interval
      self._timer = threading.Timer(self.next_call - time.time(), self._run)
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False

class State:
    def init(self, id, is_active):
        self.id = id
        self.is_active = is_active

class Transition_Probability:
    # time window is the rate at which the user input is evaluated
    # auto set to 4000ms = 4 beats in 60bpm
    def init(self, time_window=4000):
        self.time_window = time_window
        self.probabilities = {
            'similarity': 0,
            'density': 0,
            'dynamics': 0,
            'elapsed_time': 0,
            'interupt_length': 0,
            'cadence': 0,
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
    
    def update_elapsed_time(self):
        # compute elapsed number of beats
        # longest turn is automatically 1.5 min
        longest_turn = 90000
        self.probabilities['elapsed_time'] = (self.probabilities['elapsed_time'] + self.time_window) / longest_turn

    def update_cadence(self):
        # compute user input interupt metric

        # PLACE HOLDER
        self.probabilities['cadence'] = = random.randrange(0, 100) / 100.0

    def update_gaze(self):
        # compute user input gaze metric

        # PLACE HOLDER
        self.probabilities['gaze'] = random.randrange(0, 1)


    def update_probabilities(self):
        self.update_density()
        self.update_dynamics()
        self.update_elapsed_time()
        self.update_interupt_length()
        self.update_gaze()
        self.update_similarity()
        self.update_cadence()
    
    def reset_probabilities(self):
        self.probabilities['similarity'] = 0
        self.probabilities['density'] = 0
        self.probabilities['dynamics'] = 0
        self.probabilities['elapsed_time'] = 0
        self.probabilities['interupt_length'] = 0
        self.probabilities['gaze'] = 0
        self.probabilities['cadence'] = 0

    def get_probabilities(self):
        return self.probabilities

class State_Machine:
    def init(self):
        self.leader = self.create_leader()
        self.follower = self.create_follower()

        self.current_state = self.follower
        self.transition_probability = Transition_Probability()
        self.num_checks = 0

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
            turn_length = probabilities['elapsed_time']
            gaze = probabilities['gaze']
            probability = (dynamics + interupt + similarity + turn_length) * gaze
        elif self.current_state == self.follower:
            dynamics = probabilities['dynamics']
            density = probabilities['density']
            similarity = probabilities['similarity']
            turn_length = probabilities['elapsed_time']
            cadence = probabilities['cadence']
            contour = probabilities['contour']
            gaze = probabilities['gaze']
            probability = (dynamics + density + similarity + cadence + contour + turn_length) * gaze
        if probability > check_prob:
            self.transition_probability.reset_probabilities()
            self.transition()


