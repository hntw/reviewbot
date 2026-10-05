# reviewbot

[![Watch the 65-second explainer](https://hntw.github.io/reviewbot/poster.jpg)](https://hntw.github.io/reviewbot/)

An agent can make 60 things in an afternoon, and then it asks you about all 60 in chat, and the questions scroll away.
The building part is fast. The bottleneck is you.

reviewbot is a Claude Code plugin. Kick off a huge session and go to sleep. When you wake up, or when you hit the cafe
for a spro, the whole batch is waiting on one private page. Each card shows the real work with one question: Approve,
Change or Hold, plus a notes box. Answers save as you tap, on your phone, your laptop, the Claude app or a browser. Say
"done" and Claude Code reads every answer and every note straight from the page, and gets to work.

A tap on Approve means "this is right." It doesn't mean "ship it." Anything that goes live still needs you to say so in
chat, and the page hands you the exact line to paste.

## Install

```
claude plugin marketplace add hntw/reviewbot
claude plugin install reviewbot@reviewbot
```

Update later with `claude plugin update reviewbot@reviewbot`.

## Where it works

Claude Code only (terminal, IDE extensions, or the desktop app's Code tab). It needs Claude Code's Artifact publishing
and Python 3 on your machine. If the skill loads in claude.ai chat or Cowork, it tells you it runs in Claude Code and
stops.

## What it runs and sends

- Runs two small Python scripts from `skills/reviewbot/kit/` on your machine: `make.py` builds the review page from a
  `review.json` your agent writes (and keeps each question's number in a small `refs.json`), and `answers.py` turns
  your saved answers into a table.
- Publishes each review page as a private Claude Artifact on your own claude.ai account. Your answers are stored in
  that page's database on claude.ai. Nothing is sent anywhere else.
- The review page loads two fonts (Archivo and Open Sans) from Google Fonts when you open it.
- No hooks, no MCP servers, no background processes, no network calls from the scripts.

## Use

Ask your agent to "put this on a review page" or say "reviewbot" when it has a batch of decisions for you. When you've
answered, say "done" in chat.

Each page has a short code and each question a small number (like `PW-R1 #3`). They're there so you and your agent can
point at one decision later, in the same chat or a new one. They also show up in the line you paste to approve a
production change.

## License

MIT
