# name=MiniLab mkII FL (custom)
# url=
#
# Companion script for the MCC preset FL_Drums16.
#
#   Knobs (ch 1, CC 102-117, relative except 14-16)
#     K1  turn: select channel           click: next pad mode
#     K2  channel volume                 K3  channel pan
#     K4-K8  plugin params 1-5 of the selected channel
#     K9  turn: select mixer track       click: show/hide selected channel's plugin
#     K10 track volume   K11 track pan   K12 track stereo separation   K13 master volume
#     K14-K16  absolute, not handled -> use FL "Link to controller"
#
#   Pads (ch 10, GM drum notes), 3 modes cycled by clicking K1:
#     MPC (yellow):             pad N plays channel N of the current bank of 16 (bank follows K1)
#     Channel (cyan):           pad N selects channel N of the current bank of 16
#     Transport (green):        pads 1-8 = play/pause, stop, record, rewind, fast forward,
#                               song/pattern, channel up, channel down
#                               pads 9-12 = metronome, pattern -, pattern +, undo
#
#   Legacy: ch 16 CC 20-27 (old FL_Drums_Transport preset) still work as transport buttons

import channels
import device
import general
import midi
import mixer
import patterns
import plugins
import transport
import ui

CH_KNOBS = 0
CH_DRUMS = 9
CH_TRANSPORT = 15

KNOB_CC_FIRST = 102
CLICK_K1 = 118
CLICK_K9 = 119
TRANSPORT_CC_FIRST = 20

# Pad index (0-15) for each drum note the presets send; keep in sync with the MCC preset.
DRUM_NOTES = [36, 38, 39, 42, 46, 41, 45, 49,
              37, 40, 44, 47, 50, 51, 54, 56]
PAD_OF_NOTE = {n: i for i, n in enumerate(DRUM_NOTES)}
CHANNEL_RACK_NOTE = 60  # note sent to channels in Channel Rack mode (C5 = sample's root)

MODE_MPC, MODE_TRANSPORT, MODE_CHANNEL = range(3)
MODE_NAMES = ["MPC", "Transport", "Channel"]
BANK_SIZE = 16

PLUGIN_PARAM_KNOBS = 5
STEP = 1.0 / 127

# Pad LED colours (MiniLab sysex)
OFF, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = 0, 1, 4, 5, 16, 17, 20, 127
PAD_LED_FIRST = 0x70
TRANSPORT_MODE_COLORS = [GREEN, YELLOW, RED, CYAN, CYAN, MAGENTA, BLUE, BLUE,
                         WHITE, MAGENTA, MAGENTA, RED, OFF, OFF, OFF, OFF]


