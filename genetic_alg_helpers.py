import random
from queue import Empty
from collections import Counter
from statistics import mean, median, stdev
from ast import literal_eval
import operator
import math
import pythonosc
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import time
import datetime
from typing import List, Any
from mido import MidiFile, tick2second, bpm2tempo, second2tick

tpb = 240
bpm = 110
rhythm_options = [tpb/8, int((tpb/4) * .66), tpb/4, int(tpb/2 * .66), tpb/2, int(tpb * .66), tpb, (tpb + tpb/2), tpb * 2, (tpb * 2) + tpb, tpb * 4]

def percentage_pitch(pattern, pitch_options):
    # create dictionary for avail pitches
    pitch_map = dict.fromkeys(pitch_options, 0)
    # count occurance of each note in pattern
    pitch_pattern = pattern.copy()
    pitch_pattern = [pitch[0] % 12 for pitch in pitch_pattern]
    pitch_count = Counter(elem for elem in pitch_pattern)
    # combine dictionaries
    pitch_map = {**pitch_map, **pitch_count}
    pitch_map = {key: pitch_map[key] / len(pitch_pattern) for key in pitch_map.keys()}
    return pitch_map

def percentage_rhythm(pattern, rhythm_options):
    # create dictionary for avail rhythm
    rhythm_map = dict.fromkeys(rhythm_options, 0)
    # count occurance of each note in pattern

    for rhythm in pattern:
        # 32nd note
        if rhythm[1] <= rhythm_options[0]:
            rhythm_map[rhythm_options[0]] += 1
        # cycle through rhythm options and find the one with the smallest difference to the current rhythm
        for note_iter in range(len(rhythm_options)):
            if rhythm[1] <= rhythm_options[note_iter]:
                if abs(rhythm[0] - rhythm_options[note_iter - 1]) <= abs(rhythm[1] - rhythm_options[note_iter]):
                    rhythm_map[rhythm_options[note_iter - 1]] += 1
                else:
                    rhythm_map[rhythm_options[note_iter]] += 1

    rhythm_map = {key: rhythm_map[key] / len(pattern) for key in rhythm_map.keys()}
    return rhythm_map

