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

Needs Claude Code with Artifacts publishing (private pages on claude.ai) and Python 3.

## Use

Ask your agent to "put this on a review page" or say "reviewbot" when it has a batch of decisions for you. When you've
answered, say "done" in chat.

## License

MIT
