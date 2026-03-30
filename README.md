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

This simulation persists across sessions using a structured file system.  
State is separated into **core runtime files** and **supporting evolution files**.

### Core Runtime Files (Required)

These define the current reality of the simulation:

- `alex_stone_current_state.yaml` → current live state (single source of truth)  
- `alex_stone_career_history.yaml` → long-term career log (append-only)  
- `alex_stone_relationship_ledger.yaml` → trust, politics, and relationships  

Only **one active state file exists at any time**.

---

### Supporting Evolution Files

These files evolve with the character but do not drive the simulation directly.  
They provide context for behavior, communication, and football understanding.

- `alex_stone_profile.md` → character identity and career-phase development  
- `alex_stone_voice.md` → communication style and behavioral tone (role-dependent)  
- `alex_stone_scheme_profile.md` → system knowledge, scheme mastery, and coaching-tree adaptation  

These files are updated **periodically**, not every turn.

---

### Usage Model

- Core runtime files are used to run the simulation  
- Supporting files shape how the character behaves within it  
- Archive folders store snapshots of all files at key career points  

The system remains **state-driven**, with personality and knowledge layered on top.
---

## Archive System

Snapshots are stored in:

```text
characters/archive/
