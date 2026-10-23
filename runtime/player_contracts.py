"""Permanent player contract records, one per player (rebuild step 5; docs/rebuild_plan.md, step 5).

A placeholder until the contract builder replaces this body. The module stays outside the career
layer (tests/test_career_layer_isolation.py): it imports nothing from runtime.current_job,
runtime.decision_queue, scripts.render_career_views or any module in that test's LAYER, at module
level or inside a function, and takes what it needs as arguments.
"""
