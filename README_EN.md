# vtb.skill

This repo is for turning a VTuber you care about into a real `.skill` you can install, maintain, and keep enriching over time.

<table>
  <tr>
    <td width="50%" align="center" valign="top">
      <a href="https://github.com/ly-xxx/ace-taffy-skill">
        <img src="./assets/example-card-taffy.svg" alt="ace-taffy example repo card" width="100%" />
      </a>
    </td>
    <td width="50%" align="center" valign="top">
      <a href="https://github.com/ly-xxx/mocha.skill">
        <img src="./assets/example-card-mocha.svg" alt="mocha example repo card" width="100%" />
      </a>
    </td>
  </tr>
</table>

VTubers are often remembered through scattered public traces: a dynamic post, a clip, a stream archive, a room description, a few lines people quote again and again.

By the time you seriously want to preserve someone well, their public material is already spread across platforms, and the parts that matter most, cadence, tone, recurring habits, the feel of how they speak, are easy to flatten into cliché.

That is why building a VTuber `.skill` should be more than writing a few lines of imitation. It should be a careful, source-grounded repo you can revisit and keep maintaining.

Most people do not get stuck on “write one line that sounds like them”.

They get stuck on everything around it:

- finding public sources and verifying them
- collecting profiles, dynamics, live-room info, and video pages together
- deciding which public videos are worth transcribing
- separating stable persona structure from catchphrases and recurring bits
- turning all of that into a repo someone can actually install and maintain

That is the part `vtb.skill` is built for.

It focuses on:

- public-source collection from Weibo and Bilibili
- bilibili space-dynamic collection with partial flush + resume state
- transcript generation from public videos
- auditable corpus building
- writing reusable character skill repos instead of one-off prompt dumps
- keeping multi-axis persona balance instead of overfitting one recurring gag

## What You End Up With

If you use this framework to distill a new VTuber skill, the usual end result is:

- an installable skill for Codex / Claude Code
- a clear persona skeleton:
  `SKILL.md`, `persona.md`, `references/profile.md`, `distillation.md`, `expression-dna.md`, `boundaries.md`, `sources.md`
- a target manifest plus reusable collection settings
- rerunnable public-source, STT, audit, and style-bank workflows
- a user-facing README, install guide, and real examples

In other words, this framework is not only about “writing like someone”. It is about producing a skill repo that can be installed, reviewed, refreshed, and extended.

## What This Framework Does Well

- verifies public Bilibili / Weibo entry points before asking users to fill manifests
- handles profile, dynamics, live-room metadata, video pages, and public-video transcription in one workflow
- supports single-source fallback instead of collapsing when only one platform is available
- supports long-running collection with resume state
- separates stable persona axes from optional recurring motifs
- exports transcript formats that work with common editing and subtitle tools

## One-Minute Start

If your goal is simply “help me make a skill for my favorite VTuber”, do not start with scripts.

Install `create-vtb`, then paste this to Codex or Claude Code:

```text
Please use create-vtb to build a new VTuber skill for XXX.
First verify public Bilibili and Weibo sources by yourself.
If only one platform is available, continue with a single-source build.
If both are missing, stop and tell me why.
By default, create the repo, README, install guide, and a few runnable examples.
```

If you want style control, add:

```text
Please preserve: XXX.
Please avoid: XXX.
```

If you want a bundled in-repo example, add:

```text
Please build it as vtb.skill/examples/xxx.skill.
```

## What The User Needs To Provide

- Minimum input is just the character name.
- Better input is the character name plus style constraints to keep or avoid.
- Source links help, but they are optional. `create-vtb` should verify public sources first by default.

## What create-vtb Does By Default

- verifies whether stable public Bilibili / Weibo sources exist
- writes confirmed sources into the target manifest and leaves missing ones explicit
- collects profile, dynamic/feed, video, and live-room public data
- selects suitable public videos for STT and exports editor-friendly formats
- generates an installable skill repo plus README, install guidance, and example prompts
- stops clearly when evidence is too weak instead of pretending the distillation is valid

## Install

### Fastest Install

If you mainly want to get started quickly:

```bash
git clone https://github.com/ly-xxx/vtb.skill ~/work/vtb.skill
mkdir -p ~/.codex/skills ~/.claude/skills
ln -snf ~/work/vtb.skill ~/.codex/skills/create-vtb
ln -snf ~/work/vtb.skill ~/.claude/skills/create-vtb
```

If you only use Codex or only use Claude Code, keep the matching symlink only.

