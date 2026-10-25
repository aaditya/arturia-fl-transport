# MiniLab mkII → FL Studio (Windows)

## What's here

| File | Goes to |
|---|---|
| `MIDI Control Center presets/FL_Drums_Transport.minilabmk2` | MiniLab user memory (pads 1–8 drums, pads 9–16 transport) |
| `MIDI Control Center presets/FL_Drums16.minilabmk2` | MiniLab user memory (all 16 pads drums) |
| `FL Studio script/MiniLab mkII FL/` (whole folder) | `Documents\Image-Line\FL Studio\Settings\Hardware\` |

## Setup

1. **Load the presets onto the MiniLab**
   - Install/open **Arturia MIDI Control Center** with the MiniLab plugged in.
   - In the *Project Browser*, click **Import** and pick a `.minilabmk2` file.
   - Select the imported preset, choose a free user memory slot (e.g. User 2) on the right, and click **Store To**. Do the same for the other preset in another slot.
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

### Pads (MIDI ch 10, General MIDI drum notes)

| Pad | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|
| Bank 1 | Kick 36 | Snare 38 | Clap 39 | Closed HH 42 | Open HH 46 | Low tom 41 | Mid tom 45 | Crash 49 |
| Bank 2 (*Drums16*) | Rim 37 | Snare 2 40 | Pedal HH 44 | Low-mid tom 47 | High tom 50 | Ride 51 | Tambourine 54 | Cowbell 56 |
| Bank 2 (*Drums_Transport*) | ▶ Play/Pause | ■ Stop | ● Record | Metronome | Song/Pattern | Pattern − | Pattern + | Undo |

Use the MiniLab's **Pad 1-8 / 9-16** button to switch between banks.

Click **K1** to switch the pad mode:
- **Selected channel** (blue pads, the default): notes go to whichever channel is selected. Use this for **FPC** or other drum plugins with GM mapping (Battery, etc.). This mode records normally.
- **Channel Rack** (yellow pads): pad N plays channel N of the current bank of 8 channels. With the default template, pad 1 plays Kick, pad 2 Clap, pad 3 Hat, and pad 4 Snare. Turn K1 to move between banks (channels 1–8, 9–16, …). In this mode, pads 9–16 of *Drums16* play the next 8 channels. This mode is made for finger-drumming the Channel Rack. To record into the piano roll, use Selected channel mode.

## Tweaking

To change CC numbers or notes, edit the constants at the top of `device_MiniLabMk2FL.py`. If you change them in MCC, change the script to match.
