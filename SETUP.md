# Setup (5 minutes)

Your profile repo is `Blankk18/Blankk18`. Copy everything from this kit into it, keeping the folder structure:

```
README.md
SETUP.md                      (optional, delete after)
assets/                       (all the .svg files)
scripts/build_assets.py
scripts/generate_stats.py
.github/workflows/snake.yml
.github/workflows/stats.yml
```

1. **Upload** the files (drag the folders into the repo on github.com, or `git add . && git commit && git push`).
2. **Allow Actions to push:** repo → Settings → Actions → General → Workflow permissions → *Read and write permissions* → Save.
3. **Run both workflows once:** Actions tab → "Refresh profile stats" → Run workflow, then "Contribution snake" → Run workflow.
4. Refresh your profile. Stats and the snake now update themselves every 12 hours.

## Changing things

- Name, typed lines, terminal text, skills, project cards, footer line: edit the CONFIG block at the top of `scripts/build_assets.py`, then run `python scripts/build_assets.py` and commit the new `assets/` files.
- Add a project: copy one dict in `PROJECTS`, then add a matching `<td>` in `README.md` pointing at its repo.
- Colors: the palette lines sit right under CONFIG in `build_assets.py`.
- Contributions from private repos: GitHub's default token only sees public activity. For private counts, create a personal access token (read:user), save it as a repo secret named `STATS_TOKEN`, and in `stats.yml` change `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}` to `GITHUB_TOKEN: ${{ secrets.STATS_TOKEN }}`, and turn on "Include private contributions on my profile" in your profile settings.

## If something looks off

- Stats card shows "n/a" for contributions or streak: the Stats workflow hasn't run yet, or the token lacks access. Run it from the Actions tab.
- Snake missing: run the "Contribution snake" workflow once so the `output` branch exists.
- Old version still showing: GitHub caches images for a few minutes. Hard refresh.
- Typing and scrolling animations pause for people who have "reduce motion" turned on; they see a static version.
