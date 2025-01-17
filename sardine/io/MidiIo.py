import mido
import threading
from typing import Union, TYPE_CHECKING
from rich.console import Console
from rich import print
import asyncio

if TYPE_CHECKING:
    from ..clock import Clock

__all__ = ('MIDIIo',)


class MIDIIo(threading.Thread):

    """
    Direct MIDI I/O Using Mido. MIDI is also available indirectly
    through SuperDirt. I need to do something to address the redun-
    dancy.
    """

    def __init__(self,
            clock: "Clock",
            port_name: Union[str, None] = None,
            at: Union[float, int] = 0):

        threading.Thread.__init__(self)

        self._midi_ports = mido.get_output_names()
        self.port_name = port_name
        self.clock = clock
        self.after: int = at

        if self.port_name:

            try:
                self._midi = mido.open_output(port_name)
            except Exception as error:
                print(f"[bold red]Init error: {error}[/bold red]")

        else:

            try:
                self._midi = mido.open_output(self.choose_midi_port())
            except Exception as error:
                print(f"[bold red]Init error: {error}[/bold red]")


    def choose_midi_port(self) -> str:
        """ASCII MIDI Port chooser"""
        ports = mido.get_output_names()
        console = Console()
        for (i, item) in enumerate(ports, start=1):
            print(f"[color({i})] [{i}] {item}")
        nb = console.input("[bold yellow] Choose a MIDI Port: [/bold yellow]")
        try:
            nb = int(nb) - 1
            print(f'[yellow]You picked[/yellow] [green]{ports[nb]}[/green].')
            return ports[nb]
        except Exception:
            print(f"Input can only take valid number in range, not {nb}.")
            exit()


    def send(self, message: mido.Message) -> None:
        self._midi.send(message)


    async def send_async(self, message: mido.Message) -> None:
        self._midi.send(message)


    def send_stop(self) -> None:
        """MIDI Start message"""
        self._midi.send(mido.Message('stop'))


    def send_reset(self) -> None:
        """MIDI Reset message"""
        self._midi.send(mido.Message('reset'))


    def send_clock(self) -> None:
        """MIDI Clock Message"""
        self._midi.send(mido.Message('clock'))


    async def send_start(self, initial: bool = False) -> None:
        """MIDI Start message"""
        self._midi.send(mido.Message('start'))


    def schedule(self, message):
        async def _waiter():
            await handle
            self.send(message)

        ticks = self.clock.get_beat_ticks(self.after, sync=False)
        handle = self.clock.wait_after(n_ticks=ticks)
        asyncio.create_task(_waiter(), name='midi-scheduler')


    async def note(self,
            delay: int,
            note:int = 60,
            velocity: int = 127,
            channel:int = 1) -> None:
        """Send a MIDI Note through principal MIDI output"""
        noteon = mido.Message('note_on',
                note=note, velocity=velocity, channel=channel)
        noteoff = mido.Message('note_off',
                note=note, velocity=velocity, channel=channel)
        self.schedule(noteon)
        await asyncio.sleep(delay)
        self.schedule(noteoff)


    async def control_change(self, channel, control, value) -> None:
        """Control Change message"""
        self.schedule(mido.Message('control_change',
            channel=channel, control=control, value=value))


    async def program_change(self, channel, program) -> None:
        """Program change message"""
        self.schedule(mido.Message( 'program_change',
            program=program, channel=channel))


    async def pitchwheel(self, channel, pitch) -> None:
        """Program change message"""
        self.schedule(mido.Message( 'program_change',
            pitch=pitch, channel=channel))