def percentage_intervals(intervals):
    # create dictionary for avail intervals
    intervals_opt = [-12, -11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
    interval_map = dict.fromkeys(intervals_opt, 0)
    # count occurance of each note in pattern
    interval_count = Counter(elem for elem in intervals)
    # combine dictionaries
    interval_map = {**interval_map, **interval_count}
    interval_map = {key: interval_map[key] / len(intervals) for key in interval_map.keys()}
    return interval_map

def get_total_ticks(pattern):
    total = 0
    for i in range(len(pattern)):
        total += pattern[i][1]
    return total
        
def get_range(pattern):
    min_pitch = min(pattern)[0]
    max_pitch = max(pattern)[0]
    range = max_pitch - min_pitch
    return (range, min_pitch, max_pitch)

def get_pitch_mct(pattern):
    mean_pitch = mean(elem[0] for elem in pattern)
    median_pitch = median(elem[0] for elem in pattern)
    stdev_pitch = stdev(elem[0] for elem in pattern)
    return (mean_pitch, median_pitch, stdev_pitch)

def get_intervals(pattern):
    pitch_pattern = pattern.copy()
    pitch_pattern = filter(lambda i: i not in [-1], pitch_pattern)
    first_note = pattern[0][0]
    intervals = []
    for i in range(1, len(pattern)):
        second_note = pattern[i][0]
        intervals.append(second_note - first_note)
        first_note = second_note
    return intervals

def check_if_triplet(pattern, ind, dir):
    try:
        if dir == 'forward':
            if pattern[ind][0] >= rhythm_options[1] - 10 or pattern[ind][0] <= rhythm_options[1] + 10:
                if pattern[ind+1][0] >= rhythm_options[1] - 10 or pattern[ind+1][0] <= rhythm_options[1] + 10:
                    if pattern[ind+2][0] >= rhythm_options[1] - 10 or pattern[ind+2][0] <= rhythm_options[1] + 10:
                        return True
            if pattern[ind][0] >= rhythm_options[3] - 10 or pattern[ind][0] <= rhythm_options[3] + 10:
                if pattern[ind+1][0] >= rhythm_options[3] - 10 or pattern[ind+1][0] <= rhythm_options[3] + 10:
                    if pattern[ind+2][0] >= rhythm_options[3] - 10 or pattern[ind+2][0] <= rhythm_options[3] + 10:
                        return True
            if pattern[ind][0] >= rhythm_options[5] - 10 or pattern[ind][0] <= rhythm_options[5] + 10:
                if pattern[ind+1][0] >= rhythm_options[5] - 10 or pattern[ind+1][0] <= rhythm_options[5] + 10:
                    if pattern[ind+2][0] >= rhythm_options[5] - 10 or pattern[ind+2][0] <= rhythm_options[5] + 10:
                        return True
        else:
            if pattern[ind][0] >= rhythm_options[1] - 10 or pattern[ind][0] <= rhythm_options[1] + 10:
                if pattern[ind-1][0] >= rhythm_options[1] - 10 or pattern[ind-1][0] <= rhythm_options[1] + 10:
                    if pattern[ind-2][0] >= rhythm_options[1] - 10 or pattern[ind-2][0] <= rhythm_options[1] + 10:
                        return True
            if pattern[ind][0] >= rhythm_options[3] - 10 or pattern[ind][0] <= rhythm_options[3] + 10:
                if pattern[ind-1][0] >= rhythm_options[3] - 10 or pattern[ind-1][0] <= rhythm_options[3] + 10:
                    if pattern[ind-2][0] >= rhythm_options[3] - 10 or pattern[ind-2][0] <= rhythm_options[3] + 10:
                        return True
            if pattern[ind][0] >= rhythm_options[5] - 10 or pattern[ind][0] <= rhythm_options[5] + 10:
                if pattern[ind-1][0] >= rhythm_options[5] - 10 or pattern[ind-1][0] <= rhythm_options[5] + 10:
                    if pattern[ind-2][0] >= rhythm_options[5] - 10 or pattern[ind-2][0] <= rhythm_options[5] + 10:
                        return True
    except:
        return False

# attempt to define contour from front and back arcs (disregards middle if one melody is much longer)
def check_order_front_back(patt_1, patt_2):
    front = 0
    back_1 = len(patt_1) - 1
    back_2 = len(patt_2) - 1
    matches_pitch = 0
    matches_rhythm = 0
    while(front < back_1 and front < back_2):
        if ((patt_1[front][1] + 20 <= patt_2[front][1]) and (patt_1[front][1] - 20 >= patt_2[front][1])):
            matches_rhythm += 1
        if (patt_1[front][0] == patt_2[front][0]):
            matches_pitch += 1
        if ((patt_1[back_1][1] + 20 <= patt_2[back_2][1]) and (patt_1[back_1][1] - 20 <= patt_2[back_2][1])):
            matches_rhythm += 1
        if (patt_1[back_1][0] == patt_2[back_2][0]):
            matches_pitch += 1
        front = front + 1
        back_1 = back_1 - 1
        back_2 = back_2 - 1
    shorter_len = len(patt_1)
    if len(patt_2) < shorter_len:
        shorter_len = len(patt_2)
    percent_pitch = matches_pitch / shorter_len
    percent_rhythm = matches_rhythm / shorter_len
    return (percent_rhythm, percent_pitch)
    
def step_to_leap_ratio(intervals):
    # step defined as minor third and below (everything else is a leap)
    # returns step / leap
    steps = 0
    leaps = 0
    for i in range(len(intervals)):
        if abs(intervals[i]) > 3:
            leaps += 1
        else:
            steps += 1
    if leaps == 0:
        return 1
    else:
        return steps / leaps

def get_abstracted_contour(pattern):
    patt_len = len(pattern)
    min_pitch = min(pattern)[0]
    max_pitch = max(pattern)[0]
    first_pitch = pattern[0][0]
    last_pitch = pattern[patt_len - 1][0]
    mid_point = int(patt_len / 2)
    mid_pitch = pattern[mid_point][0]

    if (min_pitch == max_pitch):
        return 'flat'
    elif max_pitch == first_pitch:
        if min_pitch == last_pitch or last_pitch < mid_pitch:
            return 'descend'
        elif max_pitch == last_pitch or last_pitch >= mid_pitch:
            return 'v'
    elif min_pitch == first_pitch:
        if max_pitch == last_pitch or last_pitch >= mid_pitch:
            return 'ascend'
        elif min_pitch == last_pitch or last_pitch < mid_pitch:
            return 'arch'

    return 'undef'

def expand_pattern(pattern, rhythm_options):
    expanded_pattern = []
    for i in range(len(pattern)):
        if len(pattern[i]) == 3:
            pitch, rhythm, vel = pattern[i]
            # print(pattern[i])
        if len(pattern[i]) == 2:
            pitch, rhythm = pattern[i]
        expanded_note = [pitch] * int(rhythm)
        expanded_pattern.extend(expanded_note)
    return expanded_pattern

def transpose_to_C(pattern):
    diff = pattern[0] - 60
    transp_patt = []
    for i in range(len(pattern)):
        transp_patt.append(pattern[i] + diff)
    return transp_patt

def get_total_beats(pattern):
    total = 0
    for i in range(0, len(pattern)):
        total = total + pattern[i][1]
    return total
