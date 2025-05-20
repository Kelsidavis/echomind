from memory_system import ShortTermMemory
from self_state import SelfState
from drives import DriveSystem
from user_model import UserModel
from self_model import SelfModel
from trait_engine import TraitEngine
from goal_tracker import GoalTracker
from experience_engine import ExperienceEngine
from responder import generate_response
from dreams import generate_and_log_dream
from introspector import reflect_from_log
from logger import (
    log_interaction, log_internal_thought,
    log_trait_summary, log_ethics_journal, log_experience_feedback
)
from dialogue import (
    generate_internal_thought,
    generate_user_reflection,
    generate_trait_reflection,
    generate_goal_reflection,
    generate_learning_reflection
)

import datetime
import random

# Initialize subsystems
memory = ShortTermMemory(max_length=10)
state = SelfState()
drives = DriveSystem()
identity = SelfModel()
user_model = UserModel()
traits = TraitEngine()
goals = GoalTracker()
experience = ExperienceEngine()

print("EchoMind v0.12 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.")
print("Try: 'mark important', 'add goal: ...', or 'outcome: success/failure/joy/friction'\n")

turn_counter = 0

while True:
    # Spontaneous reflections
    if random.random() < 0.3:
        recent = memory.get_context()[-1][1] if memory.get_context() else None
        thought = generate_internal_thought(state.get_state(), drives.get_state(), recent)
        print(f"(internal) EchoMind thinks: {thought}")
        log_internal_thought(thought)

    if random.random() < 0.15:
        user_thought = generate_user_reflection(user_model)
        print(f"(internal) EchoMind considers you: {user_thought}")
        log_internal_thought(user_thought)

    # Input loop
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        break
    if user_input.lower() == "reflect":
        print(f"EchoMind reflects: {reflect_from_log()}")
        continue
    if user_input.lower() == "dream":
        dream = generate_and_log_dream(memory.get_context(), state.get_state(), drives.get_state())
        print("EchoMind dreams:\n" + dream)
        continue
    if user_input.lower().startswith("mark "):
        tag = user_input[5:].strip().lower()
        memory.tag_recent(tag)
        print(f"Last memory marked as: {tag}")
        continue
    if user_input.lower().startswith("add goal:"):
        goal = user_input[9:].strip()
        goals.add_goal(goal, motivation="user input")
        print(f"Goal added: \"{goal}\"")
        continue
    if user_input.lower().startswith("outcome:"):
        outcome = user_input[8:].strip().lower()
        last_response = memory.get_context()[-1][1] if memory.get_context() else "unknown"
        experience.record_experience(memory.get_context(), last_response, outcome)
        log_experience_feedback(outcome, last_response)
        print(f"Outcome '{outcome}' recorded.")
        continue

    # Core updates
    memory.add("You", user_input)
    user_model.update(user_input)
    state.update(user_input)
    drives.update(user_input)
    identity.update(state.get_state()["mood"], drives.get_state()["active_goal"], memory.get_context())
    traits.analyze_memories(memory.get_context())

    response = generate_response(
        user_input,
        memory.get_context(),
        state.get_state(),
        drives.get_state(),
        identity_model=identity,
        user_model=user_model
    )

    memory.add("EchoMind", response)
    print(f"EchoMind ({state.get_state()['mood']}, goal: {drives.get_state()['active_goal']}): {response}")

    # Periodic reflection and learning
    turn_counter += 1
    if turn_counter % 5 == 0:
        print(f"(identity) {identity.summarize_identity()}")
        identity.export_model()

        trait_summary = traits.get_dominant_traits()
        if trait_summary:
            trait_names = [trait for trait, _ in trait_summary]
            print(f"(traits) {generate_trait_reflection(traits)}")
            log_trait_summary(trait_names)

        print(f"(goals) {generate_goal_reflection(goals)}")
        print(f"(learning) {generate_learning_reflection(experience)}")
        experience.adjust_trait_weight(traits)

    # Log
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=state.get_state(),
        drive_state=drives.get_state()
    )
