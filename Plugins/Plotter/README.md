# Math Equation Plotter

An interactive mathematical equation plotter plugin for Aura Text. It scans and highlights math equations/functions directly in your files in real-time and allows you to plot them instantly inside a dynamic dock widget.

## Features

- **Real-time Math Scanning & Highlighting**: Automatically detects and highlights math formulas and functions inside your code or text documents without interfering with normal text editing.
- **Dynamic Context Menu Interaction**: 
  - Left-clicking any highlighted formula opens a menu to plot it immediately.
  - Right-clicking a highlighted formula dynamically updates your context menu to show `"Plot Equation: <formula>"`.
  - Selecting any custom mathematical string and right-clicking allows you to plot custom selections.
- **Premium Plotting Dock**: Plots expressions inside a beautiful, Catppuccin-themed dock widget powered by Matplotlib.
- **Custom X-Range Controls**: Easily change the plotting domain range by setting the `Min X` and `Max X` input fields and clicking **Plot**.
- **Save/Export Plots**: Save your plotted curves as high-quality image files (`.png` or `.jpg`) directly from the dock.

## Supported Functions & Constants

The plotter parses and evaluates a wide array of mathematical operators and functions:
- **Variables**: `x`, `t`, `theta`
- **Constants**: `pi`, `e`
- **Trigonometric**: `sin`, `cos`, `tan`, `sec`, `csc`, `cot`
- **Inverse Trig**: `arcsin`, `arccos`, `arctan`
- **Hyperbolic / Inverse**: `sinh`, `cosh`, `tanh`, `arcsinh`, `arccosh`, `arctanh`
- **Exponential / Log**: `exp`, `log` (natural log), `log10`
- **Basic Functions**: `sqrt`, `abs`, `pow`, `ceil`, `floor`
- **Standard Operators**: `+`, `-`, `*`, `/`, `**` (or `^` for power)

## Getting Started

1. Open a document in Aura Text.
2. Type an expression or function. Examples:
   - `y = x**2 - 5*x + 6`
   - `f(x) = sin(x) + cos(x)`
   - `log(x)` (standalone expression)
3. Left-click the highlighted formula and select **Plot Equation**.
4. The plotter dock will open on the right displaying your graph.

## Requirements

The plotting functionality requires `matplotlib` and `numpy` to be installed in your python environment:
```bash
pip install matplotlib numpy
```