### Prerequisites

```bash
pip3 install -r requirements.txt
```

You should also have:

- `ffmpeg`
- Python 3.9+
- `git`

### Know The Four Install Targets

- `create-vtb`: the framework skill
- `ace-taffy`: bundled Yongchu Taffy example
- `aza`: bundled Aza example
- `mocha`: bundled bilibili-only example

## Creating A New Character By Chat

Prefer telling Codex / Claude Code directly:

```text
Please use create-vtb to build a new VTuber skill for XXX.
First verify public Bilibili and Weibo sources by yourself.
If one source is missing, leave it empty and tell me.
If both are missing, stop and do not build the skill.
```

Useful prompt variants:

```text
Please use create-vtb to build a new VTuber skill for XXX.
Please preserve: stream cadence, public-facing tone, greeting style.
Please avoid: generic moe-template writing, quote-dumping, and overusing one catchphrase.
```

```text
Please use create-vtb to build a standalone repo named xxx.skill for XXX.
Verify public sources first, then generate the installable skill, README, install instructions, and example prompts.
```

### Codex

Install the framework:

```bash
mkdir -p ~/.codex/skills
git clone https://github.com/ly-xxx/vtb.skill ~/.codex/skills/create-vtb
```

For local development, a symlink is usually better:

```bash
git clone https://github.com/ly-xxx/vtb.skill ~/work/vtb.skill
mkdir -p ~/.codex/skills
ln -snf ~/work/vtb.skill ~/.codex/skills/create-vtb
```

Install the bundled examples from a local checkout:

```bash
mkdir -p ~/.codex/skills
ln -snf "$(pwd)/examples/taffy.skill" ~/.codex/skills/ace-taffy
ln -snf "$(pwd)/examples/aza.skill" ~/.codex/skills/aza
ln -snf "$(pwd)/examples/mocha.skill" ~/.codex/skills/mocha
```

Smoke-test prompts:

```text
Please use create-vtb and tell me how to create a target manifest for a new VTuber.
```

```text
Please use ace-taffy and write one short public-facing fan reply.
```

```text
Please use aza and write one stream announcement for 8pm tonight.
```

```text
Please use mocha and write one short game-stream title.
```

### Claude Code

Global install:

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/ly-xxx/vtb.skill ~/.claude/skills/create-vtb
```

Project-local install:

```bash
mkdir -p .claude/skills
git clone https://github.com/ly-xxx/vtb.skill .claude/skills/create-vtb
```

Bundled examples from a local checkout:

```bash
mkdir -p ~/.claude/skills
ln -snf "$(pwd)/examples/taffy.skill" ~/.claude/skills/ace-taffy
ln -snf "$(pwd)/examples/aza.skill" ~/.claude/skills/aza
ln -snf "$(pwd)/examples/mocha.skill" ~/.claude/skills/mocha
```

Smoke-test commands:

```text
/create-vtb
```

```text
/ace-taffy Write one short stream announcement.
```

```text
/aza Write one playful fan reply.
```

```text
/mocha Write one short game-stream response.
```

## What This Repo Is For

- collecting stable public metadata
- downloading public Bilibili media
- exporting `json + srt + vtt + tsv + txt` transcripts
- building style banks and train-ready transcript sets
- scaffolding per-character skill repos
- separating core persona axes from optional running motifs
- making the chat-first onboarding path clear for Codex and Claude Code users

## Bundled Examples

- [examples/taffy.skill](examples/taffy.skill): a bundled mature example that can also be refreshed inside the framework pipeline
- [examples/aza.skill](examples/aza.skill): a framework-native public-source demo distilled from `阿萨Aza`, with Weibo posts, Bilibili videos, and Bilibili space dynamics collected into the same pipeline, while keeping recurring motifs as optional seasoning instead of the full skeleton
- [examples/mocha.skill](examples/mocha.skill): a bilibili-only example showing the single-source fallback flow, now with space dynamics included and stronger bedside / strawberry / dumpling anchors

`collect_bilibili_public.py` writes partial step outputs plus `sources/raw/bilibili/_collector_state.json`, so long-running collection can resume after interruptions.

For `mocha.skill`, the verified public source is Bilibili only:

- mid: `212535360`
- live room: `21849412`
- no stable official Weibo page was verified during this run, so Weibo is intentionally left empty

## Scope Boundary

This is not:

- a live VTuber engine
- a TTS runtime
- an avatar/Live2D controller
- a gossip or private-identity investigation toolkit
