# Symbolic_Math_MCP

[![License](https://img.shields.io/github/license/ParisNeo/lollms_mcps_zoo.svg)](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE)

## Overview

**Symbolic_Math_MCP** is a Model Context Protocol (MCP) server for the [lollms](https://github.com/ParisNeo/lollms) ecosystem. It provides a suite of powerful symbolic mathematics tools, enabling Large Language Models (LLMs) to perform complex algebra and calculus operations with exact precision. Unlike a numerical calculator, which works with approximate numbers, this tool manipulates mathematical expressions and variables directly.

This MCP uses the industry-standard **SymPy** library as its backend.

---

## Features

-   **Algebraic Manipulation:** Solve equations, expand, factor, and simplify complex expressions.
-   **Calculus Operations:** Compute derivatives and both definite and indefinite integrals.
-   **Exact Results:** All computations are performed symbolically to provide exact answers (e.g., returning `sqrt(2)` instead of `1.414`).
-   **Focused Tools:** Provides distinct tools for different mathematical operations, making it easier for the LLM to achieve its goal.
-   **Self-Contained:** Automatically installs `sympy` and other dependencies on first launch using `pipmaster`.

---

## Tools and Usage

This MCP exposes multiple tools. An LLM can choose the appropriate one for the task at hand.

### `solve_equation`

Solves an equation for a specific variable.
-   **`equation`**: The equation to solve (e.g., `"x**2 - 4"`). Note: Set the expression equal to zero.
-   **`variable`**: The variable to solve for (e.g., `"x"`).
-   **Example Call**: `{"tool": "solve_equation", "equation": "x**2 - 4", "variable": "x"}`
-   **Result**: `{"status": "success", "result": "[-2, 2]"}`

### `simplify_expression`

Simplifies a mathematical expression.
-   **`expression`**: The expression to simplify.
-   **Example Call**: `{"tool": "simplify_expression", "expression": "sin(x)**2 + cos(x)**2"}`
-   **Result**: `{"status": "success", "result": "1"}`

### `expand_expression`

Expands a mathematical expression.
-   **`expression`**: The expression to expand.
-   **Example Call**: `{"tool": "expand_expression", "expression": "(x + y)**3"}`
-   **Result**: `{"status": "success", "result": "x**3 + 3*x**2*y + 3*x*y**2 + y**3"}`

### `factor_expression`

Factors a polynomial into its constituent parts.
-   **`expression`**: The expression to factor.
-   **Example Call**: `{"tool": "factor_expression", "expression": "x**3 - x**2 + x - 1"}`
-   **Result**: `{"status": "success", "result": "(x - 1)*(x**2 + 1)"}`

### `differentiate`

Computes the derivative of an expression.
-   **`expression`**: The expression to differentiate.
-   **`variable`**: The variable to differentiate with respect to.
-   **Example Call**: `{"tool": "differentiate", "expression": "cos(x) * x**2", "variable": "x"}`
-   **Result**: `{"status": "success", "result": "2*x*cos(x) - x**2*sin(x)"}`

### `integrate_expression`

Computes the integral of an expression.
-   **`expression`**: The expression to integrate.
-   **`variable`**: The variable of integration.
-   **`lower_bound`** (optional): The lower limit for definite integration.
-   **`upper_bound`** (optional): The upper limit for definite integration.

-   **Indefinite Integral Example**:
    -   **Call**: `{"tool": "integrate_expression", "expression": "x**2 + 1", "variable": "x"}`
    -   **Result**: `{"status": "success", "result": "x**3/3 + x"}`

-   **Definite Integral Example**:
    -   **Call**: `{"tool": "integrate_expression", "expression": "x", "variable": "x", "lower_bound": "0", "upper_bound": "10"}`
    -   **Result**: `{"status": "success", "result": "50"}`

---

## File Structure

-   `symbolic_math_mcp.py` — The main MCP server script.
-   `description.yml` — Metadata for integration with the lollms manager.
-   `requirements.txt` — A list of Python dependencies (handled automatically).
-   `README.md` — This documentation file.

---

## License

This MCP is part of the [lollms_mcps_zoo](https://github.com/ParisNeo/lollms_mcps_zoo) and is licensed under the [Apache 2.0 License](https://github.com/ParisNeo/lollms_mcps_zoo/blob/main/LICENSE).