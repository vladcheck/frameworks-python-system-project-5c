from typing import List

from entities.Performance import Performance


performances: List[Performance] = []

def get_performances():
    return performances

def add_new_performance(name):
    performances.append(Performance(name))
