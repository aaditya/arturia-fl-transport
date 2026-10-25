# name=MiniLab mkII FL (custom)
# url=
#
# Companion script for the MCC presets FL_MPC / FL_Transport / FL_Channel.
# Each preset is one mode; switch modes by switching the MiniLab's memory (Shift + pad).
#
#   MPC mode        (FL_MPC, ch 10, notes 36-51):     pad N triggers channel N
#   Transport mode  (FL_Transport, ch 16, CC 20-27):  play/pause, stop, record, rewind, fast forward,
#                                                     pattern/song, channel up, channel down
#   Channel mode    (FL_Channel, ch 15, CC 20-35):    pad N selects channel N

import channels
import midi
import transport
import ui

CH_MPC = 9
CH_CHANNEL = 14
CH_TRANSPORT = 15

MPC_NOTE_FIRST = 36
PAD_CC_FIRST = 20
PADS = 16
MPC_NOTE = 60  # note sent to the channel (C5 = sample's root)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


class MiniLab:
    def __init__(self):
        self.held = {}  # pad index -> global channel index, for MPC note-offs

    def select_channel(self, index):
        count = channels.channelCount()
        if not 0 <= index < count:
            return
        channels.selectOneChannel(index)
        ui.setHintMsg("Channel: " + channels.getChannelName(index))

    # --- MPC mode ---------------------------------------------------------

    def on_mpc(self, pad, velocity):
        if velocity > 0:
            if pad >= channels.channelCount():
                return
            target = channels.getChannelIndex(pad)
            self.held[pad] = target
            channels.midiNoteOn(target, MPC_NOTE, velocity)
        else:
            target = self.held.pop(pad, None)
            if target is not None:
                channels.midiNoteOn(target, MPC_NOTE, 0)

    # --- Transport mode ---------------------------------------------------

    def on_transport(self, pad, value):
        pressed = value > 0
        if pad in (3, 4):  # rewind / fast forward while held
            seek = transport.rewind if pad == 3 else transport.fastForward
            seek(midi.SS_Start if pressed else midi.SS_Stop)
            return
        if not pressed:
            return
        if pad == 0:
            transport.start()
        elif pad == 1:
            transport.stop()
        elif pad == 2:
            transport.record()
        elif pad == 5:
            transport.setLoopMode()
            ui.setHintMsg("Mode: " + ("Song" if transport.getLoopMode() else "Pattern"))
        elif pad == 6:
            self.select_channel(clamp(channels.selectedChannel() - 1, 0, channels.channelCount() - 1))
        elif pad == 7:
            self.select_channel(clamp(channels.selectedChannel() + 1, 0, channels.channelCount() - 1))

    # --- Channel mode -----------------------------------------------------

    def on_channel(self, pad, value):
        if value > 0:
            self.select_channel(pad)

    # --- dispatch ---------------------------------------------------------

    def on_midi(self, event):
        kind = event.status & 0xF0
        chan = event.midiChan

        if kind in (midi.MIDI_NOTEON, midi.MIDI_NOTEOFF) and chan == CH_MPC:
            pad = event.data1 - MPC_NOTE_FIRST
            if 0 <= pad < PADS:
                self.on_mpc(pad, event.data2 if kind == midi.MIDI_NOTEON else 0)
                event.handled = True

        elif kind == midi.MIDI_CONTROLCHANGE and chan in (CH_TRANSPORT, CH_CHANNEL):
            pad = event.data1 - PAD_CC_FIRST
            if 0 <= pad < PADS:
                if chan == CH_TRANSPORT:
                    self.on_transport(pad, event.data2)
                else:
                    self.on_channel(pad, event.data2)
                event.handled = True


minilab = MiniLab()


def OnMidiMsg(event):
    minilab.on_midi(event)
