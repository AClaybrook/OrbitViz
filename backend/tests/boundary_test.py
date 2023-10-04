import pytest
from boundary import find_crossing_bound_indices, positive_and_negative_indices

@pytest.mark.parametrize("values, expected", [
    ([3,2,1,0,-1,-2,-3,-2,-1,0,1,2,3], [(3, 4), (8, 9)]),
    ([1, -1, 1, -1, 1], [(0, 1), (1, 2), (2, 3), (3, 4)]),
    ([1, 1, 1, 1], []),
    ([-1, 0, 1], [(0, 1)]),
    ([1, 0, -1], [(1, 2)]),
    ([-1, 0, -1], [(0, 1), (1, 2)]),
    ([-1, 1, -1], [(0, 1), (1, 2)]),
    ([-1, 1, 1, 1, 1, -1], [(0, 1), (4, 5)]),
    ([1,2,-3,4,-5], [(1, 2), (2,3),(3,4)])
])
def test_crossing_bounds(values, expected):
    assert find_crossing_bound_indices(values) == expected


@pytest.mark.parametrize("values, expected", [
    ([1, 2, 3, 4, 5], ([(0, 4)], [])),
    ([-1, -2, -3, -4, -5], ([], [(0, 4)])),
    ([1, 2, 3, -4, -5], ([(0, 2)], [(3, 4)])),
    ([-1, -2, -3, 4, 5], ([(3, 4)], [(0, 2)])),
    ([1, 2, -3, 4, -5], ([(0, 1), (3, 3)], [(2, 2), (4, 4)]))
])
def test_positive_and_negative_indices(values, expected):
    result = positive_and_negative_indices(values)
    assert result == expected

