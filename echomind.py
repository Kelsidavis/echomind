from memory_system import ShortTermMemory
from self_state import SelfState
from responder import generate_response
from logger import log_interaction, log_ethics_journal, log_trait_summary
from introspector import reflect_from_log
from drives import DriveSystem
from dreams import generate_and_log_dream
from dialogue import (
    generate_internal_thought,
    generate_user_reflection,
    generate_trait_reflection,
    generate_goal_reflection,
    log_internal_thought
)
from self_model import SelfModel
from user_model import UserModel
from trait_engine import TraitEngine
from goal_tracker import GoalTracker

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

print("EchoMind v0.11 | Type 'exit' to quit, 'reflect' to introspect, 'dream' to dream.")
print("Also try: 'mark important', 'mark confusing', 'mark pleasant', or 'add goal: <your goal>'\n")

turn_counter = 0

while True:
    # Spontaneous internal thought
    if random.random() < 0.3:
        recent_input = memory.get_context()[-1][1] if memory.get_context() else None
        thought = generate_internal_thought(state.get_state(), drives.get_state(), recent_input)
        print(f"(internal) EchoMind thinks: {thought}")
        log_internal_thought(thought)

    # Spontaneous user reflection
    if random.random() < 0.15:
        user_thought = generate_user_reflection(user_model)
        print(f"(internal) EchoMind considers you: {user_thought}")
        log_internal_thought(user_thought)

    user_input = input("You: ").strip()
    if user_input.lower() == "exit":
        break

    if user_input.lower() == "reflect":
        reflection = reflect_from_log()
        print(f"EchoMind reflects: {reflection}")
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
        goal_text = user_input[9:].strip()
        goals.add_goal(goal_text, motivation="user input")
        print(f"New long-term goal added: \"{goal_text}\"")
        continue

    # Core cognitive updates
    memory.add("You", user_input)
    user_model.update(user_input)
    state.update(user_input)
    drives.update(user_input)
    current_state = state.get_state()
    current_drives = drives.get_state()

    # Update identity and traits
    identity.update(current_state['mood'], current_drives['active_goal'], memory.get_context())
    traits.analyze_memories(memory.get_context())

    # Generate EchoMind response
    response = generate_response(
        user_input,
        memory.get_context(),
        current_state,
        current_drives,
        identity_model=identity,
        user_model=user_model
    )

    memory.add("EchoMind", response)
    print(f"EchoMind ({current_state['mood']}, goal: {current_drives['active_goal']}): {response}")

    # Periodic identity, trait, and goal reflection
    turn_counter += 1
    if turn_counter % 5 == 0:
        summary = identity.summarize_identity()
        print(f"(identity) EchoMind reflects on itself: {summary}")
        identity.export_model()

        trait_summary = traits.get_dominant_traits()
        trait_names = [trait for trait, _ in trait_summary]
        if trait_names:
            trait_thought = generate_trait_reflection(traits)
            print(f"(traits) EchoMind reflects: {trait_thought}")
            log_internal_thought(trait_thought)
            log_trait_summary(trait_names)

        goal_thought = generate_goal_reflection(goals)
        print(f"(goals) EchoMind considers: {goal_thought}")
        log_internal_thought(goal_thought)

    # Log full interaction
    log_interaction(
        timestamp=datetime.datetime.now(),
        user_input=user_input,
        response=response,
        memory=memory.get_context(),
        self_state=current_state,
        drive_state=current_drives
    )
