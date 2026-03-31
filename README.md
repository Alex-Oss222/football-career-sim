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
- structured offseason evaluation and hiring cycles  
- role-based progression across coaching levels  

The simulation is **state-driven**, not narrative-driven. Outcomes are based on role, performance, reputation, and organizational context — not story bias.

---

## Current Focus (2011 Job Cycle)

The simulation is currently in the **2011 NFL offseason hiring cycle**.

Alex Stone is:

- A **43-year-old coach**
- Former **NFL Passing Game Coordinator (San Diego Chargers)**
- Former **College Head Coach (Memphis)**
- Former **NFL Position Coach and QC (Philadelphia Eagles)**

Current status:

- **Free agent coach**
- **Active OC candidate**
- Résumé at its strongest point  
- Entering a critical career inflection point  

Primary targets:

- Jacksonville Jaguars  
- Indianapolis Colts  

Objective:

- Secure an **Offensive Coordinator role**
- Establish long-term NFL trajectory toward **Head Coach candidacy**

---

## Core Architecture

### Engine Layer
- Governs realism, rules, and simulation flow  
- Controls time progression, evaluation systems, and hiring outcomes  

### Modules
- Coaching Module  
- Interview Module  
- Job Market / Hiring Logic  

Modules activate depending on phase (season, offseason, job cycle).

---

## State System

The simulation persists through structured state files rather than chat memory.

### Core Runtime Files (Required)

- `alex_stone_current_state.yaml` → current live state (single source of truth)  
- `alex_stone_career_history.yaml` → long-term career log (append-only)  
- `alex_stone_relationship_ledger.yaml` → trust, politics, and network  

Only **one active state file exists at any time**.

These files define:
- role
- team context
- reputation
- relationships
- job market status

---

## Supporting Evolution Files

These shape how Stone behaves, communicates, and thinks:

- `alex_stone_profile.md` → identity and career evolution  
- `alex_stone_voice.md` → communication style and authority level  
- `alex_stone_scheme_profile.md` → system knowledge and philosophy  

These are updated at **major career phases**, not every turn.

---

## Current Simulation Phase

```text
Phase: Offseason — 2011 Job Cycle Active
Date: January 1, 2011
Status: Free Agent Coach (HC and OC Candidate)
