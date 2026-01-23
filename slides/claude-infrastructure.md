---
marp: true
theme: default
paginate: true
---

<!-- Context: [[claude-presentation-context-2026-01]] -->

# Infrastructure That Compounds

Cedar Ren
January 2026

---

# The Problem I'm Solving

Personal projects accumulate context.

- What did I learn last time I touched this code?
- What gotchas did I hit?
- What's the API key situation?

Every new Claude conversation starts from zero. Unless you build infrastructure.

---

# The Setup

```
~/.claude/
├── CLAUDE.md          # 56 lines. Working style. Every conversation.
├── skills/            # 15 skills. Accumulated knowledge.
│   ├── gmail/         # email triage + filter creation
│   ├── retro/         # friction → system improvement
│   └── convo-logs/    # search 2295 past sessions
```

Syncs across machines via chezmoi + Syncthing.

---

# CLAUDE.md: Teach Once

```markdown
## Communication
Think generously, communicate tersely.
Verbose reasoning internally → dense output externally.

## On Failure
Classify → act. Transient (retry) vs permanent (alternative).
Max 2-3 attempts per approach. Never loop.

## CEV
<- cev = Coherent Extrapolated Volition.
Figure out what I'd actually want. Do that, or ask.
```

56 lines. Applies to every conversation.

---

# Example: Commute Transit CLI

Built a CLI to plan my SF ↔ Mountain View commute.

**Friction → Fix cycle:**
```
me:     "why are there only 3 caltrain in the api response?"
        → merged realtime API + GTFS static schedule

me:     "uh could you not hardcode the mdf -> mtv ride time?"
        → fetch from live data instead

me:     "your caltrain schedule is probably off"
        → stopped using fallback values, validated against real schedules
```

Each fix goes into the codebase. Next session starts better.

---

# Example: Gmail Automation

Started: "help me triage 53 emails sitting in my inbox"

**What emerged:**
- Pattern-based filters (not sender whitelists)
- Monthly Review queue for "probably junk but maybe not"
- Recruiter reply drafting + batch send
- CCPA request generation from email history

**Core heuristic discovered:**
"Inbox is for decisions, not information storage."

Now encoded in the `/gmail` skill.

---

# Skills: Domain Knowledge That Persists

**Personal data:** gmail, obsidian, todoist, convo-logs
Greppable markers, ISO dates, decision frameworks

**Financial:** hsa-receipts, credit-cards
Track deadlines, maximize rewards

**Meta:** retro, extending-claude
Skills that improve the skill system itself

---

# Example: Obsidian as Knowledge Sink

Research sessions produce artifacts. Then I say "save to obsidian."

```
me:     [30 min researching CCPA opt-outs via Gmail API]
me:     "save to obsidian. CCPA will be ongoing."
claude: → projects/CCPA Privacy Opt-Outs.md
        (40 companies, methodology, template, legal notes)

me:     [tax planning session about QSBS]
me:     "my obsidian - does it have QSBS? incorporate."
claude: → finance/QSBS.md
        (hedging rules, state conformity, references)
```

Research happens once. Knowledge persists.

---

# Obsidian: Editorial Direction

I shape the distillation:

```
me:     "put summary on top, expand acronyms,
         rephrase using lesswrong language"
claude: [restructures]

me:     "add a state conformity chart"
claude: [adds chart]

me:     "anything missing? references?"
claude: [adds footnotes, primary sources]
```

Not just transcription. Structured knowledge I can query later.

---

# The Bidirectional Loop

**Writing:** Session insights → distilled to Obsidian
**Reading:** Future sessions check Obsidian first

```
me:     "what's that SEC filing that was abused?"
claude: [checks finance/10b5-1 Plans.md]
        "Form 144. Your notes say... but let me verify current status."

me:     "who would like this article about mechanism design?"
claude: [greps people/ for intellectual profiles]
        "Hayden (systems thinking), Karthik (governance)"
```

Past research becomes future context.

---

# Core Principles

**Fix the system, not the docs**
Workarounds become scripts. Gotchas become validation checks.

**Preferences as heuristics**
- "inbox is for decisions, not storage"
- "purgatory over loss"
- "ball in whose court?"

**Patterns over whitelists**
Rules that work for future unknown cases.

---

# The Retro Loop

After a session, I run `/retro`:

```
me:     "the retro skill is kinda bad"
claude: [explains what it learned about my preferences]
me:     "write me a new retro skill"
```

**Friction → extract learnings → fix the system**

The gmail skill exists because of a retro.
The retro skill was rewritten because of a retro.

---

# Cross-Session Memory

```bash
convo-logs search "commute" --expand
# Finds: commute, transit, caltrain, bart, muni, 511...

convo-logs analyze redirections --limit 20
# Shows: what Claude was thinking before I corrected it
```

If I'm correcting Claude repeatedly →
That's a candidate for CLAUDE.md.

**The conversations become training data for the system.**

---

# Concrete Example: The Payoff

**Commute project, January 8:**
```
me:     "i intend to leave office after 2:45.
         Suggest some best commutes. No bike today."
claude: [produces options using learned station preferences,
         backtracking logic, realtime + static schedule merge]
```

No setup. No re-explaining. It already knows the project.

---

# The Compound Effect

Each improvement applies to **all future sessions**.

- Commute gotchas fixed Dec 18 → still working
- Gmail heuristics learned Jan 3 → still working
- Retro skill rewritten → better retros forever

**Value:** Less repetition. Context that persists.

---

# Questions?

```
~/.claude/CLAUDE.md
~/.claude/skills/
```
