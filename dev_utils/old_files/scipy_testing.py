from scipy.optimize import root_scalar
import numpy as np

# Define the function
def func(x):
    return x**3 - 4*x**2 - x + 4

# Broad range
a, b = -2, 5
# Number of points to sample
n_points = 1000
# Generate x values
x_values = np.linspace(a, b, n_points)
# Generate y values
y_values = func(x_values)

# Find intervals where the function changes sign
intervals = [(x_values[i], x_values[i+1]) for i in range(n_points-1) if np.sign(y_values[i]) != np.sign(y_values[i+1])]

# Find and print the roots in each interval
roots = []
for a, b in intervals:
    root = root_scalar(func, method='brentq', bracket=(a, b))
    roots.append(root.root)

print(f"Roots found: {roots}")

# Now, evaluate the function at points between these roots to find where it is positive.
intervals_sign = []
for i in range(len(roots) - 1):
    test_point = (roots[i] + roots[i+1]) / 2  # choosing a point between two roots
    if func(test_point) >= 0:
        intervals_sign.append((roots[i], roots[i+1]))

# Output the intervals where the function is positive
for interval in intervals_sign:
    print(f"The function is positive in the interval {interval}")
