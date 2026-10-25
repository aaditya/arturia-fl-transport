# name=MiniLab mkII FL (custom)
# url=
#
# Companion script for the MCC presets FL_Drums_Transport / FL_Drums16.
#
#   Knobs (ch 1, CC 102-117, relative except 14-16)
#     K1  turn: select channel           click: toggle pad mode (Selected channel / Channel Rack)
#     K2  channel volume                 K3  channel pan
#     K4-K8  plugin params 1-5 of the selected channel
#     K9  turn: select mixer track       click: show/hide selected channel's plugin
#     K10 track volume   K11 track pan   K12 track stereo separation   K13 master volume
#     K14-K16  absolute, not handled -> use FL "Link to controller"
#
#   Pads (ch 10, GM drum notes)
#     Selected-channel mode: notes go to the selected channel (FPC, Battery, ...)
#     Channel Rack mode:     pad N plays channel N of the current bank of 8 (bank follows K1)
#
#   Transport pads 9-16 (ch 16, CC 20-27, FL_Drums_Transport preset only)
#     play/pause, stop, record, metronome, song/pattern, pattern -, pattern +, undo

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

PLUGIN_PARAM_KNOBS = 5
STEP = 1.0 / 127

# Pad LED colours (MiniLab sysex)
OFF, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = 0, 1, 4, 5, 16, 17, 20, 127
PAD_LED_FIRST = 0x70


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
        self.channel_rack_mode = False
        self.held = {}  # pad index -> global channel index, for note-offs in Channel Rack mode
        self.led_state = None

    # --- feedback ---------------------------------------------------------

    def set_pad_led(self, pad, color):
        if device.isAssigned():
            device.midiOutSysex(bytes([0xF0, 0x00, 0x20, 0x6B, 0x7F, 0x42, 0x02, 0x00,
                                       0x10, PAD_LED_FIRST + pad, color, 0xF7]))

    def refresh_pad_leds(self):
        self.led_state = (self.channel_rack_mode, self.bank_start(), channels.channelCount())
        if self.channel_rack_mode:
            first = self.bank_start()
            for pad in range(8):
                self.set_pad_led(pad, YELLOW if first + pad < channels.channelCount() else OFF)
        else:
            for pad in range(8):
                self.set_pad_led(pad, BLUE)

    def hint(self, text):
        ui.setHintMsg(text)

    # --- helpers ----------------------------------------------------------

    def bank_start(self):
        sel = channels.selectedChannel()
        return (max(sel, 0) // 8) * 8

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
            count = channels.channelCount()
            if count:
                new = clamp(channels.selectedChannel() + (1 if d > 0 else -1), 0, count - 1)
                channels.selectOneChannel(new)
                self.hint("Channel: " + channels.getChannelName(new))
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
            self.channel_rack_mode = not self.channel_rack_mode
            self.hint("Pads: " + ("Channel Rack" if self.channel_rack_mode else "Selected channel"))
            self.refresh_pad_leds()
        elif cc == CLICK_K9:
            ch = channels.selectedChannel()
            if ch >= 0:
                channels.showCSForm(ch, -1)

    # --- pads -------------------------------------------------------------

    def on_pad(self, event):
        """Channel Rack mode only: route pad to channel N of the current bank."""
        pad = PAD_OF_NOTE.get(event.data1)
        if pad is None:
            return False
        note_on = (event.status & 0xF0) == midi.MIDI_NOTEON and event.data2 > 0
        if note_on:
            index = self.bank_start() + pad
            if index >= channels.channelCount():
                return True
            target = channels.getChannelIndex(index)
            self.held[pad] = target
            channels.midiNoteOn(target, CHANNEL_RACK_NOTE, event.data2)
        else:
            target = self.held.pop(pad, None)
            if target is not None:
                channels.midiNoteOn(target, CHANNEL_RACK_NOTE, 0)
        return True

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
            transport.setLoopMode()
            self.hint("Mode: " + ("Song" if transport.getLoopMode() else "Pattern"))
        elif action in (5, 6):
            step = -1 if action == 5 else 1
            new = clamp(patterns.patternNumber() + step, 1, patterns.patternCount() + 1)
            patterns.jumpToPattern(new)
            self.hint("Pattern " + str(new))
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
            if self.channel_rack_mode:
                event.handled = self.on_pad(event)
            # otherwise unhandled: FL plays the note on the selected channel


minilab = MiniLab()


def OnInit():
    minilab.refresh_pad_leds()


def OnDeInit():
    for pad in range(8):
        minilab.set_pad_led(pad, OFF)


def OnMidiMsg(event):
    minilab.on_midi(event)


def OnRefresh(flags):
    if (minilab.channel_rack_mode, minilab.bank_start(), channels.channelCount()) != minilab.led_state:
        minilab.refresh_pad_leds()
