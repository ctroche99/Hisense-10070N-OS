# Hisense-10070N-OS

Making a **Hisense 100U70N** (100" U70 series QLED, Google TV) lean, quiet and ad-free, without breaking it.

## The short version

You **can't** replace the TV's operating system with a lean build. No custom ROM, AOSP or LineageOS build exists for any Hisense TV or for its MediaTek Pentonic 700 (MT9618) chip. Hisense's firmware files are encrypted, and root has only been done by hand on other Hisense boards, using a serial cable. See [docs/research-report.md](docs/research-report.md).

What you **can** do is strip the TV down, and every step can be undone:

1. **Settings:** turn off Hisense's viewing tracking (ACR), ad personalisation and slow animations.
2. **Projectivy Launcher:** an ad-free home screen, set up with no computer.
3. **ADB debloat:** freeze Hisense ad, tracking and helper apps plus Google leftovers, in small tested batches.

Expect a cleaner, ad-free TV with less tracking, plus snappier menus. Don't expect a dramatically faster one: the only measured gain on a similar Hisense was about 80 MB more free RAM. For the best speed, use an external streamer, but still do steps 1 and 3, because the TV's ACR also fingerprints HDMI inputs.

## What's here

| Path | What it is |
|---|---|
| [docs/setup-checklist.md](docs/setup-checklist.md) | Step-by-step checklist. **Start here.** |
| [docs/research-report.md](docs/research-report.md) | The research behind it, with sources |
| `tvdebloat.py` | Reversible debloat tool (Python 3, standard library only, needs `adb`) |
| `packages/batch1-hisense.txt` | Hisense ads, ACR and clutter |
| `packages/batch2-google.txt` | Google leftovers |
| `packages/batch3-optional.txt` | Removals that cost a feature; applied one at a time |
| `packages/batch4-launcher.txt` | Stock Google TV home and its setup fallback (only after Projectivy) |
| `packages/never-touch.txt` | Packages the tool refuses to disable, whatever list they appear in |

## The tool

```
python3 tvdebloat.py connect 192.168.1.50   # your TV's IP; accept the prompt on the TV
python3 tvdebloat.py info                    # model, Android version, memory
python3 tvdebloat.py baseline                # save a snapshot before changing anything
python3 tvdebloat.py check batch1            # dry run: what exists on your TV, what would change
python3 tvdebloat.py apply batch1 --reboot   # disable, wait 15 s, reboot
python3 tvdebloat.py status                  # what's disabled; flags anything that came back
python3 tvdebloat.py rearm                   # re-disable anything an update turned back on
python3 tvdebloat.py restore --all --reboot  # undo everything this tool did
python3 tvdebloat.py tweaks apply            # animations to 0.5x (tweaks revert = back to 1x)
```

On Windows, use `python` or `py` instead of `python3`.

Safety rules built into the tool:

- It only ever uses `pm disable-user --user 0`. It never uninstalls, and `restore` re-enables with `pm enable`.
- It skips packages that aren't on your TV and refuses anything on `packages/never-touch.txt`, including every `com.mediatek.*` package, the remote and picture services, Play Services and firmware updates.
- Batch 3 only runs one package at a time (`--only <package>`).
- Batch 4 refuses unless Projectivy is installed, and always disables the stock launcher and setup wizard together.
- Every change is logged to `logs/changes.jsonl`, which git ignores, so `restore` undoes exactly what the tool did. It won't touch apps that were disabled from the factory.

## Caveats

The package names and safety ratings come mainly from a 2024 Hisense 55U8N, which has the same chip family and Google TV generation, and from older Hisense lists. **None of it has been tested on a 100U70N yet.** Always run `check` before `apply`, go one batch at a time, and test the remote, inputs, HDMI, sound and casting after each reboot. If a Hisense or MediaTek package isn't in these lists and you can't identify it, leave it alone.

Turn USB debugging off when you're done, because network ADB is open to your whole home network.
