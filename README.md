# MiniLab mkII → FL Studio (Windows)

## What's here

| File | Goes to |
|---|---|
| `MIDI Control Center presets/FL_Drums16.minilabmk2` | MiniLab user memory (one preset does everything) |
| `FL Studio script/MiniLab mkII FL/` (whole folder) | `Documents\Image-Line\FL Studio\Settings\Hardware\` |

## Setup

1. **Load the presets onto the MiniLab**
   - Install/open **Arturia MIDI Control Center** with the MiniLab plugged in.
   - In the *Project Browser*, click **Import** and pick `FL_Drums16.minilabmk2`.
   - Select the imported preset, choose a free user memory slot (e.g. User 2) on the right, and click **Store To**.
   - On the MiniLab, hold **Shift** and press the pad for that memory slot to switch to it.
2. **Install the FL script**
   - Copy the folder `MiniLab mkII FL` into
     `C:\Users\<you>\Documents\Image-Line\FL Studio\Settings\Hardware\`
3. **Turn it on in FL Studio**
   - Close MIDI Control Center first (it locks the MIDI port).
   - Go to **Options → MIDI settings**. In *Input*, select **Arturia MiniLab mkII**, tick **Enable**, and set *Controller type* to **MiniLab mkII FL (custom)**.
   - In *Output*, select the MiniLab and give it the same **Port** number as the input. This lets the script light up the pads.

## Layout

```
 ┌K1───────┬K2──────┬K3─────┬K4──────┬K5──────┬K6──────┬K7──────┬K8──────┐
 │Select ch│Ch vol  │Ch pan │Plugin 1│Plugin 2│Plugin 3│Plugin 4│Plugin 5│  ← Channel Rack
 │click:   │        │       │        │        │        │        │        │
 │pad mode │        │       │        │        │        │        │        │
 ├K9───────┼K10─────┼K11────┼K12─────┼K13─────┼K14─────┼K15─────┼K16─────┤
 │Select   │Track   │Track  │Stereo  │Master  │ free   │ free   │ free   │  ← Mixer
 │mixer trk│vol     │pan    │sep     │vol     │(link)  │(link)  │(link)  │
 │click:   │        │       │        │        │        │        │        │
 │plugin   │        │       │        │        │        │        │        │
 └─────────┴────────┴───────┴────────┴────────┴────────┴────────┴────────┘
```

- K1–K13 are endless (relative), so values never jump. "Plugin 1–5" are the first 5 parameters of the selected channel's instrument.
- **K14–K16** send plain CC 115–117. To use one, right-click any FL knob, choose **Link to controller…**, and turn the MiniLab knob.

### Pads

All 16 pads send drum notes (MIDI ch 10). Use the MiniLab's **Pad 1-8 / 9-16** button to switch between the two rows. **Click K1** to cycle through the 3 pad modes (MPC → Transport → Channel). The pad colours show which mode you're in, and FL's hint bar shows the mode name.

| Mode | Colour | What the pads do |
|---|---|---|
| **MPC** (default) | Yellow | Pad N plays channel N of the Channel Rack (pads 1–16 → channels 1–16), for drums, FX and sample chops, one channel each. |
| **Transport** | Coloured per function | See below. |
| **Channel** | Cyan (selected pad is white) | Pad N selects channel N. |

MPC and Channel work on banks of 16 channels. Turn **K1** past channel 16 and the pads move to channels 17–32, and so on.

**Transport mode:**

| Pad | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| | ▶ Play/Pause | ■ Stop | ● Record on/off | ⏪ Rewind (hold) | ⏩ Fast forward (hold) | Song/Pattern | Channel up | Channel down |

| Pad | 9 | 10 | 11 | 12 | 13–16 |
|---|---|---|---|---|---|
| | Metronome | Pattern − | Pattern + | Undo | — |

"Channel up" moves up the Channel Rack (to the previous channel).

Typical loop-record flow: in **Transport** mode, press Record, then Play. Click K1 twice to reach **MPC** and play the part. Click K1 once to get back to Transport. To play a melody, select its channel (in **Channel** mode or with K1) and use the keys, which always play the selected channel.

> The old `FL_Drums_Transport` preset has been merged into Transport mode and removed. If it's still stored on your MiniLab, its pads 9–16 keep working, but you no longer need it.

## Tweaking

To change CC numbers or notes, edit the constants at the top of `device_MiniLabMk2FL.py`. If you change them in MCC, change the script to match.
