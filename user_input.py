import pythonosc
import threading 
import time
import numpy as np
from typing import List, Any


class User_Input:
    # time window is the rate at which the user input is evaluated
    # auto set to 4000ms = 4 beats in 60bpm
    def __init__(self, time_window=4000):
        # full user turn list
        self.curr_user_turn = []
        # self.user_knowledge = []
        self.time_window = time_window
        # notes played in previous time window
        self.prev_window = []
        # notes played in current time window
        self.curr_window = []
        self.turn_time = 0
        self.amt_window = 0
        self.debug = True

        # self.running_density = 0
        # initialize a 1x12 list
        self.pitch_histogram = [0] * 12

        self.probabilities = {
            'similarity': 0,
            'density': 0,
            'dynamics': 0,
            'elapsed_time': 0,
            'elapsed_time_percent': 0,
            'interupt_length': 0,
            'cadence': 0,
            'gaze': 0
        }

    def fill_window(self, pitch, ms, vel):
        self.curr_user_turn.append((pitch, ms, vel))
        self.curr_window.append((pitch, ms, vel))

    def update_window(self):
        # self.curr_user_turn.append(new_window)
        if self.debug:
            print("Updating window. Prev window: " + str(self.prev_window))
        self.prev_window = self.curr_window
        self.curr_window = []
        if self.debug:
            print("Updating window. Switched window: " + str(self.prev_window))

    # def interpret_input(address: str, *args: List[Any]):
    #     ms = args[0]
    #     pitch = args[1]
    #     vel = args[2]
    #     self.curr_user_turn.append((pitch, ms, vel))
    #     self.curr_window.append((pitch, ms, vel))

        # self.amt_window += ms
        # if self.amt_window >= time_window:

        #     self.prev_window = self.curr_window.copy()
        #     self.prev_window.append((pitch, ms))
        #     self.curr_window = []
        # else:
        #     self.curr_window.append((pitch, ms))  

    def get_similarity(self):
        #TODO: add rhythmic similarity
        # something to do rounding the amount of time

        if self.prev_window == [] or self.curr_window == []:
            return 0
        else:
            prev_window_pitch = list(zip(*self.prev_window))[0]
            prev_window_pitch = prev_window_pitch % 12
            prev_window_time = list(zip(*self.prev_window))[1]
        
            curr_window_pitch = list(zip(*self.curr_window))[0]
            curr_window_pitch = curr_window_pitch % 12
            curr_window_time = list(zip(*self.curr_window))[1]

            # direct similarity calculation - finds overlap
            pitch_overlap = len(set(prev_window_pitch) & set(curr_window_pitch)) / float(len(set(prev_window_pitch) | set(curr_window_pitch)))

            prev_intervals = np.diff(prev_window_pitch)
            curr_intervals = np.diff(curr_window_pitch)

            interval_overlap = len(set(prev_intervals) & set(curr_intervals)) / float(len(set(prev_intervals) | set(curr_intervals)))

            return pitch_overlap

        # TODO: figure out how to combine similarity metrics
        # TODO: add n-gram and edit distance 
        # https://qspace.library.queensu.ca/bitstream/handle/1974/7442/Kelly_Matthew_B_201208_MSC.pdf;sequence=1

    def update_similarity(self):
        similarity = self.get_similarity()
        self.probabilities['similarity'] = similarity

    def get_note_density(self):
        # how many notes have passed compared to last time window
        if self.prev_window is []:
            return 0
        else:
            prev_window_len = len(self.prev_window)
            curr_window_len = len(self.curr_window)
            try:
                change_note_density = (curr_window_len - prev_window_len) / curr_window_len
            except:
                change_note_density = 0
            return change_note_density

    def update_note_density(self):
        note_density = self.get_note_density()
        self.probabilities['note_density'] = note_density

    def get_dynamics(self):
        # check difference of moving avg of velocities
        if self.prev_window is []:
            return 0
        else:
            prev_window_len = len(self.prev_window)
            prev_dynamics_sum = sum([tup[2] for tup in self.prev_window])
            curr_window_len = len(self.curr_window)
            curr_dynamics_sum = sum([tup[2] for tup in self.curr_window])
            
            try:
                prev_avg_dynamics = prev_dynamics_sum / prev_window_len
            except:
                prev_avg_dynamics = 0
            try:
                curr_avg_dynamics = curr_dynamics_sum / curr_window_len
            except:
                curr_avg_dynamics = 0
                return 0
            
            change_dynamics = (curr_avg_dynamics - prev_avg_dynamics) / curr_avg_dynamics
            return change_dynamics
        
    def update_dynamics(self):
        dynamics = self.get_dynamics()
        self.probabilities['dynamics'] = dynamics

    def get_tonic(self):
        for note in self.curr_window:
            pitch_class = note[1] % 12
            self.pitch_histogram[pitch_class] += 1
        likely_tonic = max(self.pitch_histogram)
        return likely_tonic

    def get_cadence(self):
        if self.curr_window == []:
            return 0
        # return a 1 or 0 if the phrase ends on the likely_tonic
        likely_tonic = self.get_tonic()
        if (self.curr_window[-1][0] % 12) == likely_tonic:
            return 1
        else:
            return 0

    def update_cadence(self):
        cadence = self.get_cadence()
        self.probabilities['cadence'] = cadence

    def update_elapsed_time(self):
        # compute elapsed number of beats
        # longest turn is automatically 1.5 min
        longest_turn = 90000
        self.probabilities['elapsed_time'] = self.probabilities['elapsed_time'] + self.time_window
        self.probabilities['elapsed_time_percent'] = self.probabilities['elapsed_time'] / longest_turn

    def update_probabilities(self):
        self.update_note_density()
        self.update_dynamics()
        self.update_elapsed_time()
        # self.update_interupt_length()
        # self.update_gaze()
        self.update_similarity()
        self.update_cadence()
        if self.debug:
            print("Updated Probabilities: " + str(self.probabilities))
    
    def get_probabilities(self):
        return self.probabilities

class Transition_Probability:
    # time window is the rate at which the user input is evaluated
    # auto set to 4000ms = 4 beats in 60bpm
    def init(self, time_window=4000):

        self.probabilities = {
            'similarity': 0,
            'density': 0,
            'dynamics': 0,
            'elapsed_time': 0,
            'interupt_length': 0,
            'cadence': 0,
            'gaze': 0
        }
        # full user turn list
        self.curr_user_turn = []
        # self.user_knowledge = []
        self.time_window = time_window
        # notes played in previous time window
        self.prev_window = []
        # notes played in current time window
        self.curr_window = []
        self.turn_time = 0
        self.amt_window = 0

        # self.running_density = 0
        # initialize a 1x12 list
        self.pitch_histogram = [0] * 12

    
    def update_elapsed_time(self):
        # compute elapsed number of beats
        # longest turn is automatically 1.5 min
        longest_turn = 90000
        self.probabilities['elapsed_time'] = (self.probabilities['elapsed_time'] + self.time_window) / longest_turn


    def update_probabilities(self):

        self.update_density()
        self.update_dynamics()
        self.update_elapsed_time()
        # self.update_interupt_length()
        # self.update_gaze()
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
    