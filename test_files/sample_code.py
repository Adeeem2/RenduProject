"""
Sample Python code for testing the Lab Report Generator.

This file contains a simple implementation of the Fibonacci sequence
and a visualization of the sequence using matplotlib.
"""

import matplotlib.pyplot as plt
import numpy as np

def fibonacci(n):
    """
    Calculate the Fibonacci sequence up to the nth term.
    
    Args:
        n (int): The number of terms to generate
        
    Returns:
        list: The Fibonacci sequence up to the nth term
    """
    if n <= 0:
        return []
    elif n == 1:
        return [0]
    elif n == 2:
        return [0, 1]
    
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[i-1] + fib_sequence[i-2])
    
    return fib_sequence

def plot_fibonacci(n):
    """
    Plot the Fibonacci sequence up to the nth term.
    
    Args:
        n (int): The number of terms to plot
    """
    sequence = fibonacci(n)
    
    plt.figure(figsize=(10, 6))
    plt.plot(range(len(sequence)), sequence, marker='o', linestyle='-', color='blue')
    plt.title(f'Fibonacci Sequence (First {n} Terms)')
    plt.xlabel('Term Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
    # Also create a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(range(len(sequence)), sequence, color='green')
    plt.title(f'Fibonacci Sequence Bar Chart (First {n} Terms)')
    plt.xlabel('Term Index')
    plt.ylabel('Value')
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Calculate and print the first 15 Fibonacci numbers
    n_terms = 15
    fib_sequence = fibonacci(n_terms)
    
    print(f"First {n_terms} Fibonacci numbers:")
    for i, num in enumerate(fib_sequence):
        print(f"F({i}) = {num}")
    
    # Plot the sequence
    plot_fibonacci(n_terms)