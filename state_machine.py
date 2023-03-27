import random
import threading
import time

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
      self._timer.daemon = True
      self._timer.start()
      self.is_running = True

  def stop(self):
    self._timer.cancel()
    self.is_running = False


# def call_repeatedly(interval, func, *args):
#     stopped = Event()
#     def loop():
#         while not stopped.wait(interval): # the first call is in `interval` secs
#             func(*args)
#     Thread(target=loop).start()    
#     return stopped.set

class State:
    def __init__(self, id, is_active):
        self.id = id
        self.is_active = is_active

class State_Machine:
    def __init__(self):
        self.leader = self.create_leader()
        self.follower = self.create_follower()

        self.current_state = self.follower
        self.num_checks = 0
        
        self.debug = True
        

    def transition(self):
        if self.current_state == self.leader:
            self.current_state = self.follower
        elif self.current_state == self.follower:
            self.current_state = self.leader
            
        if self.debug:
            print("New state is: " + str(self.current_state.id))
            
        return str(self.current_state.id)

        
    
    def create_leader(self):
        leader = State('leader', False)
        return leader
    
    def create_follower(self):
        follower = State('follower', False)
        return follower
    
    def check_state(self, probabilities):
        check_prob = 0.8

        probability = 0
        if self.current_state.id == 'leader':
            # want this to increase
            dynamics = probabilities['dynamics']
            # interupt = probabilities['interupt_length']
            # looking for density to increase
            density = probabilities['note_density'] 
            # want this to decrease
            similarity = probabilities['similarity']
            # this increases over time
            turn_length = probabilities['elapsed_time_percent']
            # gaze = probabilities['gaze']
            # probability = (dynamics + interupt + similarity + turn_length) * gaze
            probability = (dynamics + similarity + turn_length)
        elif self.current_state == self.follower:
            # looking for dynamics to decrease
            dynamics = probabilities['dynamics'] * -0.8
            # looking for density to decrease
            density = probabilities['note_density'] * -0.8
            # similarity should increase
            similarity = probabilities['similarity'] 
            # this increases with time
            turn_length = probabilities['elapsed_time_percent']
            # this should be a 1
            cadence = probabilities['cadence']
            # contour = probabilities['contour']
            # gaze = probabilities['gaze']
            # probability = (dynamics + density + similarity + cadence + contour + turn_length) * gaze
            probability = (dynamics + density + similarity + turn_length)
        
        if self.debug:
           print("Input probability: " + str(probability))
           print("Check probability: " + str(check_prob))
        if probability > check_prob:
            # self.transition_probability.reset_probabilities()
            if self.debug:
               print("State Transition")
            return self.transition()
        if self.debug:
           print('____________')


