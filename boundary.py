import numpy as np
import portion as P
from scipy import optimize

def find_crossing_bound_indices(values):
    """Given a list of values, returns the indices of the values where the boundary is crossed
    Assumes that the boundary is crossed when the sign of the value changes"""
    values = np.array(values)
    # Treats 0 as positive
    signs = np.sign(values)
    signs[signs == 0] = 1
    crossing_indices = np.where((np.diff(signs) != 0))[0]
    return [(i, i+1) for i in crossing_indices]

def find_crossing_bounds(times, values):
    """Given a list of values and a desired value, returns the indices of the values where the desired value is crossed"""
    crossings_bound_indices = np.array(find_crossing_bound_indices(values))
    return [(times[a], times[b]) for a,b in crossings_bound_indices]

def initial_search(times, f, desired_val, *args):
    """Initial search where the times sample frequently enough so that boundary crossing is not likely to be missed"""
    unit = f(times[0], desired_val, *args)
    return [f(t, desired_val, *args).to_value() for t in times]*unit

def find_crossing(func, desired_val, start_time, end_time, *args):
    """Finds the desired value boundary crossing time of a function of time."""
    # Use scipy optimize to find the boundary crossing times
    root = optimize.root_scalar(
        func,
        args=(desired_val, *args),
        bracket=[start_time, end_time],
        method='brentq'  # Brent method is generally robust
    )
    return root.root  # return the time of the boundary crossing

def find_crossings(func, desired_val, crossings_bounds, *args):
    """Given a list of bounds, this finds the desired value crossing times a function of time."""
    print(args)
    return [find_crossing(func, desired_val, start, end, *args,) for start, end in crossings_bounds]

def get_intervals(times, func, desired_val, crossings, *args):
    # Add start and end bounds  mn
    if crossings:
        if crossings[0] != times[0]:
            crossings = [times[0]] + crossings
        if crossings[-1] != times[-1]:
            crossings += [times[-1]]
    else:
        crossings = [times[0], times[-1]]

    # Append intervals to pos or neg list depending on whether the function is positive or negative at the midpoint
    pos = []
    neg = []
    for i in range(len(crossings) -1):
        mid_point = (crossings[i+1]- crossings[i]) / 2 + crossings[i]  # choosing a point between two roots
        if func(mid_point, desired_val, *args)  >= 0:
            pos.append((crossings[i], crossings[i+1]))
        else:
            neg.append((crossings[i], crossings[i+1]))
    return pos, neg


def positive_and_negative_indices(values):
    pos = []
    neg = []
    start = 0
    for i, v in enumerate(values):
        sign = 1 if np.sign(v) >= 0 else -1
        if i != 0:
            if sign != prev_sign:
                if sign < 0:
                    pos.append((start,i-1))
                    start = i
                else:
                    neg.append((start,i-1))
                    start = i
        prev_sign = sign
    if sign >= 0:
        pos.append((start,i))
    else:
        neg.append((start,i))
    return pos, neg

def to_portion_intervals(intervals):
    return P.Interval(*[P.closed(*i) for i in intervals])

# pos_ints, neg_ints = positive_and_negative_to_intervals([(0, 1), (3, 3)], [(2, 2), (4, 4)])
# all_ints = (pos_ints | neg_ints)
# crossing_ints = ~all_ints
# upper = all_ints.upper
# lower = all_ints.lower
# conv = lambda v: lower if v == -P.inf else (upper if v == P.inf else v)
# crossing_ints = crossing_ints.apply(lambda x: x.replace(lower=conv, upper=conv, ignore_inf=False))
# print(crossing_ints)
