[README.md](https://github.com/user-attachments/files/34083899/README.md)
# Hoops for Hope Broadcast Graphics

Local, browser-based broadcast graphics package built for **Hoops for Hope 2026** and OBS on macOS.

> **Future-me note:** this README is intentionally operational. The goal is to make next year's setup take minutes instead of reconstructing all the weird OBS/DSK/CORS decisions from memory.

## Current 2026 baseline

The last working 2026 package in this repo is:

- `hoops_for_hope_graphics_master_v28.html`
- `h4h_server_v3.py`
- `Start_H4H_GFX_v3.command`

The package is plain HTML/CSS/JavaScript plus a tiny Python standard-library HTTP server. There is no build system and no npm dependency chain.

The 2026 show machine was macOS + OBS, with the graphics running as a browser source and the on-air package composited through the **Downstream Keyer** plugin.

---

## What the package does

The master HTML contains both the on-air graphics and the operator control panel.

### Standard lower thirds

The normal layout is:

- Countdown bug: lower left, `340×150`, at `X 48 / bottom 48`
- Fundraiser bar: `1456×150`, beginning at `X 416 / bottom 48`
- Live raised amount and goal
- Progress bar
- Periodic event promo takeover
- Periodic Top Players ticker

The standard countdown uses separate Hours / Minutes / Seconds columns. **Do not turn it back into one large `HH:MM:SS` string with separately spaced labels.** That broke alignment when the countdown crossed from 3-digit hours to 2-digit hours.

### Action Compact lower third

For high-action sections such as the skills contest there is an alternate compact layout.

Current dimensions:

- Package width: approximately `780 px`
- Main strip: `780×42`
- Center countdown tab: approximately `148×26`

The compact mode combines fundraiser information and countdown into one centered scorebug-style package.

The panel supports:

- `Standard`
- `Action Compact`
- Master `Show Lower Thirds / Hide Lower Thirds`
- Individual Countdown Show/Hide
- Individual Fundraiser Show/Hide

If the master lower thirds are hidden, Standard / Action Compact should **remain selectable**. That is intentional: it lets the operator preset the next layout off-air and then use the master Show button to build it back in.

### BRB / holding graphics

There are two BRB layouts:

1. **Camera BRB**
   - Transparent fly-on-the-wall camera viewport
   - Editable BRB text
   - Countdown
   - Fundraiser
   - Top Players
   - Animated holding elements

2. **Full Graphic BRB**
   - Full-frame graphics package
   - Editable BRB text
   - Countdown
   - Fundraiser
   - Top Players
   - Animated holding elements

Leaving BRB returns to full-screen program first, keeps the lower thirds hidden for about **1.5 seconds**, then rebuilds the selected lower-third layout using its normal broadcast entrance.

### Color schemes

Two palettes are available from the dock:

- Navy + Candy Red
- Navy + Celtics Green

The current theme transition uses **temporary local overlay pieces**. This is important.

Earlier attempts animated `transform` / `opacity` directly on the real countdown, fundraiser, BRB, and compact DOM elements. That collided with the normal broadcast show/hide animations and badly broke PGM. **Do not reintroduce theme animations on the real graphic elements.**

---

# Quick start

## 1. Put these files in the same folder

At minimum:

```text
hoops_for_hope_graphics_master_v28.html
h4h_server_v3.py
Start_H4H_GFX_v3.command
README.md
```

Older HTML versions can be kept in the same folder as archives, but see the versioning warning below.

## 2. Start the local server

On macOS, double-click:

```text
Start_H4H_GFX_v3.command
```

If macOS says the launcher does not have permission to execute:

```bash
chmod +x /path/to/Start_H4H_GFX_v3.command
```

The easiest method is to type `chmod +x ` in Terminal, then drag the `.command` file into Terminal and press Return.

If Gatekeeper quarantines the downloaded files:

```bash
xattr -d com.apple.quarantine /path/to/Start_H4H_GFX_v3.command
xattr -d com.apple.quarantine /path/to/h4h_server_v3.py
```

You can always bypass the launcher and run:

```bash
cd /path/to/this/folder
python3 h4h_server_v3.py
```

The server binds only to:

```text
127.0.0.1:8765
```

It is intentionally localhost-only and is not exposed to the venue LAN.

## 3. OBS Program Browser Source

Use this URL:

```text
http://127.0.0.1:8765/
```

Use a `1920×1080` browser source. Match the OBS production frame rate; 2026 was run at 60 fps.

Keep the browser source loaded continuously.

Recommended OBS Browser Source behavior:

- **Shutdown source when not visible:** OFF
- **Refresh browser when scene becomes active:** OFF

The graphics have their own timers, state, sync logic, BRB state, and control-channel state. Let the browser source remain alive.

## 4. OBS Custom Browser Dock

Use:

```text
http://127.0.0.1:8765/#panel
```

The same HTML file runs both surfaces:

- no hash = PGM graphics
- `#panel` = operator dock

Do not use a `file://` URL for the dock. Serving both from the same localhost origin is important for the control channel and persistent state.

---

# Versioning and hot reload

The Python server automatically serves the highest clean `*_v#.html` file in its folder.

Examples that **will** be detected:

```text
hoops_for_hope_graphics_master_v28.html
hoops_for_hope_graphics_master_v29.html
hoops_for_hope_graphics_master_v30.html
```

Examples that **will not** be selected by the version matcher:

```text
hoops_for_hope_graphics_master_v29_test.html
hoops_for_hope_graphics_master_v30_final.html
```

The filename must end exactly in:

```text
_v<number>.html
```

The regex in `h4h_server_v3.py` is:

```text
_v(\d+)\.html$
```

### Important

Keep OBS pointed at:

```text
http://127.0.0.1:8765/
```

—not a resolved `..._v28.html` URL.

Server v2 originally redirected `/` to a versioned filename. OBS could then keep refreshing the old resolved file and never discover the next version. **Server v3 fixes this by serving the newest HTML directly at `/` without redirecting.**

For a normal HTML update:

1. Add the new clean `v#.html` file.
2. Refresh the OBS Browser Source.
3. Refresh the Custom Browser Dock.

You do **not** need to restart Python for ordinary HTML revisions.

If `h4h_server_v3.py` itself changes, restart the Python process.

### Another versioning gotcha

The server scans every HTML file in the folder. If an unrelated experimental file is named something like:

```text
test_v99.html
```

the server will consider it the newest graphics file.

Do not leave a higher-numbered unrelated `_v#.html` file in the live folder.

---

# OBS / Downstream Keyer architecture

The 2026 workflow ended up using the H4H graphics package itself as a DSK.

The intended stack is approximately:

```text
TOP
H4H GFX DSK
Camera / FOTW DSK
Program content
BOTTOM
```

A logo DSK can be handled separately depending on the show.

The important rule is:

> **The H4H GFX DSK should own the visible BRB frame/outline. The camera DSK belongs underneath it.**

## Camera BRB viewport

The visible camera frame in the H4H graphics is:

```text
Outer frame:
X 70
Y 150
1120 × 630
```

The script currently prepares the camera DSK scene item to fit inside the frame:

```text
Inner camera bounds:
X 76
Y 156
1108 × 618
```

Current OBS bounds mode:

```text
OBS_BOUNDS_SCALE_OUTER
```

This preserves camera aspect ratio and crop-fills the opening instead of letterboxing it.

The camera viewport in the HTML is intentionally **transparent**.

There was a black-matte experiment in earlier versions. It was removed because the final workflow uses DSK layer order to place the camera behind the H4H frame.

## Downstream Keyer control

The HTML talks to OBS WebSocket and the Downstream Keyer plugin.

Defaults in the dock:

```text
OBS WebSocket:
ws://127.0.0.1:4455

DSK Name:
DSK 1

DSK Camera Scene:
H4H BRB Camera
```

The camera source name must exactly match the OBS source name.

The DSK setup section can:

- connect to OBS WebSocket
- create/update the dedicated camera scene
- add the configured camera source
- apply the viewport transform
- add/select that scene in the configured DSK
- release the camera DSK when Camera BRB ends

The camera DSK uses the plugin vendor WebSocket calls. The H4H GFX DSK itself is part of the normal OBS/Downstream Keyer setup and is not created automatically by this HTML.

### If the camera covers the BRB outline

Check:

1. Camera DSK is **below** the H4H GFX DSK.
2. Camera scene item is using the inner `1108×618 @ 76,156` transform.
3. Bounds are still `SCALE_OUTER`.

### If the camera gets black bars

`SCALE_INNER` was tested and produced bars when the source aspect ratio did not exactly match the opening.

The current code intentionally uses `SCALE_OUTER` to crop-to-fill.

---

# Live fundraiser data

The fundraiser data comes from:

```text
https://playforapurpose.org/
```

The browser source does **not** primarily fetch the website directly.

The local Python server provides:

```text
/api/playforapurpose
```

The server fetches the website server-side, then the HTML requests the local same-origin endpoint. This avoids browser CORS issues inside OBS.

Current polling interval:

```text
15 seconds
```

The server also adds cache-busting headers/query parameters.

The graphics retain the last valid fundraiser value if a sync fails. They should never intentionally zero the fundraiser on a temporary network failure.

## Health check

Open:

```text
http://127.0.0.1:8765/api/health
```

Expected result:

```json
{"ok":true}
```

To inspect the fundraiser proxy directly:

```text
http://127.0.0.1:8765/api/playforapurpose
```

## The parser is fragile by nature

The current overall fundraiser parser expects page text resembling:

```text
$27,004.98 of $70,000 goal
```

The Top Players parser expects headings resembling:

```text
Top Players
...
Select a Player
```

and player entries containing:

```text
Raised $...
```

If Play for a Purpose redesigns its website next year, the server may still successfully fetch the page while the HTML parser fails to find the total or Top Players.

If fundraiser sync is stale:

1. Verify the live website itself has updated.
2. Check `/api/health`.
3. Check `/api/playforapurpose`.
4. Look at the Terminal window running `h4h_server_v3.py`.
5. Check the Fundraiser sync status in the GFX dock.
6. If the proxy contains the correct number but the graphic does not, inspect `parseOverall()` and `parseTopPlayers()` in the HTML.

The direct website request and Jina path remain emergency fallbacks. The localhost proxy is the preferred production path.

---

# Automatic graphics timing

Current 2026 values:

```text
Countdown promo:
Initial delay: 1.2 s
Duration: 7 s
Automatic interval: randomized 10–15 minutes

Top Players:
Initial run: 15 s after load
Automatic interval: every 15 minutes

Top Players -> countdown promo link:
Countdown promo starts ~1.4 s after Top Players begins

Fundraiser sync:
Every 15 s
```

When Top Players runs in Standard mode, the countdown promo card joins it and remains up for the Top Players sequence.

Automatic large takeovers are suppressed in Action Compact mode.

Automatic countdown promo / Top Players are also suppressed while the master lower thirds are hidden.

---

# Control panel

The dock uses a Stream Deck-inspired UI with collapsible banks.

Current sections:

- Looks
- BRB / Holding
- Countdown
- Fundraiser
- Camera DSK

The open/closed state of the banks is remembered locally.

## Looks

Contains:

- Navy + Candy Red
- Navy + Celtics Green
- Standard lower third
- Action Compact lower third
- Master Show / Hide Lower Thirds

### Master lower-third behavior

The master Show/Hide is separate from individual visibility.

Example:

```text
Countdown: enabled
Fundraiser: enabled
Master: hidden
```

Both logical elements remain enabled; they are simply off-air.

While master-hidden, you can change:

- Standard / Action Compact
- individual Countdown visibility
- individual Fundraiser visibility

Those become the configuration for the next master Show.

Standard master Hide uses the same coordinated package-drop language as the Standard -> Action Compact switch.

Compact master Hide animates the whole compact package as one unit.

## BRB

Controls:

- Editable BRB text
- Camera BRB
- Full Graphic BRB
- Hide BRB
- Cut Transition

Changing Standard / Action Compact while BRB is live is allowed. It silently presets which lower third will build when BRB clears.

## Countdown

Controls:

- Run Promo
- Stop
- Show / Hide
- next-auto-animation countdown
- state readout

## Fundraiser

Controls:

- Run Top Players
- Stop
- Show / Hide
- live-data health
- next sync
- last-good age
- Sync Now

---

# State / communication

The Program instance and `#panel` instance communicate locally through browser-side messaging and persistent storage.

They must remain on the same localhost origin.

The dock and program are intentionally render-isolated:

- Program mode does not render the panel.
- Panel mode hard-hides the program graphics.

This isolation was added after an animation regression caused PGM elements to appear over the control dock.

If editing CSS next year, preserve that separation.

---

# 2027 update checklist

Before using this again next year, search the latest HTML for **2026** and update everything that is actually event-specific.

## Required

### 1. Event end time

Current code:

```js
const EVENT_TARGET =
  new Date("2026-10-10T07:00:00-04:00").getTime();
```

Replace with the actual 2027 event end date/time.

Use an explicit UTC offset appropriate for the event date. Do not blindly assume `-04:00`; verify whether the date is in EDT or EST.

### 2. Visible year strings

Search for:

```text
2026
```

Examples include:

```text
Hoops For Hope 2026
2026 Goal
```

Update to the new event year.

### 3. Fallback fundraiser seed

The HTML contains a `SEED` object with fallback:

- raised total
- goal
- Top Players

Update these shortly before the event.

The live sync should replace them, but the seed is what you want on-air if the website is unreachable at startup.

### 4. Fundraising goal

The live website goal is parsed when sync succeeds, but update the fallback goal and any visible year/goal labels anyway.

### 5. Play for a Purpose page format

Verify:

- total parser still works
- Top Players parser still works
- website URL is still correct

### 6. OBS WebSocket / DSK setup

Verify:

- OBS WebSocket is enabled
- port is still `4455` or update it
- password
- DSK plugin is installed
- camera DSK name
- camera scene name
- fly-on-the-wall camera source name
- DSK layer order

### 7. Test the countdown at several lengths

Test at:

- over 100 hours
- under 100 hours
- under 10 hours
- event complete

The separate time-column layout exists specifically because the old label layout broke when hours changed digit count.

---

# Show-day smoke test

Run this before doors:

1. Start `h4h_server_v3.py`.
2. Confirm Terminal shows the expected newest `v#.html`.
3. Open `http://127.0.0.1:8765/`.
4. Open `http://127.0.0.1:8765/#panel`.
5. Confirm the dock says the overlay is linked.
6. Confirm fundraiser total matches the live website.
7. Press **Sync Now** and verify the last-good time updates.
8. Run the countdown promo manually.
9. Run Top Players manually.
10. Confirm the countdown promo joins Top Players at the expected timing.
11. Switch Standard -> Action Compact -> Standard.
12. Master Hide lower thirds.
13. While hidden, change the layout and individual visibility.
14. Master Show and confirm the correct preset builds.
15. Test Navy/Red -> Celtics Green -> Navy/Red.
16. Test Camera BRB.
17. Verify camera DSK fits inside the frame.
18. Test Full Graphic BRB.
19. Exit BRB and verify lower thirds wait ~1.5 seconds before rebuilding.
20. Confirm the panel never shows PGM graphics over itself.
21. Confirm the program feed never displays dock UI.
22. Leave it running for at least one 15-minute Top Players cycle if time permits.

---

# Troubleshooting

## The server does not pick up the newest HTML

Check the filename.

Good:

```text
hoops_for_hope_graphics_master_v29.html
```

Bad:

```text
hoops_for_hope_graphics_master_v29_fix.html
```

Also verify OBS is pointed at:

```text
http://127.0.0.1:8765/
```

not an older direct version URL.

Refresh the Browser Source and dock.

## `.command` will not execute

```bash
chmod +x Start_H4H_GFX_v3.command
```

If necessary:

```bash
xattr -d com.apple.quarantine Start_H4H_GFX_v3.command
xattr -d com.apple.quarantine h4h_server_v3.py
```

## Fundraiser is stale

Check:

```text
/api/health
/api/playforapurpose
```

Then compare the proxy response to the live website.

If the proxy has the correct page but the graphic is stale, the HTML parser probably needs updating.

## Panel buttons are disabled while lower thirds are hidden

That was a bug fixed in v28.

Off-air layout selection is intentional and should remain available.

## Theme transition breaks show/hide animation

Do not animate `transform` or `opacity` on the real graphic elements as part of the theme change.

The safe design is:

1. create temporary overlay pieces
2. animate those pieces
3. change CSS palette variables underneath
4. delete the temporary pieces

The normal graphic animation engine owns the real element transforms.

## PGM graphics appear inside the panel

Panel mode must hard-hide `#programView`.

Do not remove the panel/program render isolation CSS.

## Camera DSK covers the border

The graphics DSK should be above the camera DSK.

The camera is intended to fit the inner box, not the outer `1120×630` frame.

## Camera has black bars

Check that the scene-item bounds mode is still:

```text
OBS_BOUNDS_SCALE_OUTER
```

`SCALE_INNER` was tested and letterboxed the camera.

---

# Development notes / landmines

These are the mistakes most worth remembering.

### Do not make the Custom Browser Dock a `file://` URL

Use the localhost server.

### Do not redirect `/` to the newest version

Serve the newest HTML directly at `/`.

OBS may retain the resolved redirect URL and stop discovering new versions.

### Do not animate real PGM transforms for cosmetic theme changes

The broadcast animation system heavily uses transforms. A second animation system on the same elements will fight it.

### Do not make the BRB camera viewport opaque unless the DSK architecture changes

The current workflow expects:

```text
H4H GFX DSK
Camera DSK
Program
```

The transparent opening is deliberate.

### Do not couple master lower-third visibility to individual visibility

Master Hide is an on/off air gate.

Countdown/Fundraiser visibility is the preset of what should exist when the master comes back.

### Do not disable Standard / Action Compact while master-hidden or BRB is live

Those are exactly the moments when presetting the next layout is most useful.

### Do not revert the countdown labels to fixed spacing

Hours may be 3 digits, 2 digits, then 1 digit. Keep number + label as one column.

---

# Repo hygiene

A sensible repo layout is:

```text
/
├── README.md
├── hoops_for_hope_graphics_master_v28.html
├── h4h_server_v3.py
├── Start_H4H_GFX_v3.command
└── archive/
    ├── hoops_for_hope_graphics_master_v27.html
    ├── hoops_for_hope_graphics_master_v26.html
    └── ...
```

If using `archive/`, keep old versions out of the root live-server folder so an accidentally high version number cannot win the auto-selection.

Do not commit OBS WebSocket passwords or other credentials into the HTML/server. The control panel is designed to store operator configuration locally.

If publishing this publicly, add an explicit `LICENSE` file. No license choice is assumed by this README.

---

# Short version for next year

If you remember nothing else:

```text
1. Update the event date/year.
2. Update fallback fundraiser/player data.
3. Start h4h_server_v3.py.
4. PGM = http://127.0.0.1:8765/
5. Dock = http://127.0.0.1:8765/#panel
6. GFX DSK goes ABOVE Camera DSK.
7. Verify live fundraiser sync.
8. Do not rewrite the theme animation using transforms on real PGM elements.
9. Keep new masters named exactly *_v#.html.
10. Run the show-day smoke test.
```

Good luck, future me.
