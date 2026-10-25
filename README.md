# MiniLab mkII → FL Studio (Windows)

A custom template for using the MiniLab mkII in FL Studio. You don't need FPC, and each sound gets its own channel and its own MIDI data from the start, which makes arranging and mixing easier later.

## What's here

| File | Goes to |
|---|---|
| `MIDI Control Center presets/FL_MPC.minilabmk2` | MiniLab user memory: **MPC mode** |
| `MIDI Control Center presets/FL_Transport.minilabmk2` | MiniLab user memory: **Transport mode** |
| `MIDI Control Center presets/FL_Channel.minilabmk2` | MiniLab user memory: **Channel mode** |
| `FL Studio script/MiniLab mkII FL/` (whole folder) | `Documents\Image-Line\FL Studio\Settings\Hardware\` |

## Setup

1. **Load the presets onto the MiniLab**
   - Install/open **Arturia MIDI Control Center** with the MiniLab plugged in.
   - In the *Project Browser*, click **Import** and pick each `.minilabmk2` file.
   - Store each preset in its own user memory slot. Select the preset, choose a slot on the right, and click **Store To**. For example: User 1 = MPC, User 2 = Transport, User 3 = Channel.
2. **Install the FL script**
   - Copy the folder `MiniLab mkII FL` into
     `C:\Users\<you>\Documents\Image-Line\FL Studio\Settings\Hardware\`
3. **Turn it on in FL Studio**
   - Close MIDI Control Center first (it locks the MIDI port).
   - Go to **Options → MIDI settings**. In *Input*, select **Arturia MiniLab mkII**, tick **Enable**, and set *Controller type* to **MiniLab mkII FL (custom)**.

## Switching modes

Each mode is one MiniLab memory. Hold **Shift** and press the pad for that memory slot (pad 2 = User 1, pad 3 = User 2, pad 4 = User 3). Use the **Pad 1-8 / 9-16** button to reach pads 9–16.

## MPC Mode (yellow pads)

Use the drum pads like a traditional MPC, triggering the sample for that channel.

- Pad 1 triggers channel 1
- Pad 2 triggers channel 2
- …
- Pad 16 triggers channel 16

Use the pads to trigger drums, FX, sample chops, and more.

## Transport Mode

All of the playback controls you need to loop record.

| Pad | Action |
|---|---|
| 1 | Play/Pause |
| 2 | Stop |
| 3 | Record (enable/disable) |
| 4 | Rewind (hold) |
| 5 | Fast Forward (hold) |
| 6 | Pattern/Song Mode |
| 7 | Channel Up |
| 8 | Channel Down |

## Channel Mode (cyan pads)

Each pad selects the matching channel in the FL Studio Channel Rack.

- Pad 1 selects channel 1
- Pad 2 selects channel 2
- …
- Pad 16 selects channel 16

## Notes

- The knobs send plain absolute CCs. To use one, right-click any FL knob, choose **Link to controller…**, and turn the MiniLab knob.
- The keys always play the selected channel.
- MIDI channels the script listens on: MPC = ch 10 (notes 36–51), Transport = ch 16 (CC 20–27), Channel = ch 15 (CC 20–35). If you change them in MCC, change the constants at the top of `device_MiniLabMk2FL.py` to match.
