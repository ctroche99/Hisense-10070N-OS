# Setup checklist

Go through these steps in order. Steps 1 and 2 don't need a computer. The full reasoning and sources are in [research-report.md](research-report.md).

## Step 0: Turn on ADB (needed for the tool, not for steps 1–2)

- [ ] On your computer, install **Python 3** and Google's **Android SDK Platform-Tools**, and add the `platform-tools` folder to your PATH.
- [ ] On the TV, open **Settings > System > About** and click **Android TV OS build** about 7 times, until it says you're a developer.
- [ ] Open **Settings > System > Developer options** and turn on **USB debugging**. On the U8N this also opened network ADB on port 5555.
- [ ] Find the TV's IP address under **Settings > Network & Internet**.
- [ ] `python3 tvdebloat.py connect <TV-IP>`. On the TV, accept **Allow USB debugging?** and tick **Always allow**.
- [ ] `python3 tvdebloat.py info`. Check that it shows the right model, and note the Android version and memory.
- [ ] `python3 tvdebloat.py baseline`. Keep the `logs/baseline-*` folder it creates.

## Step 1: Settings (no risk)

- [ ] **Hisense viewing tracking (ACR):** in **Settings > Privacy** (or **Settings > System > Privacy**), turn off whichever of these your firmware shows: **Enhanced Viewing**, **Viewing Information Services** or **Smart TV Experience**.
- [ ] In the same menu, turn off **usage & diagnostics** and **personalised ads**, and reset or delete the **advertising ID**.
- [ ] **Animations:** set **Window / Transition / Animator duration scale** to **0.5x** in Developer options, or run `python3 tvdebloat.py tweaks apply`.
- [ ] Leave **Background process limit** at Standard, and don't turn on **Don't keep activities**.
- [ ] Uninstall apps you never use, and optionally clear all caches with `python3 tvdebloat.py tweaks apply --trim-cache`.
- [ ] *Optional, if you're not using Projectivy:* turn on **Settings > Accounts & Sign In > your profile > Apps only mode**. This also turns off Search and Assistant on the home screen, and you have to turn it off again to install apps.

## Step 2: Projectivy Launcher (very low risk)

- [ ] Install **Projectivy Launcher** from the Play Store.
- [ ] Turn on **Settings > Accessibility > Projectivy Launcher**.
- [ ] In **Projectivy Settings > General > Change default launcher**, choose **Override current launcher**.
- [ ] Press Home to check that Projectivy opens. Optionally add HDMI input tiles. If a tile hangs, use the remote's Input button instead.
- [ ] To go back to the stock home, turn the override off.

## Step 3: Hisense ads and tracking apps (ADB batch 1)

- [ ] `python3 tvdebloat.py check batch1` lists which packages exist on your TV. If you don't want something removed (for example HiAlexa), comment out its line in `packages/batch1-hisense.txt`.
- [ ] `python3 tvdebloat.py apply batch1 --reboot`
- [ ] **Test** the remote, Input button, every HDMI port, picture modes, sound, CEC, AirPlay/Cast and one streaming app. If anything breaks, run `python3 tvdebloat.py restore --all --reboot`.

## Step 4: Google leftovers (ADB batch 2)

- [ ] If you watch movies you bought on Google TV, remove `com.google.android.videos` from `packages/batch2-google.txt`.
- [ ] `python3 tvdebloat.py check batch2`, then `python3 tvdebloat.py apply batch2 --reboot`, then test.

## Step 5: Optional, one at a time (ADB batch 3)

Each item costs a feature. Read the comments in `packages/batch3-optional.txt` first.

- [ ] `python3 tvdebloat.py apply batch3 --only <package> --reboot`, then test before doing the next one.
- [ ] Disabling `com.google.android.katniss` stops the **mic button and voice search** from working.
- [ ] To remove a sponsored app you never use, find its name with `python3 tvdebloat.py check` or `adb shell pm list packages`, then run `python3 tvdebloat.py apply --package <name>`.

## Step 6: Stock Google TV home (ADB batch 4, highest ADB risk, optional)

Only do this if Step 2 already works. The tool refuses unless Projectivy is installed, and it always disables the stock launcher and its setup fallback together.

- [ ] `python3 tvdebloat.py apply batch4 --reboot`
- [ ] Expect these side effects, based on the U8N: the gear key and the YouTube/Disney+/Prime buttons stop working, and the quick-settings panel disappears. Remap the keys with **Button Mapper** (keycodes: gear 83, Inputs 178, Menu 702).
- [ ] If YouTube sign-in or input switching breaks, run `python3 tvdebloat.py restore com.google.android.apps.tv.launcherx com.google.android.tungsten.setupwraith --reboot`.

## When you're finished

- [ ] **Turn off USB debugging.** While it's on, anyone on your home network can connect to the TV on port 5555.

## After every TV update or power cut

- [ ] Turn USB debugging back on, run `python3 tvdebloat.py status`, and run `python3 tvdebloat.py rearm` if anything came back.
- [ ] Check that the privacy toggles from Step 1 are still off.
- [ ] Press Home to check that the Projectivy override still works. If it doesn't, turn the override and its Accessibility permission off and on again.
- [ ] Turn USB debugging off again.

## If something goes wrong

| Problem | What to do |
|---|---|
| A feature stopped working | `python3 tvdebloat.py restore <package> --reboot`, or `restore --all --reboot` |
| No computer handy | **Settings > Apps > See all apps > Show system apps**, open the app, then **Enable** |
| Boots to **Android Recovery** ("Can't load Android system") | Choose **Try again**, **not** "Factory data reset". Then run `restore --all`. |
| Black screen after Step 6 | Reconnect with ADB and restore the two batch 4 packages |
| Nothing else works | Factory reset, which re-enables all apps. As a last resort, reinstall stock firmware from Hisense support (`upgrade_loader.pkg` on a FAT32 USB stick, power button held at start-up). Never interrupt a firmware update. |
