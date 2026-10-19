# Debloat your Hisense instead of reflashing it

**You can't rebuild the Hisense 100U70N with a lean Google TV or Android TV OS. No custom ROM, AOSP build or GSI exists for any Hisense TV or for its MediaTek Pentonic 700 chip. Hisense's USB firmware is encrypted with keys that aren't public. Root has only been done by hand on a few other Hisense boards, using a serial (UART) cable and a boot-image dump.** The realistic way to make the TV lean and fast is software-only and reversible. In order: switch off Hisense's content-recognition tracking (ACR) and Google's ad personalisation in Settings; make Projectivy Launcher your home screen with its built-in override, which needs no root; then use ADB to disable Hisense's ad, ACR and helper apps plus a few Google leftovers, about ten at a time with a reboot after each group. The best evidence comes from one owner of a 2024 Hisense 55U8N, which uses the same chip family and Google TV generation. That owner froze 23 packages, swapped the launcher, and kept Game Mode, VRR, Dolby, HDMI-CEC and AirPlay working ([U8N debloat repo](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat)). Expect modest gains: idle free memory rose by about 80 MB on that TV, and there are no measured boot-time or UI-latency improvements. Mostly you get a cleaner, ad-free home screen and less tracking, not a dramatically faster TV. If raw smoothness and fast updates matter most, an external streamer with the TV used as a display is the simplest fix. Even then, switch off the TV's ACR, because it fingerprints HDMI content too. **Every package name in this report comes from other Hisense units. Check each one on your own TV with `adb shell pm list packages` before you disable anything.**

| Option | Possible on 100U70N? | Risk | Verdict |
|---|---|---|---|
| Custom ROM / "lean OS" reflash | No: none exists, firmware encrypted | n/a | Not available |
| Bootloader unlock + root | Plausible in principle, unproven on this board | High (boot loops, needs UART cable to recover) | Experts only, not recommended |
| Settings changes (privacy, animations) | Yes | None | Do it |
| Projectivy launcher with override | Yes | Very low, instantly reversible | Do it |
| ADB debloat in batches | Yes | Low if you follow the never-touch list | Do it, carefully |
| External streamer | Yes | None | Best if speed matters most |

## Your "100U7ON" is a 100U70N built on the Pentonic 700 chip

"100U7ON" is almost certainly the **Hisense 100U70N**, with a zero rather than the letter O. It's the 100" Class U70 Series QLED 4K Google TV that Best Buy, Amazon, Walmart and Costco sold ([Best Buy](https://www.bestbuy.com/product/hisense-100-class-u70-series-qled-4k-uhd-smart-google-tv-2025/J3Z9Z4235R); [Walmart](https://www.walmart.com/ip/Hisense-100U70N-100-inch-Class-U70-Series-4K-QLED-Smart-Google-TV/16951109660)). A spec database states that the **100U76N "is also known as" the 100U70N** and lists a **MediaTek Pentonic 700 (MT9618)** with four Cortex-A73 cores at 1.4 GHz and a Mali-G52 GPU ([DisplaySpecifications](https://www.displayspecifications.com/en/model/f26b37ba)). The 100U76N's replacement main board is sold as **RSAG7.820.13512** ([ShopJimmy](https://www.shopjimmy.com/hisense-357649-401854-rsag7-820-13512-roh-main-board-100u76n/)). That's the same chip family as the 2024 U8N, which has the only Hisense Google TV debloat guide and root guide, but a **different main board** ([XDA U8N root guide](https://xdaforums.com/t/root-guide-android-tv-how-to-root-mt9618-hisense-tvs-using-mainboard-part-rsag7-820-13493-65u8n-55u8n-etc.4744258/)).

Hisense doesn't publish RAM or OS details for this set. Sibling 2024 models have about **2.5 GB of RAM and 32 GB of storage** (owner reports for the U8K/U8N; [AVS Forum](https://www.avsforum.com/threads/2025-hisense-u8q-owners-thread.3323493/); [9to5Google U7N review](https://9to5google.com/2024/09/28/hisense-u7n-google-tv-review/)), and the U8N's MT9618 build ID points to **Android TV 12**. Treat both as likely but unconfirmed for your TV. The U8N owner saw 2.4 GB total RAM with only about 600 MB available at idle ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)). That makes RAM the likely bottleneck, and it's why removing background apps and the ad-heavy home screen helps at all. You can confirm your build under **Settings > System > About**, or with the commands in Step 0.

