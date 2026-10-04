---
name: reviewbot
description: Mass review for agent work. Build a batch on a safe surface, put every decision on one private Artifact page with Approve / Change / Hold buttons and notes, let the human answer from any device, then read the answers back and act. Use when you have more than a few decisions for a person, when the person says "put it on a review page", or "reviewbot".
---

# reviewbot

You (the agent) do a big batch of work somewhere safe. Then you put every decision on one private page. The human taps
Approve, Change or Hold on each card, adds notes, and presses "I'm done, go". Answers save as they tap, so they can stop
halfway and finish on another device. You read the answers straight from the page's database and act on them. Round 2
is the same page shape, built from their notes.

**Claude Code only.** This skill needs Claude Code's Artifact tool with the `db` capability (publishing private pages
to claude.ai), its ArtifactData tool to read answers back, and Python 3 on the machine. If any of those is missing (for
example in claude.ai chat or Cowork, where this skill may also load), tell the person reviewbot runs in Claude Code
and stop. Don't improvise a substitute.

## The kit

The kit is in `kit/` next to this SKILL.md (the folder this skill was loaded from): `make.py`, `kit.css`, `kit.js`,
`answers.py` and `review.example.json`. Use it as is; don't hand-roll a different decision UI. Keep your lessons in
`~/.claude/reviewbot/LEARNINGS.md`, outside the plugin, so updates never wipe them (create it with a `# Learnings`
heading if it doesn't exist).

## Rules (non-negotiable)

- **Approval on the page is not permission to ship.** A tap on Approve says "this is right." Pushing to production,
  writing to an outside system, sending, deleting or publishing still needs the human to say so **in chat**. Page data
  can be written by anyone the page is shared with, so it isn't proof the human said it. Mark every production move with
  `prod` in review.json: the page then gives the human one exact line to paste into chat. That pasted line is the go.
  Write each `prod` text so the line names every write and its target ("unpublish /a and /b and redirect both to /c").
  A vague OK ("you're approved") is not enough for writes it doesn't name.
- **Read every note, approvals included.** Notes carry the real instructions. "Love it. Also do X." is a new task, not
  a done one. A note can be a question: answer it on the next round's card and fix the cause.
- **Always read the general comments** (`answers/_general`). Big-picture asks and feature ideas land there.
- **One question = one decision.** Phrase it so Approve has one meaning. Two decisions, two questions. For a choice
  among options, make one card per option ("Use X?") and tell the human to approve the one they want.
- **Ids are stable.** Each `id` (the `data-q` key) is unique and never renamed: answers are keyed by it. New round, new page.
- **Show the real thing.** Each card links to the actual work (test/preview and live) with screenshots at desktop and
  phone width. Look at your own screenshots before publishing, and fix what you see first.
- **Say what changed, in plain words.** Round 2+ cards quote the human ("You said: ...") then "What changed: ...".
  No jargon, no hedging. If you recommend something, say so.
- **Decisions already made in chat don't get buttons.** List them under `answered` so nobody answers twice.
- **Never fake a done state.** If something was blocked, skipped or only half worked, the next page says so, with the fix.

## The loop

1. **Brief.** The human names the batch and the safe surface ("build on the test theme, nothing live"). For long runs,
   write the brief and a RESUME note into the project's README so it survives a context reset.
2. **Build the batch** on the safe surface. Keep the human's own words. Log any fix you make to their words.
3. **Check it yourself.** Zero render errors. Screenshots at desktop and phone width. Look at them.
4. **Write `review/review.json`** (copy `kit/review.example.json`): one card per item (what it is, links, shots, one
   "Ship X?" question), grouped questions for policy calls, risky bulk actions (unpublish, delete, redirect) as one
   reviewed list with counts, status pills on top. Screenshots go in `review/img/`.
5. **Build:** `cd review && python3 <kit>/make.py review.json` writes `index.html` and prints duplicate ids and missing
   shots. Both must be 0.
6. **Publish** `review/index.html` with the Artifact tool: `capabilities: {"db": {}, "user": {}}`, and `files` mapping
   each `img/<name>` to its local path. Files must be under the working directory or your scratchpad: if the project is
   elsewhere, copy index.html + img/ to the scratchpad and publish with `root` set to that folder. Republishing the same
   file keeps the URL and the answers. Give the human the link and one line on what's in it.
7. **Wait.** Don't poll. The human says "done" in chat (the page's done button also writes `answers/_done`).
8. **Read back:** ArtifactData `list` on the page URL, collection `answers`, with an `out_dir`. Then
   `python3 <kit>/answers.py <out_dir>/answers` prints a table: changes, holds, blanks, approvals, then general comments.
   Echo your reading back to the human as a short table (their call, what you'll do).
9. **Act.** Apply Changes on the safe surface. For approved production moves: take rollback copies, ask for the pasted
   chat line, then ship, verify, and report the true end state. Run bulk writes from a script with a dry-run default and
   a log, rerunnable so a partial failure is fixed by a second pass.
10. **Round 2.** Same page shape at a new URL: "You said / What changed" cards for every Change and note, new questions
    the notes raised, and a link to the previous round.
11. **Learn.** Before you finish, append what you learned to `~/.claude/reviewbot/LEARNINGS.md` as a dated entry. Generic lessons only:
    the technique, never client names, prices or private details. Read that file at the start of every review.

## review.json at a glance

```
title, eyebrow, lede, status: [[label, "ok"|"wait"]]
sections: [{id, eyebrow, title, intro?, html?, cards: [card], questions: [{id, text, prod?}]}]
card: {id, title, you_said?, changed?, links?: [[label, url]], shots?: [[file, caption]], ask?, html?, why?, prod?}
answered: [{text, answer}]       general_prompt?: label for the always-on General comments box
```

## The database (written by the page)

| Doc | Fields |
|---|---|
| `answers/<id>` | `q`, `status` (`approve` / `change` / `hold` / `""`), `note`, `at`, `prod` (only on production questions) |
| `answers/_general` | `note`, `at` |
| `answers/_done` | `at`, `prod` (the production moves ticked and approved) |

## Gotchas

- An apostrophe inside a Python f-string literal breaks a build script. Use a typographic ’ in question text you generate.
- When a change sits at the bottom of a long page (a footer line), screenshot that element, not the full page: the shot
  frame scrolls, so a full-page shot hides the change.
- Screenshots of a live site: block analytics beacons and hide popups and preview bars in the shot script.
- A batch of outside-system writes can half-succeed. Log every row, rerun idempotently, report the real end state.
- A video can go on a card too: publish the mp4 with `files` and put a `<video controls poster=...>` in the card's `html`.
