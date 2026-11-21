"""Shared helpers for the PlantIQ comparison study (data, metrics, training utilities, LLM access).

Notebooks put the `compare/` folder on sys.path (see `bootstrap()` in every notebook's first cell) and import
`common.*`. Keeping these in .py files makes every model use the same evaluation code, and lets PyTorch
data-loader workers start on Windows (they cannot unpickle functions defined inside a notebook).
"""