## No lean ROM exists, and root is an expert-only gamble

**Custom ROMs.** No LineageOS, AOSP or GSI build exists for any Hisense TV or Pentonic/MT96xx chip. Community Android TV ROMs target the Raspberry Pi and Nvidia Shield ([XDA thread](https://xdaforums.com/t/its-possible-to-mod-a-tv-with-built-in-android-tv-and-install-a-custom-rom-instead-for-privacy-reasons.4719701/); [Hacker News](https://news.ycombinator.com/item?id=42428303)). The reason is structural. The picture pipeline, local dimming, HDMI inputs, tuner and panel control all run on proprietary MediaTek vendor code, and MediaTek releases little documentation. XDA posters conclude that without source code nobody can build new firmware, so they recommend root plus debloat plus a custom launcher. Even a generic image that booted would very likely lose core TV functions and Google certification. That last point is our inference; nobody has reported trying.

**Reflashing modified firmware.** Hisense's USB firmware is a MediaTek PKG file (`upgrade_loader.pkg`), installed by holding the remote's power button while the TV starts with the file on a FAT32 stick ([Hisense ES](https://www.hisense.es/descargas-firmware/u7a/)). Newer PKGs are **encrypted, and Hisense's keys aren't public**. The main extraction tool supports new-format PKGs only "depending on keys" and ships keys for Sony and Philips, not Hisense ([unixtract README](https://drm-free.duckdns.org/thegame_1980/unixtract/raw/commit/30fafbd3fc9127cd40e8da487bafe755dd719085/README.md); [XDA U8G](https://xdaforums.com/t/q-hisense-u8g-root-mt5895.4465983/)). Nobody has reported flashing a modified PKG. Flashing a **stock** PKG is still useful as a recovery tool (see Restore). In the US, Hisense support supplies firmware by serial number ([Elektroda](https://www.elektroda.com/qa,nt72690-tv-firmware-usb-recovery.html)).

**Bootloader unlock and root: status, requirements and risk.** On several earlier Hisense Google/Android TVs (U8G, U6H and the 65/55U8N), forum users report unlocking the bootloader through the standard Android fastboot interface, with no OEM-unlock toggle needed ([XDA U8G](https://xdaforums.com/t/hisense-u8g-bootloader-unlock-and-probably-others.4465683/)). Root then meant flashing a Magisk-patched boot image. That image first had to be dumped from the TV, usually through a **UART service-port or UART-over-HDMI cable into the U-Boot shell**. Generic phone exploits don't apply: "mtk-su doesn't work", and the BROM tool mtkclient covers phones, not TV chips ([XDA U8G root](https://xdaforums.com/t/q-hisense-u8g-root-mt5895.4465983/); [mtkclient](https://mtkclient.org/)). Magisk itself needed a code fix in September 2024 for Hisense's modified bootloader ([Magisk #8063](https://github.com/topjohnwu/Magisk/issues/8063)). The U8N guide's pre-patched image only fits board RSAG7.820.13493 on build STT2.230310.002, so **a 100U70N owner would have to make their own boot dump for board RSAG7.820.13512**. Its UART pinout is undocumented, and no 100" unlock or root has been reported.

The risks are documented. On the U8G, users reported boot loops and TVs stuck at the unlocked-bootloader warning ([XDA U8G](https://xdaforums.com/t/hisense-u8g-bootloader-unlock-and-probably-others.4465683/)). The U6H author needed USB recovery after both flash attempts ([XDA U6H](https://xdaforums.com/t/root-hisense-u6h-via-modified-magisk.4635687/)). The U8N author warns that **without the UART cable you can't recover from a brick**, because fastboot and recovery are unreachable once the TV fails to boot. The worst case short of panel damage is a replacement main board, about **$218** for the 100U76N ([Newegg](https://www.newegg.com/p/11J-03WU-00077)). The unlock warning shows at every boot, so expect warranty claims for software or board faults to be refused. Rooted Android devices commonly lose streaming-DRM certification, though nobody has tested that on Hisense.

On the legal side, US DMCA §1201 exemptions have covered jailbreaking smart TVs since the 2018 cycle ([EFF](https://www.eff.org/node/96933)). Distributing circumvention tools is still illegal. Even after all that, root doesn't give you a lean OS. Its main gain is finer-grained disabling, because on Android 12 the ADB shell can't disable individual app components ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)). For a non-specialist, the trade isn't worth it.

## The plan, ordered from zero risk to expert-only

Each step stands on its own, so stop wherever you're satisfied. Steps 1 and 2 need no computer. Steps 3 to 6 use ADB from a laptop on the same network as the TV. Each ADB change is one command to undo.

### Step 0: Turn on ADB and record a baseline

Install Google's "Android SDK Platform-Tools" on your computer. On the TV, open **Settings > System > About** and click **"Android TV OS build"** repeatedly until Developer options unlock ([9to5Google](https://9to5google.com/?p=442008)). Then turn on **USB debugging** in Developer options. On the U8N, turning on USB debugging also opened network ADB on port 5555 ([U8N README](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat)). Find the TV's IP address under Settings > Network & Internet, connect, and accept the "Allow debugging" prompt on the TV.

```
adb connect 192.168.1.50:5555
adb devices
adb shell getprop ro.product.model
adb shell getprop ro.build.version.release
adb shell getprop ro.build.display.id
```

Replace the IP with your TV's own. Then save a baseline. These files are your record for any rollback, so keep them ([DEBLOAT-LOG](https://github.com/Pradeeppilotdev/tv-debloat/blob/main/DEBLOAT-LOG.md)).

```
adb shell pm list packages > all-packages.txt
adb shell pm list packages -s > system-packages.txt
adb shell pm list packages -d > disabled-before.txt
adb shell pm list packages -f > package-paths.txt
adb shell dumpsys meminfo > meminfo-before.txt
```

**Before every batch, confirm the packages exist on your TV.** These searches run on the TV itself, so they work from Windows, macOS or Linux:

```
adb shell "pm list packages | grep -i vt"
adb shell "pm list packages | grep -i hisense"
adb shell "pm list packages | grep -i vidaa"
adb shell "pm list packages | grep -i google"
```

If a package in this report isn't on your list, skip it. The `disable-user` command fails harmlessly on a missing name. If you see `com.hisense.*` names instead of `com.vt.*`, your firmware is closer to the older Hisense Android TV layout, and you should use the never-touch list with extra care.

### Step 1: Change settings, with no tools and no risk

**Hisense ACR.** Hisense runs its own content-recognition service, separate from Google. Turn it off in the privacy menu. Its label varies by firmware: the U8N owner found **"Enhanced Viewing" under Settings > Privacy** ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)). Consumer Reports describes **Settings > System > Privacy > "Viewing Information Services"**, called "Smart TV Experience" on some models ([Consumer Reports via Yahoo](https://news.yahoo.com/turn-off-smart-tv-snooping-060657238.html?fr=sycsrp_catchall)). In the same menu, turn off device usage/diagnostics data and personalised ads, and delete or reset the advertising ID ([PCWelt](https://www.pcwelt.de/?p=3124436); [Smart Home Perfected](https://www.smarthomeperfected.com/how-to-disable-acr-smart-tv/)). Google's own data collection can't be fully opted out of if you keep smart features ([Consumer Reports](https://www.consumerreports.org/electronics-computers/tvs/how-to-turn-off-smart-tv-snooping-features-a4840102036/)). One Hisense owner reported the ACR setting turning itself back on ([Tom's Guide forum](https://forums.tomsguide.com/threads/turn-off-the-acr-on-a-hisense-tv.584074/post-2094699)), which is why Step 3 also disables the ACR app.

**Animations.** In Developer options, set the window, transition and animator duration scales to **0.5x**. 9to5Google called this the most immediate improvement in snappiness ([9to5Google](https://9to5google.com/?p=442008)). The ADB equivalent is:

```
adb shell settings put global window_animation_scale 0.5
adb shell settings put global transition_animation_scale 0.5
adb shell settings put global animator_duration_scale 0.5
```

Leave "Background process limit" at Standard unless you still see stutter, and don't go below 3. A strict limit forces streaming apps to cold-start every time you return to them. Also avoid "Don't keep activities". Keep storage free by removing apps you don't use, because full storage is a known cause of slowdowns ([9to5Google](https://9to5google.com/?p=442008)). You can clear all app caches at once (apps rebuild them):

```
adb shell pm trim-caches 32G
```

**Apps only mode (optional).** **Settings > Accounts & Sign In > your profile > Apps only mode** hides personalised recommendations, Continue Watching and the Library. It also turns off Search and Google Assistant on the home screen. The sponsored "Highlights" carousel stays, and you have to turn the mode off to install apps ([TCL Support](https://support.tcl.com/en_US/google-tv-apps-only-mode); [How-To Geek](https://www.howtogeek.com/695447/how-to-disable-recommendations-on-google-tv/)). Use it if you want an ad-light home screen without a new launcher. Skip it if you plan to use Projectivy.

### Step 2: Make Projectivy your home screen, with no ADB

Install **Projectivy Launcher** from the Play Store; its package is `com.spocky.projengmenu`. Then turn it on in two places. First, **Settings > Accessibility > Projectivy Launcher > On**. Second, in **Projectivy Settings > General > Change default launcher**, choose **"Override current launcher"** ([Android Police](https://www.androidpolice.com/remove-google-tv-ads/)). The override catches Home button presses through an Accessibility service. Google TV stays installed, and turning the override off brings the stock home back at once ([Make Tech Easier](https://maketecheasier.com/use-projectivy-launcher-android-tv/)). XDA found Projectivy "much smoother than Google's launcher" on a Chromecast with Google TV ([XDA Developers](https://www.xda-developers.com/google-tv-bloated-replaced-custom-launcher-actually-works/)). Projectivy can also add HDMI input tiles and open a chosen app or input when the TV powers on.

There are known issues. The Back button can still land on the stock home ([Notebookcheck](https://www.notebookcheck.net/The-Google-TV-launcher-is-mess-of-adverts-but-this-replacement-is-a-clean-beautiful-ad-free-alternative.1018849.0.html)). A Hisense owner reported that a Projectivy HDMI tile worked once, then hung for about 30 seconds on reopening, so use the remote's Input button as a fallback ([XDA Projectivy thread](https://xdaforums.com/t/app-android-tv-projectivy-launcher.4436549/page-36)). A 2026 Google TV update broke the override for some users ([Android Authority](https://www.androidauthority.com/google-tv-update-blocks-projectivy-override-3649445/)), and re-toggling the override and the Accessibility permission reportedly fixed it ([Simturax](https://simturax.com/replace-stock-launcher-google-tv/)). **After every TV update, check that the override still works.**

### Step 3: Disable Hisense ads, ACR and clutter (ADB batch 1)

Every command below uses `pm disable-user --user 0`. It freezes an app without deleting it, and one `pm enable` reverses it. That's the U8N owner's method for all system apps, applied in batches of about ten with a reboot and a function test between batches ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)). An older Hisense set lost changes when it was rebooted straight away, so **wait about 15 seconds before rebooting** ([cleanyourtv FFM list](https://github.com/Gathin23/cleanyourtv/blob/main/examples/hisense-smarttv-4k-ffm/debloat.txt)). Turn off the ACR toggle in Step 1 first.

```
adb shell pm disable-user --user 0 com.vt.tv.evservice
adb shell pm disable-user --user 0 net.vidaatv.hisense.android.tv
adb shell pm disable-user --user 0 com.vidaa.oemtabcontentprovider
adb shell pm disable-user --user 0 com.vt.hishow
adb shell pm disable-user --user 0 com.vt.tv.protector
adb shell pm disable-user --user 0 com.vt.storemode
adb shell pm disable-user --user 0 com.vt.tv.ai_sense
adb shell pm disable-user --user 0 com.vt.alexa
adb shell pm disable-user --user 0 com.hisense.odinbrowser
adb reboot
```

That freezes ACR (the U8N file is `Vtp_ACR.apk`), Hisense Channels (ad-supported streaming channels), the "Hisense" tab feed in the Google TV home, Family Moment, Device Assistant, the store demo mode, camera functions, HiAlexa (skip it if you use Alexa) and Hi Browser. After rebooting, test the remote, the Input button, every HDMI port, picture modes, sound, CEC, AirPlay/Cast and a streaming app.

### Step 4: Disable Google leftovers (ADB batch 2)

```
adb shell pm disable-user --user 0 android.autoinstalls.config.google.gtvpai
adb shell pm disable-user --user 0 com.google.android.play.games
adb shell pm disable-user --user 0 com.google.android.feedback
adb shell pm disable-user --user 0 com.google.android.syncadapters.calendar
adb shell pm disable-user --user 0 com.google.android.videos
adb reboot
```

These are the Play auto-install stub (the U8N author says it pushes sponsored apps back onto the TV), Play Games, the feedback agent, Calendar sync, and the Google TV/Play Movies app. The U8N owner removed the last one without breakage ([batch-a](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/debloat/batch-a.txt); [batch-c](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/debloat/batch-c.txt)). Leave `com.google.android.videos` enabled if you watch movies you bought through Google TV.

### Step 5: Optional removals that cost features (ADB batch 3, one at a time)

Each of these trades a feature or carries a conflicting safety rating, so **disable them one at a time and reboot between each**:

```
adb shell pm disable-user --user 0 com.google.android.katniss
adb shell pm disable-user --user 0 com.google.android.apps.tv.dreamx
adb shell pm disable-user --user 0 com.google.android.youtube.tvmusic
adb shell pm disable-user --user 0 com.android.printspooler
adb shell pm disable-user --user 0 com.google.android.tvrecommendations
adb shell pm disable-user --user 0 com.google.android.onetimeinitializer
adb shell pm disable-user --user 0 com.google.android.partnersetup
```

Disabling `katniss` (the Google app/Assistant) frees memory but **kills the mic button and voice search**. The U8N author also found that Hisense's Smartsense service turns Assistant back on at boot and periodically ([U8N README](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat)). `dreamx` is the Ambient Mode screensaver, which shows Google promos in some regions. `printspooler` worked fine on the U8N, but UAD-ng warns it can break a connection-preferences menu in Settings ([UAD-ng](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/main/resources/assets/uad_lists.json)). `tvrecommendations` was disabled without problems on an older Hisense, but UAD-ng rates it "Expert" ([cleanyourtv FFM](https://github.com/Gathin23/cleanyourtv/blob/main/examples/hisense-smarttv-4k-ffm/debloat.txt)). `onetimeinitializer` and `partnersetup` come from generic lists and haven't been tested on Hisense ([TechPP](https://techpp.app/howto/debloat-android-tv-adb)). Sponsored streaming apps you never use, such as Paramount+, Prime Video or Spotify, can be disabled the same way once you've found their exact names on your TV. The Latin American apps in the U8N list won't exist on US firmware.

### Step 6: Disable the stock Google TV home (ADB batch 4, highest ADB risk)

Do this only if Projectivy's override (Step 2) already works and you want the swap to stick. **Never disable the stock home before a replacement is set up.** Doing it in the wrong order can leave a black screen, or send the Home button to a factory test app ([freya.cat](https://freya.cat/blog/post/2025-03-11); [Notebookcheck](https://www.notebookcheck.net/The-Google-TV-launcher-is-mess-of-adverts-but-this-replacement-is-a-clean-beautiful-ad-free-alternative.1018849.0.html)). Both packages must go together, because on Hisense the setup wizard (`setupwraith`) acts as a fallback home and re-enables the launcher ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)):

```
adb shell pm disable-user --user 0 com.google.android.apps.tv.launcherx
adb shell pm disable-user --user 0 com.google.android.tungsten.setupwraith
adb reboot
```

On the U8N this broke several things. The gear key and the YouTube, Disney+ and Prime remote buttons stopped working, while the Netflix button kept working. The quick-settings panel disappeared. The Inputs screen kept a "Google TV Home" tile. The author restored the keys with the Button Mapper app (keycodes: gear 83, Inputs 178, Menu 702). On a MediaTek-based Philips set, input switching failed until MediaTek's TV app was restored ([freya.cat](https://freya.cat/blog/post/2025-03-11)). On other Google TV devices, YouTube sign-in failed until the launcher was re-enabled ([gist](https://gist.github.com/SMUsamaShah/25a1c4958fcdfe87db49da18f66dbf7a)). The two packages **came back enabled after at least one full reboot** on the U8N, so check `adb shell pm list packages -d` after power cuts and updates. The author's [re-arm script](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/ps5-button/rearm-after-reboot.sh) automates re-disabling them. The gains from this step over Step 2 are small, and it's the step most likely to annoy you.

When you're finished, turn USB debugging off. Network ADB on port 5555 accepts connections from anyone on your home network ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)).

### Step 7: Root, for experts only

Root stays at the status described above. It needs a self-made UART cable, a boot dump from this specific board, and acceptance of a possible $218 board replacement. Nothing in Steps 1 to 6 needs it.

## Which packages to disable, which are optional, which never to touch

"Confidence for 100U70N" reflects how close the evidence is to your TV. **Medium-high** means confirmed safe on the 2024 Hisense U8N (same chip family and Google TV generation) and also on generic Google TV lists. **Medium** means confirmed only on the U8N. **Low** means the evidence comes from other brands or older Hisense sets, or the ratings conflict. Nothing has been tested on a 100U70N itself. Sources: [U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md), [U8N labels](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/baseline/labels.txt), [UAD-ng](https://github.com/Universal-Debloater-Alliance/universal-android-debloater-next-generation/blob/main/resources/assets/uad_lists.json), [cleanyourtv FFM](https://github.com/Gathin23/cleanyourtv/blob/main/examples/hisense-smarttv-4k-ffm/debloat.txt), [TechPP](https://techpp.app/howto/debloat-android-tv-adb).

| Package | What it is | Action | Confidence for 100U70N |
|---|---|---|---|
| `com.vt.tv.evservice` | Hisense ACR (content recognition) | Disable | Medium |
| `net.vidaatv.hisense.android.tv` | Hisense Channels (ad-supported channels) | Disable | Medium |
| `com.vidaa.oemtabcontentprovider` | "Hisense" tab in the Google TV home | Disable | Medium |
| `com.vt.hishow` | Family Moment | Disable | Medium |
| `com.vt.tv.protector` | Device Assistant cleaner | Disable | Medium |
| `com.vt.storemode` | Retail store demo | Disable | Medium |
| `com.vt.tv.ai_sense` | USB-camera features | Disable | Medium (may be absent) |
| `com.vt.alexa` | HiAlexa | Disable if you don't use Alexa | Medium |
| `com.hisense.odinbrowser` | Hi Browser | Disable | Medium |
| `android.autoinstalls.config.google.gtvpai` | Play auto-install of sponsored apps | Disable | Medium |
| `com.google.android.play.games` | Play Games | Disable | Medium-high |
| `com.google.android.feedback` | Feedback agent | Disable | Medium-high |
| `com.google.android.syncadapters.calendar` | Calendar sync | Disable | Medium-high |
| `com.google.android.videos` | Google TV / Play Movies app | Disable (keep if you use purchases) | Medium-high |
| `com.google.android.katniss` | Google app / Assistant | Optional: loses mic and voice search | Medium |
| `com.google.android.apps.tv.dreamx` | Ambient Mode screensaver | Optional | Medium-high |
| `com.google.android.youtube.tvmusic` | YouTube Music | Optional | Medium-high |
| `com.android.printspooler` | Print spooler | Optional (conflicting ratings) | Low-medium |
| `com.google.android.tvrecommendations` | Recommendation service | Optional, test alone | Low |
| `com.google.android.onetimeinitializer`, `com.google.android.partnersetup` | Setup leftovers | Optional, test alone | Low |
| `com.google.android.apps.tv.launcherx` + `com.google.android.tungsten.setupwraith` | Stock home + setup fallback | Optional, both together, only after Projectivy works | Medium |
| `com.vt.tv.ota`, `com.vt.remoteupgrade` | Firmware updates | Keep (blocks security and HDMI/gaming fixes) | Medium |
| `com.vt.tv.smartsense`, `com.vt.tv.smartsense.ui`, `com.vt.tv.aiot*` | Remote keys, wake, input events | **Never touch** (related packages sent an older Hisense into Android Recovery) | High |
| `com.vt.tvservice`, `com.vt.tvplayer`, `com.vt.avmiddleware`, `com.vt.tv.aipq`, `com.vt.tv.videocolor`, `com.vt.tv.calmanconnector`, `com.vt.roomcalibration`, `com.vt.edv.drmp`, `com.dolby.android.audio.service` | Picture, audio and DRM pipeline | **Never touch** | High |
| `com.vt.tv.input`, `com.vt.source.external`, `com.vt.source.tuner`, `com.vt.tv.tvcenter`, `com.android.providers.tv`, all `com.mediatek.*` | Inputs, HDMI, CEC, tuner, Live TV | **Never touch** | High |
| `com.google.android.tv.remote.service`, `com.mediatek.autopair`, `com.android.bluetooth` | Remote pairing | **Never touch** (UAD-ng disagrees, but three sources say keep) | High |
| `com.mediatek.AirplayAPK`, `com.mediatek.airplaydaemon`, `com.google.android.apps.mediashell` | AirPlay and Cast | **Never touch** | High |
| `com.google.android.gms`, `com.google.android.gsf`, `com.android.vending`, `com.google.android.inputmethod.latin`, `com.android.tv.settings`, `com.android.systemui`, `com.android.location.fused`, any `overlay`/`rro` package | Android and Google core (fused location can cause a boot loop) | **Never touch** | High |
| `com.vt.eula`, `com.vt.fte`, `com.vt.factory`, `com.vt.tv.commonui`, `com.vt.tv.customerlauncher`, `com.vt.tv.usbota`, `com.vt.tv.b2b`, `com.vt.tv.smartservice`, `com.vt.tv.dlna`, `com.vt.tv.mediacenter` | Hisense system, unidentified roles | **Never touch** | High |

The U8N author's rule is worth adopting: **if a package is Hisense or MediaTek and you can't positively identify it, leave it alone.**

## Every change rolls back with one command

The commands depend on how a package was removed. For anything frozen with `disable-user`, which is everything in this plan, re-enable it like this:

```
adb shell pm enable --user 0 com.vt.tv.evservice
```

To roll back a whole batch, run the same list again with `pm enable --user 0` in place of `pm disable-user --user 0`. To see everything currently disabled, and compare it against `disabled-before.txt`, run `adb shell pm list packages -d`. Some packages, such as MediaTek's "TIF Test" app, ship disabled from the factory, so don't re-enable everything blindly ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)).

If you uninstalled a package for user 0 instead of disabling it, restore it with `pm install-existing` or reinstall it from the Play Store ([restore.sh](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/debloat/restore.sh)):

```
adb shell pm install-existing --user 0 <package.name>
```

To bring back the stock Google TV home:

```
adb shell pm enable --user 0 com.google.android.apps.tv.launcherx
adb shell pm enable --user 0 com.google.android.tungsten.setupwraith
```

To undo the animation changes, set them back to 1:

```
adb shell settings put global window_animation_scale 1
adb shell settings put global transition_animation_scale 1
adb shell settings put global animator_duration_scale 1
```

If you have no computer to hand, the Settings > Apps page can re-enable disabled apps ([cleanyourtv README](https://github.com/Gathin23/cleanyourtv)).

If the TV boots to an Android Recovery screen saying "Can't load Android system", **choose "Try again", not "Factory data reset"**. On the older Hisense that hit this screen, "Try again" booted normally, and the restore script then undid the changes ([cleanyourtv FFM](https://github.com/Gathin23/cleanyourtv/blob/main/examples/hisense-smarttv-4k-ffm/debloat.txt)). A factory reset is the last software resort and re-enables every app ([TechPP](https://techpp.app/howto/debloat-android-tv-adb)). Below that sits a stock USB reinstall: a `upgrade_loader.pkg` from Hisense support matched to the model on your rear sticker, installed with the power button held at start-up ([Hisense ES](https://www.hisense.es/descargas-firmware/u7a/)). Don't interrupt a firmware update, because that can leave the TV stuck at the boot logo ([SlashGear](https://www.slashgear.com/1803516/hisense-tvs-common-problems-fixes/)). Also keep `com.vt.tv.ota` and `com.vt.remoteupgrade` enabled; on an older Hisense, disabling the equivalent packages blocked updates until they were re-enabled. After any Hisense update, re-run `pm list packages -d`, recheck the privacy toggles, and confirm the Projectivy override.

## Gains are modest: about 80 MB of RAM and a cleaner home screen

The only Hisense Google TV measurement comes from the U8N. After freezing 23 packages and replacing the launcher, idle free RAM rose from **about 135 MB to about 215 MB**. Before the debloat, the biggest background users were Play services, Smartsense, the Google app/Assistant, Netflix and the Google TV launcher ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)). Play services and Smartsense can't be removed safely, which caps how lean the TV can get. A 1 GB Xiaomi TV freed 130 MB of used RAM and cut swap by 82% ([DEBLOAT-LOG](https://github.com/Pradeeppilotdev/tv-debloat/blob/main/DEBLOAT-LOG.md)). Nobody has published boot-time, input-lag or app-launch measurements for any Hisense TV before and after debloating. The improvements people describe are impressions: snappier menus with 0.5x animations, and a home screen that loads without ad rows ([Android Police](https://www.androidpolice.com/remove-google-tv-ads/)). The baseline is already decent. 9to5Google rated the U7N's Google TV performance "excellent", with occasional stutter when waking and in poorly optimised apps ([9to5Google](https://9to5google.com/2024/09/28/hisense-u7n-google-tv-review/)).

### An external streamer buys smoothness and updates, not privacy

The same 9to5Google review put the U7N below an Nvidia Shield and suggested a Shield, Apple TV or Google TV Streamer for the best experience. The Google TV Streamer has **4 GB of RAM**, against this TV's likely 2.5 GB. One low-confidence review measured a 2.3-second average cold app launch versus over 4 seconds on built-in TCL/Hisense Google TV ([The Tested Hub](https://thetestedhub.com/reviews/google-tv-streamer-4k/)). Professional reviewers still saw the Streamer freeze or stutter in menus ([What Hi-Fi](https://www.whathifi.com/advice/google-tv-streamer-vs-chromecast-with-google-tv-should-you-upgrade); [Android Police](https://www.androidpolice.com/google-tv-streamer-review/)), so it isn't a guaranteed cure. A streamer's clearer advantage is software. Hisense is slow with major Android updates ([9to5Google](https://9to5google.com/2024/09/28/hisense-u7n-google-tv-review/)), while a streamer gets newer builds and app support on its own schedule.

The catch is that Hisense's ACR **fingerprints whatever is on screen, including HDMI sources like a PS5** ([U8N NOTES](https://github.com/JesusRojass/hisense-u8n-google-tv-debloat/blob/main/NOTES.md)). A streamer doesn't remove the TV's tracking, so Steps 1 and 3 still matter. The cleanest setup is to do Step 1, disable `com.vt.tv.evservice`, set the TV to start on the last-used input ([FlatpanelsHD](https://www.flatpanelshd.com/guide.php?subaction=showfull&id=1730969892)), and let the streamer handle apps. That leaves the TV's own Google TV mostly idle.

| | Debloated built-in Google TV | External streamer (e.g. Google TV Streamer, Shield, Apple TV) |
|---|---|---|
| Speed | Modestly better; RAM-limited (~2.5 GB, unconfirmed) | Usually smoother (4 GB on Google TV Streamer); not flawless |
| Updates | Slow, at Hisense's pace | Faster, on the streamer's own schedule |
| Privacy | ACR removed if you do Steps 1 and 3 | Still need Steps 1 and 3 on the TV |
| Effort and risk | An evening with ADB; low risk if careful | Plug in; no risk |
| Cost | Free | Price of the device |

## What we couldn't verify

No source confirms the 100U70N's RAM, storage, Android version, security patch level or exact main board. The 100U76N link and the MT9618 chip come from a single spec database. No debloat, launcher swap or root has been reported on any 100" Hisense, or on any U7N or U70 model. Every package rating here is borrowed from one 55U8N owner, on Latin American firmware, whose repository appeared on 2026-10-14, plus older Hisense and other-brand lists. That source also contradicts itself on how often the stock launcher re-enables after reboots, and on whether `com.vt.tv.usbota` is safe. US-firmware sponsored app package names on Hisense are undocumented. Nobody has documented whether a Hisense update re-enables specific packages, or whether Projectivy's override survives current Google TV builds on Hisense. We found no Hisense setting for "quick start" or standby, and no measured latency data. Whether a 2025 or 2026 Hisense update still allows bootloader unlock, and whether root breaks streaming DRM on Hisense, are both unknown.

## Conclusion

The idea of a "lean OS" for this TV doesn't hold up, and not because Hisense locks things down especially hard: the bootloader on sibling models opens with standard tools. The real obstacle is that everything that makes the panel a television (local dimming, HDMI, CEC, picture processing) lives in closed MediaTek and Hisense services that no replacement OS can carry. So the useful work is subtraction, not replacement. Of the things you can subtract, the ones that change your daily experience most are about **attention and privacy**: the ad-filled home screen and the ACR fingerprinting of everything you watch. Raw speed changes much less.

That changes what "lean and fast" should mean here. Treat the TV as a display with a clean launcher and no tracking, and accept that its 2024-era memory sets a ceiling. If that ceiling still bothers you after Steps 1 to 4, buying a streamer is a better use of effort than going further down the ADB list or anywhere near root. The Hisense-specific debloat evidence is days old and comes from a single owner, so check each name, change things in small batches, and keep the baseline files that make every step reversible.