def relative(value):
    """Decode a relative encoder value; accepts Relative #1 (64 = 0) and two's complement."""
    if 40 <= value <= 88:
        return value - 64
    if value >= 89:
        return value - 128
    return value


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class MiniLab:
    def __init__(self):
        self.mode = MODE_MPC
        self.held = {}  # pad index -> global channel index, for note-offs in MPC mode
        self.held_seek = {}  # pad index -> transport.rewind / transport.fastForward while held
        self.led_state = None

    # --- feedback ---------------------------------------------------------

    def set_pad_led(self, pad, color):
        if device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42, 0x02, 0x00,
                                       0x10, PAD_LED_FIRST + pad, color, 0xF7]))

    def current_led_state(self):
        return (self.mode, self.bank_start(), channels.channelCount(), channels.selectedChannel())

    def pad_color(self, pad):
        index = self.bank_start() + pad
        exists = index < channels.channelCount()
        if self.mode == MODE_MPC:
            return YELLOW if exists else OFF
        if self.mode == MODE_CHANNEL:
            if not exists:
                return OFF
            return WHITE if index == channels.selectedChannel() else CYAN
        return TRANSPORT_MODE_COLORS[pad]

    def refresh_pad_leds(self):
        self.led_state = self.current_led_state()
        for pad in range(16):
            self.set_pad_led(pad, self.pad_color(pad))

    def hint(self, text):
        ui.setHintMsg(text)

    # --- helpers ----------------------------------------------------------

    def bank_start(self):
        sel = channels.selectedChannel()
        return (max(sel, 0) // BANK_SIZE) * BANK_SIZE

    def select_channel(self, index):
        count = channels.channelCount()
        if not count:
            return
        index = clamp(index, 0, count - 1)
        channels.selectOneChannel(index)
        self.hint("Channel: " + channels.getChannelName(index))

    def step_channel(self, step):
        self.select_channel(channels.selectedChannel() + step)

    def step_pattern(self, step):
        new = clamp(patterns.patternNumber() + step, 1, patterns.patternCount() + 1)
        patterns.jumpToPattern(new)
        self.hint("Pattern " + str(new))

    def toggle_song_mode(self):
        transport.setLoopMode()
        self.hint("Mode: " + ("Song" if transport.getLoopMode() else "Pattern"))

    def nudge_channel_param(self, delta, get, put, lo, hi, scale=1.0):
        ch = channels.selectedChannel()
        if ch < 0:
            return
        put(ch, clamp(get(ch) + delta * STEP * scale, lo, hi))

    def nudge_track_param(self, track, delta, get, put, lo, hi, scale=1.0):
        put(track, clamp(get(track) + delta * STEP * scale, lo, hi))

    # --- knobs ------------------------------------------------------------

    def on_knob(self, knob, value):
        """knob is 0-based physical index (0 = K1 ... 15 = K16). Returns True if handled."""
        if knob >= 13:
            return False  # K14-K16: free for Link to controller

        d = relative(value)
        if d == 0:
            return True

        if knob == 0:
            self.step_channel(1 if d > 0 else -1)
        elif knob == 1:
            self.nudge_channel_param(d, channels.getChannelVolume, channels.setChannelVolume, 0.0, 1.0)
        elif knob == 2:
            self.nudge_channel_param(d, channels.getChannelPan, channels.setChannelPan, -1.0, 1.0, 2.0)
        elif 3 <= knob <= 7:
            self.on_plugin_knob(knob - 3, d)
        elif knob == 8:
            new = clamp(mixer.trackNumber() + (1 if d > 0 else -1), 0, mixer.trackCount() - 2)
            mixer.setTrackNumber(new, midi.curfxScrollToMakeVisible)
            self.hint("Mixer: " + mixer.getTrackName(new))
        elif knob == 9:
            self.nudge_track_param(mixer.trackNumber(), d, mixer.getTrackVolume, mixer.setTrackVolume, 0.0, 1.0)
        elif knob == 10:
            self.nudge_track_param(mixer.trackNumber(), d, mixer.getTrackPan, mixer.setTrackPan, -1.0, 1.0, 2.0)
        elif knob == 11:
            self.nudge_track_param(mixer.trackNumber(), d, mixer.getTrackStereoSep, mixer.setTrackStereoSep, -1.0, 1.0, 2.0)
        elif knob == 12:
            self.nudge_track_param(0, d, mixer.getTrackVolume, mixer.setTrackVolume, 0.0, 1.0)
        return True

    def on_plugin_knob(self, param, delta):
        ch = channels.selectedChannel()
        if ch < 0 or not plugins.isValid(ch):
            return
        if param >= min(PLUGIN_PARAM_KNOBS, plugins.getParamCount(ch)):
            return
        value = clamp(plugins.getParamValue(param, ch) + delta * STEP, 0.0, 1.0)
        plugins.setParamValue(value, param, ch)
        try:
            self.hint(plugins.getParamName(param, ch) + ": " + plugins.getParamValueString(param, ch))
        except Exception:
            pass  # older FL versions lack getParamValueString

    def on_click(self, cc):
        if cc == CLICK_K1:
            self.mode = (self.mode + 1) % len(MODE_NAMES)
            self.hint("Pads: " + MODE_NAMES[self.mode])
            self.refresh_pad_leds()
        elif cc == CLICK_K9:
            ch = channels.selectedChannel()
            if ch >= 0:
                channels.showCSForm(ch, -1)

    # --- pads -------------------------------------------------------------

    def on_pad(self, event):
        """Note-offs always release what the pad started,
        even if the mode changed while it was held."""
        pad = PAD_OF_NOTE.get(event.data1)
        if pad is None:
            return False
        note_on = (event.status & 0xF0) == midi.MIDI_NOTEON and event.data2 > 0
        if not note_on:
            target = self.held.pop(pad, None)
            if target is not None:
                channels.midiNoteOn(target, CHANNEL_RACK_NOTE, 0)
            seek = self.held_seek.pop(pad, None)
            if seek is not None:
                seek(midi.SS_Stop)
            return True

        index = self.bank_start() + pad
        if self.mode == MODE_MPC:
            if index < channels.channelCount():
                target = channels.getChannelIndex(index)
                self.held[pad] = target
                channels.midiNoteOn(target, CHANNEL_RACK_NOTE, event.data2)
        elif self.mode == MODE_CHANNEL:
            if index < channels.channelCount():
                self.select_channel(index)
        elif self.mode == MODE_TRANSPORT:
            self.on_transport_pad(pad)
        return True

    def on_transport_pad(self, pad):
        if pad == 0:
            transport.start()
        elif pad == 1:
            transport.stop()
        elif pad == 2:
            transport.record()
        elif pad in (3, 4):
            seek = transport.rewind if pad == 3 else transport.fastForward
            self.held_seek[pad] = seek
            seek(midi.SS_Start)
        elif pad == 5:
            self.toggle_song_mode()
        elif pad == 6:
            self.step_channel(-1)  # up the Channel Rack
        elif pad == 7:
            self.step_channel(1)
        elif pad == 8:
            transport.globalTransport(midi.FPT_Metronome, 1)
        elif pad in (9, 10):
            self.step_pattern(-1 if pad == 9 else 1)
        elif pad == 11:
            general.undoUp()

    # --- transport pads ---------------------------------------------------

    def on_transport(self, cc, value):
        if value == 0:
            return
        action = cc - TRANSPORT_CC_FIRST
        if action == 0:
            transport.start()
        elif action == 1:
            transport.stop()
        elif action == 2:
            transport.record()
        elif action == 3:
            transport.globalTransport(midi.FPT_Metronome, 1)
        elif action == 4:
            self.toggle_song_mode()
        elif action in (5, 6):
            self.step_pattern(-1 if action == 5 else 1)
        elif action == 7:
            general.undoUp()

    # --- dispatch ---------------------------------------------------------

    def on_midi(self, event):
        kind = event.status & 0xF0
        chan = event.midiChan

        if kind == midi.MIDI_CONTROLCHANGE:
            cc, value = event.data1, event.data2
            if chan == CH_KNOBS and KNOB_CC_FIRST <= cc < KNOB_CC_FIRST + 16:
                event.handled = self.on_knob(cc - KNOB_CC_FIRST, value)
            elif chan == CH_KNOBS and cc in (CLICK_K1, CLICK_K9):
                if value > 0:
                    self.on_click(cc)
                event.handled = True
            elif chan == CH_TRANSPORT and TRANSPORT_CC_FIRST <= cc < TRANSPORT_CC_FIRST + 8:
                self.on_transport(cc, value)
                event.handled = True

        elif kind in (midi.MIDI_NOTEON, midi.MIDI_NOTEOFF) and chan == CH_DRUMS:
            event.handled = self.on_pad(event)


minilab = MiniLab()


def OnInit():
    minilab.refresh_pad_leds()


def OnDeInit():
    for pad in range(16):
        minilab.set_pad_led(pad, OFF)


def OnMidiMsg(event):
    minilab.on_midi(event)


def OnRefresh(flags):
    if minilab.current_led_state() != minilab.led_state:
        minilab.refresh_pad_leds()
