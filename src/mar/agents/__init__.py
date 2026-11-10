"""Agent backends for the fishery: scripted mocks, Jev (a decision model) and chat LLMs.

No network is touched unless a backend is asked to make a call. Keys come only from the environment
(see env.py). All HTTP goes through http.post_json so tests can replace it.
"""
