import pandas as pd

from ext.console import debug

def to_anova(response):
    all_conditions = [response.blank] + response.orientations
    mean_of_reps_of_conds = [
        [rep.trace.mean() for rep in ori.reps]
        for ori in all_conditions
    ]
    # debug.enter()
    return mean_of_reps_of_conds

def to_blank_and_orientations(response):
    if response.blank and response.orientations:
        all_conditions = [response.blank] + response.orientations
        mean_of_reps_of_conds = [
            [rep.trace.mean() for rep in ori.reps]
            for ori in all_conditions
        ]
        # debug.enter()
        return mean_of_reps_of_conds
