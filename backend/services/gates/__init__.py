"""
services/gates — modular gate functions extracted from _assemble_signal().

Each module exposes one public function with a consistent signature:
  (state_args...) -> tuple[action, confidence, cards, new_sources]
  OR for confidence-only gates:
  (state_args...) -> tuple[confidence, cards, new_sources]

_assemble_signal() calls each module and applies the returned updates.
Extracting gates here makes them independently unit-testable and reduces
the surface area of the monolithic _assemble_signal() function incrementally.

Modules:
  calendar         — §57 DOW gate, §77 tax-loss seasonal window
"""
