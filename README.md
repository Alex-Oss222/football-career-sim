# Football Career Sim

An LLM-first football simulation framework built around structured state, realistic progression, and role-based coaching/player systems.

---

## Overview

Football Career Sim is a persistent simulation system designed to model a football career across multiple seasons, roles, and organizations.

The system is built around:

- a master engine governing rules and realism
- player, coaching, and interview modules
- persistent state tracking (no resets between sessions)
- world and team-specific dossiers
- a structured progression system across seasons

The simulation is **state-driven**, not narrative-driven. Outcomes are based on role, performance, context, and progression — not story bias.

---

## Current Focus

Coach-first start:

- Alex Stone enters the January 1999 coaching carousel  
- Primary target: Philadelphia Eagles — Offensive Quality Control (QC)  
- Simulation currently progressing into Year 2 within the Eagles system  

---

## Core Architecture

### Engine Layer
- Governs realism, rules, and turn processing
- Controls time progression, evaluation systems, and outcomes

### Modules
- Player Module  
- Coaching Module  
- Interview Module  

Modules activate depending on the career phase.

### State System
The simulation persists through structured state files rather than chat memory.

---

## Persistence & Progression

This simulation does not restart between sessions.

It uses three core files:

- `alex_stone_current_state.yaml` → current live state (single source of truth)  
- `alex_stone_career_history.yaml` → long-term career log (append-only)  
- `alex_stone_relationship_ledger.yaml` → trust, politics, and relationships  

Only **one active state file exists at a time**.

Seasons are played across multiple chat sessions:
- each chat typically represents one season
- progression continues using the latest state file
- major milestones are archived

---

## Archive System

Snapshots are stored in:

```text
characters/archive/
