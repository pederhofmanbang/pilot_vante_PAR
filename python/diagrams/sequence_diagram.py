"""
Professionellt sekvensdiagram för Regiongemensam hubb
Genererat med Python och matplotlib
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Rectangle, FancyArrowPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as path_effects
import numpy as np
from dataclasses import dataclass
from typing import List, Tuple, Optional
import os

# ============================================================
# Moderna färgpaletter (Tailwind-inspirerade)
# ============================================================
COLORS = {
    # Participants
    'region_box': '#C7F9CC',
    'region_participant': '#86EFAC',
    'hubb_box': '#BFDBFE',
    'hubb_participant': '#60A5FA',
    'spe_box': '#DDD6FE',
    'spe_participant': '#A78BFA',
    'externa_box': '#FED7AA',
    'sos_participant': '#FB923C',
    'extern_participant': '#F97316',

    # Notes
    'note_info': '#E0F2FE',
    'note_warning': '#FEF3C7',
    'note_danger': '#FEE2E2',
    'note_success': '#DCFCE7',
    'note_purple': '#F3E8FF',

    # Sections
    'section_header': '#E0E7FF',
    'loop_bg': '#F0FDF4',
    'alt_bg': '#FEF9C3',
    'par_bg': '#EFF6FF',
    'critical_bg': '#FEF2F2',

    # Lines and text
    'arrow': '#1E3A5F',
    'lifeline': '#94A3B8',
    'text_dark': '#1F2937',
    'text_medium': '#4B5563',
    'border': '#374151',
}


@dataclass
class Participant:
    """Representerar en deltagare i sekvensdiagrammet"""
    id: str
    name: str
    subtitle: str
    x: float
    color: str
    box_color: str


class SequenceDiagram:
    """Professionell sekvensdiagram-generator"""

    def __init__(self, width: float = 24, height: float = 40):
        self.fig, self.ax = plt.subplots(1, 1, figsize=(width, height))
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.axis('off')
        self.ax.set_facecolor('white')
        self.fig.patch.set_facecolor('white')

        self.current_y = 95  # Börja från toppen
        self.participants: List[Participant] = []
        self.lifeline_start_y = 0

    def add_title(self, title: str, subtitle: str = ""):
        """Lägg till titel"""
        self.ax.text(50, 98, title,
                    fontsize=18, fontweight='bold',
                    ha='center', va='top',
                    color=COLORS['text_dark'])
        if subtitle:
            self.ax.text(50, 96.5, subtitle,
                        fontsize=11, ha='center', va='top',
                        color=COLORS['text_medium'], style='italic')
        self.current_y = 94

    def setup_participants(self, participants: List[Tuple[str, str, str, str, str]]):
        """
        Sätt upp deltagare
        Varje tuple: (id, namn, subtitle, participant_color, box_color)
        """
        n = len(participants)
        spacing = 80 / (n + 1)

        for i, (pid, name, subtitle, p_color, b_color) in enumerate(participants):
            x = 10 + spacing * (i + 1)
            self.participants.append(Participant(pid, name, subtitle, x, p_color, b_color))

        self._draw_participants()
        self.lifeline_start_y = self.current_y - 2

    def _draw_participants(self):
        """Rita deltagare-boxar"""
        box_width = 10
        box_height = 4

        for p in self.participants:
            # Rita box med rundade hörn
            box = FancyBboxPatch(
                (p.x - box_width/2, self.current_y - box_height),
                box_width, box_height,
                boxstyle="round,pad=0.02,rounding_size=0.3",
                facecolor=p.color,
                edgecolor=COLORS['border'],
                linewidth=2,
                zorder=10
            )
            self.ax.add_patch(box)

            # Namn
            self.ax.text(p.x, self.current_y - 1.2, p.name,
                        fontsize=10, fontweight='bold',
                        ha='center', va='center',
                        color=COLORS['text_dark'], zorder=11)
            # Subtitle
            self.ax.text(p.x, self.current_y - 2.8, p.subtitle,
                        fontsize=8, ha='center', va='center',
                        color=COLORS['text_medium'], zorder=11)

        self.current_y -= box_height + 1

    def _get_participant_x(self, pid: str) -> float:
        """Hämta x-koordinat för deltagare"""
        for p in self.participants:
            if p.id == pid:
                return p.x
        raise ValueError(f"Participant {pid} not found")

    def _draw_lifelines(self, end_y: float):
        """Rita livslinjerna"""
        for p in self.participants:
            self.ax.plot([p.x, p.x], [self.lifeline_start_y, end_y],
                        color=COLORS['lifeline'], linestyle='--',
                        linewidth=1.5, zorder=1)

    def add_section(self, title: str, color: str = None):
        """Lägg till en sektionsrubrik"""
        self.current_y -= 2

        if color is None:
            color = COLORS['section_header']

        # Rita sektionsrubrik
        rect = FancyBboxPatch(
            (5, self.current_y - 1.5), 90, 2,
            boxstyle="round,pad=0.02,rounding_size=0.2",
            facecolor=color,
            edgecolor='#4F46E5',
            linewidth=1.5,
            zorder=5
        )
        self.ax.add_patch(rect)

        self.ax.text(50, self.current_y - 0.5, title,
                    fontsize=11, fontweight='bold',
                    ha='center', va='center',
                    color='#3730A3', zorder=6)

        self.current_y -= 3

    def add_message(self, from_id: str, to_id: str, text: str,
                   style: str = 'solid', response: bool = False,
                   self_message: bool = False, number: int = None):
        """
        Lägg till ett meddelande mellan deltagare
        style: 'solid', 'dashed'
        """
        from_x = self._get_participant_x(from_id)
        to_x = self._get_participant_x(to_id)

        self.current_y -= 1.5

        if self_message or from_id == to_id:
            # Self-message (loop tillbaka)
            self._draw_self_message(from_x, text, number)
        else:
            # Vanligt meddelande
            linestyle = '--' if style == 'dashed' or response else '-'
            arrow_style = '<|-' if response else '-|>'

            # Rita pil
            arrow = FancyArrowPatch(
                (from_x, self.current_y), (to_x, self.current_y),
                arrowstyle=arrow_style,
                mutation_scale=15,
                color=COLORS['arrow'],
                linewidth=2,
                linestyle=linestyle,
                zorder=8
            )
            self.ax.add_patch(arrow)

            # Text ovanför pilen
            mid_x = (from_x + to_x) / 2
            label = f"{number}. {text}" if number else text

            # Bakgrund för text
            txt = self.ax.text(mid_x, self.current_y + 0.5, label,
                              fontsize=8, ha='center', va='bottom',
                              color=COLORS['text_dark'], zorder=9,
                              bbox=dict(boxstyle='round,pad=0.2',
                                       facecolor='white',
                                       edgecolor='none',
                                       alpha=0.9))

        self.current_y -= 0.5

    def _draw_self_message(self, x: float, text: str, number: int = None):
        """Rita ett meddelande till sig själv"""
        offset = 3
        height = 1.5

        # Rita loop
        self.ax.plot([x, x + offset, x + offset, x],
                    [self.current_y, self.current_y,
                     self.current_y - height, self.current_y - height],
                    color=COLORS['arrow'], linewidth=2, zorder=8)

        # Pilspets
        self.ax.annotate('', xy=(x, self.current_y - height),
                        xytext=(x + offset, self.current_y - height),
                        arrowprops=dict(arrowstyle='-|>',
                                       color=COLORS['arrow'],
                                       lw=2),
                        zorder=8)

        # Text
        label = f"{number}. {text}" if number else text
        self.ax.text(x + offset + 0.5, self.current_y - height/2, label,
                    fontsize=8, ha='left', va='center',
                    color=COLORS['text_dark'], zorder=9)

        self.current_y -= height

    def add_note(self, participant_id: str, text: str,
                position: str = 'right', color: str = None,
                width: float = 15):
        """
        Lägg till en notis
        position: 'right', 'left', 'over'
        """
        x = self._get_participant_x(participant_id)

        if color is None:
            color = COLORS['note_info']

        lines = text.split('\n')
        height = len(lines) * 0.8 + 1

        self.current_y -= 0.5

        if position == 'right':
            note_x = x + 6
        elif position == 'left':
            note_x = x - 6 - width
        else:  # over
            note_x = x - width/2

        # Rita not-box
        note = FancyBboxPatch(
            (note_x, self.current_y - height),
            width, height,
            boxstyle="round,pad=0.02,rounding_size=0.2",
            facecolor=color,
            edgecolor=COLORS['border'],
            linewidth=1,
            zorder=7
        )
        self.ax.add_patch(note)

        # Rita text
        y_offset = 0.5
        for line in lines:
            if line.startswith('**') and line.endswith('**'):
                # Bold text
                self.ax.text(note_x + 0.5, self.current_y - y_offset,
                            line.strip('*'),
                            fontsize=8, fontweight='bold',
                            ha='left', va='top',
                            color=COLORS['text_dark'], zorder=8)
            else:
                self.ax.text(note_x + 0.5, self.current_y - y_offset,
                            line,
                            fontsize=7, ha='left', va='top',
                            color=COLORS['text_medium'], zorder=8)
            y_offset += 0.8

        self.current_y -= height + 0.5

    def add_note_over(self, from_id: str, to_id: str, text: str,
                     color: str = None):
        """Lägg till en notis som sträcker sig över flera deltagare"""
        from_x = self._get_participant_x(from_id)
        to_x = self._get_participant_x(to_id)

        if color is None:
            color = COLORS['note_info']

        lines = text.split('\n')
        height = len(lines) * 0.8 + 1
        width = abs(to_x - from_x) + 10
        note_x = min(from_x, to_x) - 5

        self.current_y -= 0.5

        # Rita not-box
        note = FancyBboxPatch(
            (note_x, self.current_y - height),
            width, height,
            boxstyle="round,pad=0.02,rounding_size=0.2",
            facecolor=color,
            edgecolor=COLORS['border'],
            linewidth=1,
            zorder=7
        )
        self.ax.add_patch(note)

        # Rita text
        y_offset = 0.5
        for line in lines:
            weight = 'bold' if line.startswith('**') else 'normal'
            clean_line = line.strip('*')
            self.ax.text(note_x + width/2, self.current_y - y_offset,
                        clean_line,
                        fontsize=8, fontweight=weight,
                        ha='center', va='top',
                        color=COLORS['text_dark'], zorder=8)
            y_offset += 0.8

        self.current_y -= height + 0.5

    def start_block(self, block_type: str, label: str, color: str = None):
        """Starta ett block (loop, alt, par, critical)"""
        self.current_y -= 1
        self._block_start_y = self.current_y
        self._block_type = block_type
        self._block_label = label

        if color is None:
            color_map = {
                'loop': COLORS['loop_bg'],
                'alt': COLORS['alt_bg'],
                'par': COLORS['par_bg'],
                'critical': COLORS['critical_bg'],
                'group': '#F3F4F6'
            }
            color = color_map.get(block_type, '#F9FAFB')
        self._block_color = color

    def end_block(self):
        """Avsluta ett block"""
        height = self._block_start_y - self.current_y + 1

        # Rita block-rektangel
        rect = FancyBboxPatch(
            (8, self.current_y - 1),
            84, height,
            boxstyle="round,pad=0.02,rounding_size=0.3",
            facecolor=self._block_color,
            edgecolor=COLORS['border'],
            linewidth=1.5,
            alpha=0.5,
            zorder=2
        )
        self.ax.add_patch(rect)

        # Block-typ label
        label_box = FancyBboxPatch(
            (8, self._block_start_y - 1.5),
            8, 1.5,
            boxstyle="round,pad=0.02,rounding_size=0.2",
            facecolor=COLORS['border'],
            edgecolor=COLORS['border'],
            linewidth=1,
            zorder=3
        )
        self.ax.add_patch(label_box)

        self.ax.text(12, self._block_start_y - 0.75, self._block_type.upper(),
                    fontsize=8, fontweight='bold',
                    ha='center', va='center',
                    color='white', zorder=4)

        # Block-label
        self.ax.text(18, self._block_start_y - 0.75, self._block_label,
                    fontsize=8, ha='left', va='center',
                    color=COLORS['text_dark'], zorder=4)

        self.current_y -= 1

    def add_else_divider(self, label: str):
        """Lägg till en else/alternative-avgränsare"""
        self.ax.plot([8, 92], [self.current_y, self.current_y],
                    color=COLORS['border'], linestyle='--',
                    linewidth=1, zorder=3)

        self.ax.text(12, self.current_y + 0.3, f"[{label}]",
                    fontsize=8, ha='left', va='bottom',
                    color=COLORS['text_medium'],
                    style='italic', zorder=4)

        self.current_y -= 1

    def add_legend(self, items: List[Tuple[str, str]]):
        """Lägg till en legend"""
        self.current_y -= 2

        # Legend box
        legend_height = len(items) * 1.2 + 1
        legend = FancyBboxPatch(
            (5, self.current_y - legend_height),
            25, legend_height,
            boxstyle="round,pad=0.02,rounding_size=0.3",
            facecolor='#F9FAFB',
            edgecolor=COLORS['border'],
            linewidth=1,
            zorder=7
        )
        self.ax.add_patch(legend)

        y_offset = 0.8
        for title, desc in items:
            if title.startswith('**'):
                self.ax.text(7, self.current_y - y_offset, title.strip('*'),
                            fontsize=9, fontweight='bold',
                            ha='left', va='top',
                            color=COLORS['text_dark'], zorder=8)
            else:
                self.ax.text(7, self.current_y - y_offset, f"• {title}: {desc}",
                            fontsize=8, ha='left', va='top',
                            color=COLORS['text_medium'], zorder=8)
            y_offset += 1.2

        self.current_y -= legend_height + 1

    def add_spacer(self, height: float = 1):
        """Lägg till vertikalt utrymme"""
        self.current_y -= height

    def finalize(self, end_y: float = None):
        """Slutför diagrammet"""
        if end_y is None:
            end_y = self.current_y - 2

        # Rita livslinjerna
        self._draw_lifelines(end_y)

        # Rita deltagare igen längst ner
        box_width = 10
        box_height = 3

        for p in self.participants:
            box = FancyBboxPatch(
                (p.x - box_width/2, end_y - box_height),
                box_width, box_height,
                boxstyle="round,pad=0.02,rounding_size=0.3",
                facecolor=p.color,
                edgecolor=COLORS['border'],
                linewidth=2,
                zorder=10
            )
            self.ax.add_patch(box)

            self.ax.text(p.x, end_y - box_height/2, p.name,
                        fontsize=9, fontweight='bold',
                        ha='center', va='center',
                        color=COLORS['text_dark'], zorder=11)

        # Justera figurstorleken
        self.ax.set_ylim(end_y - box_height - 1, 100)

    def save(self, filename: str, dpi: int = 150):
        """Spara diagrammet"""
        self.fig.savefig(filename, dpi=dpi, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
        print(f"Saved: {filename}")

    def show(self):
        """Visa diagrammet"""
        plt.show()


def create_regiongemensam_hubb_diagram():
    """Skapa det kompletta sekvensdiagrammet för Regiongemensam hubb"""

    # Skapa diagram
    diagram = SequenceDiagram(width=28, height=50)

    # Titel
    diagram.add_title(
        "Regiongemensam hubb – flöde, federering och distribution",
        "(detaljnivå)"
    )

    # Deltagare
    diagram.setup_participants([
        ('region', 'Region', '(Producent + mottagare)',
         COLORS['region_participant'], COLORS['region_box']),
        ('hubb', 'Hubb', '(Standard + benchmark + transport)',
         COLORS['hubb_participant'], COLORS['hubb_box']),
        ('spe', 'SPE', '(Federerad beräkning)',
         COLORS['spe_participant'], COLORS['spe_box']),
        ('sos', 'Socialstyrelsen', '(SoS)',
         COLORS['sos_participant'], COLORS['externa_box']),
        ('extern', 'Övriga externa', '(Forskning m.fl.)',
         COLORS['extern_participant'], COLORS['externa_box']),
    ])

    # ============================================================
    # Inledande noter
    # ============================================================
    diagram.add_note('hubb',
        "**Hubbens standardpaket (P1–P7)**\n"
        "P1. Gemensamma variabellistor\n"
        "P2. Gemensamma definitioner/struktur\n"
        "P3. Gemensamt räknesätt för väntetider\n"
        "P4. Gemensamma kvalitetskontroller\n"
        "P5. Stöd för att koppla rätt\n"
        "P6. Mallar för leveranser\n"
        "P7. Spårbarhet",
        position='right', color=COLORS['note_info'], width=18
    )

    diagram.add_note('spe',
        "**Vad SPE är**\n"
        "• Kör frågor nära datat\n"
        "• Hämtar ej individnivå i bulk\n"
        "• Samlar sammanställda delresultat\n"
        "• Används via policy-gate",
        position='right', color=COLORS['note_purple'], width=16
    )

    # Legend
    diagram.add_legend([
        ("**Push vs Pull**", ""),
        ("Push", "Region skickar leverans (krypterad)"),
        ("Pull", "Federerad fråga via SPE → aggregat"),
    ])

    # ============================================================
    # Sektion 1: Standardpaket
    # ============================================================
    diagram.add_section("1. Standardpaket (byggs och hålls uppdaterat centralt)")

    diagram.start_block('loop', 'Vid uppdatering (ny version / nya krav)')
    diagram.add_message('hubb', 'region', 'Publicerar uppdaterat standardpaket (P1–P7)', number=1)
    diagram.add_note_over('hubb', 'region',
        "Regionen slipper bygga om från grunden.\n"
        "Uppgraderar version och kör samma flöde igen.",
        color=COLORS['note_warning']
    )
    diagram.end_block()

    # ============================================================
    # Sektion 2: Region skapar basunderlag
    # ============================================================
    diagram.add_section("2. Region skapar basunderlag (brett) och kör enligt standard")

    diagram.add_message('region', 'region', 'Skapar basunderlag (brett)', number=2, self_message=True)
    diagram.add_message('region', 'region', 'Gör automatiska kontroller (kvalitet)', number=3, self_message=True)
    diagram.add_message('region', 'region', 'Räknar väntetider enligt gemensamt räknesätt (P3)', number=4, self_message=True)
    diagram.add_message('region', 'region', 'Förbereder för snabb selektering', number=5, self_message=True)

    diagram.add_note('region',
        "**Nyckelidé:**\n"
        "Regionen tar fram ett bredare\n"
        "underlag en gång. Sedan görs\n"
        "urval per användningsfall.",
        position='left', color=COLORS['note_success'], width=14
    )

    # ============================================================
    # Sektion 3: Urval per användningsfall
    # ============================================================
    diagram.add_section("3. Urval per användningsfall (från samma basunderlag)")

    diagram.start_block('group', 'Regionen gör urval/mappning per behov')
    diagram.add_message('region', 'region', 'Urval A – benchmark (utan person-id)', number=6, self_message=True)
    diagram.add_message('region', 'region', 'Urval B – SoS väntetider', number=7, self_message=True)
    diagram.add_message('region', 'region', 'Urval C – SoS patientdata', number=8, self_message=True)
    diagram.add_message('region', 'region', 'Urval D – övrig extern', number=9, self_message=True)
    diagram.end_block()

    # ============================================================
    # Sektion 4: PUSH-flöden
    # ============================================================
    diagram.add_section("4. Två spår – PUSH (benchmark + extern distribution)")

    diagram.start_block('par', 'Spår A: Benchmark & återkoppling (utan person-id)', COLORS['par_bg'])
    diagram.add_message('region', 'hubb', 'Skickar Urval A (sammanställning utan person-id)', number=10)
    diagram.add_message('hubb', 'hubb', 'Bygger jämförelser över regioner & tid', number=11, self_message=True)
    diagram.add_message('hubb', 'region', 'Skickar tillbaka benchmark + insikter', number=12, response=True)

    diagram.add_else_divider('Spår B: Distribution till externa (blind relay)')

    diagram.add_message('region', 'hubb', 'Skickar krypterat paket + manifest', number=13)

    diagram.add_note_over('region', 'hubb',
        "**Hubben kan inte dekryptera.**\n"
        "Hanterar endast transport, spårbarhet, kvittens.",
        color=COLORS['note_danger']
    )

    diagram.add_message('hubb', 'sos', 'Vidarebefordrar krypterat paket (blind relay)', number=14)
    diagram.add_message('sos', 'hubb', 'Status/kvittens', response=True)
    diagram.add_message('hubb', 'extern', 'Vidarebefordrar krypterat paket (blind relay)', number=15)
    diagram.add_message('extern', 'hubb', 'Status/kvittens', response=True)
    diagram.add_message('hubb', 'region', 'Returnerar status/kvittenser', number=16, response=True)

    diagram.end_block()

    # ============================================================
    # Sektion 5: PULL/Federering
    # ============================================================
    diagram.add_section("5. Federerad beräkning via SPE – PULL (sammanställda resultat)")

    diagram.add_note_over('hubb', 'extern',
        "**Federering kan initieras av:**\n"
        "• Region (för egen återkoppling/benchmark)\n"
        "• Externa användare (via policy-gate)\n"
        "Rådata flyttas aldrig centralt – endast sammanställda delresultat.",
        color=COLORS['section_header']
    )

    diagram.start_block('alt', 'Alt A: Region/Hubb initierar federerad fråga', COLORS['alt_bg'])

    diagram.start_block('critical', 'Integritetskänsligt moment (data stannar regionalt)', COLORS['critical_bg'])
    diagram.add_message('hubb', 'spe', 'Startar federerad körning (Q1/Q2/Q3 + period)', number=17)
    diagram.add_message('spe', 'region', 'Federerad fråga + urval', number=18)
    diagram.add_message('region', 'region', 'Kör lokalt (data stannar i regionen)', number=19, self_message=True)
    diagram.add_message('region', 'spe', 'Returnerar sammanställda delresultat', number=20, response=True)
    diagram.add_message('spe', 'hubb', 'Slår ihop och lämnar sammanställning', number=21, response=True)
    diagram.end_block()

    diagram.add_message('hubb', 'region', 'Återkoppling baserat på federerat resultat', number=22)

    diagram.add_else_divider('Alt B: Extern initierar federerad fråga (via policy-gate)')

    diagram.start_block('critical', 'Extern begär federerad analys (godkänd process krävs)', COLORS['critical_bg'])
    diagram.add_message('extern', 'hubb', 'Begär federerad analys', number=23)
    diagram.add_message('hubb', 'hubb', 'Policy-gate (behörighet, små-talsskydd)', number=24, self_message=True)
    diagram.add_message('hubb', 'spe', 'Startar federerad körning', number=25)
    diagram.add_message('spe', 'region', 'Federerad fråga + urval', number=26)
    diagram.add_message('region', 'region', 'Kör lokalt (data stannar i regionen)', number=27, self_message=True)
    diagram.add_message('region', 'spe', 'Delresultat (endast sammanställning)', number=28, response=True)
    diagram.add_message('spe', 'hubb', 'Sammanställt resultat', number=29, response=True)
    diagram.end_block()

    diagram.add_message('hubb', 'extern', 'Levererar sammanställt resultat', number=30, response=True)

    diagram.add_note_over('hubb', 'extern',
        "**Extern får endast sammanställt resultat enligt policy.**\n"
        "Ingen åtkomst till individdata eller rådata.",
        color=COLORS['note_danger']
    )

    diagram.end_block()

    # ============================================================
    # Sektion 6: Sammanfattning externa användare
    # ============================================================
    diagram.add_section("6. Externa användare (sammanfattning)")

    diagram.add_note_over('sos', 'extern',
        "**Socialstyrelsen (SoS)**\n"
        "• Mottar: Väntetider + PAR (krypterade via push)\n"
        "• Kan begära: Federerade analyser (via pull/policy-gate)\n\n"
        "**Övriga externa (forskning, jämförelsetjänster)**\n"
        "• Mottar: Krypterade leveranser (om avtal finns)\n"
        "• Kan begära: Federerade analyser (via pull/policy-gate)\n\n"
        "**Gemensamt:** Hubben ser aldrig innehållet i krypterade leveranser.",
        color=COLORS['externa_box']
    )

    # Slutför
    diagram.add_spacer(2)
    diagram.finalize()

    return diagram


def main():
    """Huvudfunktion"""
    # Skapa output-katalog
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(output_dir, '..', '..', 'exports', 'python')
    os.makedirs(output_dir, exist_ok=True)

    # Skapa diagrammet
    print("Skapar sekvensdiagram...")
    diagram = create_regiongemensam_hubb_diagram()

    # Spara som PNG och SVG
    png_path = os.path.join(output_dir, 'regiongemensam-hubb-sekvens.png')
    svg_path = os.path.join(output_dir, 'regiongemensam-hubb-sekvens.svg')

    diagram.save(png_path, dpi=150)
    diagram.save(svg_path)

    print(f"\nDiagram sparade i: {output_dir}")
    print(f"  - {os.path.basename(png_path)}")
    print(f"  - {os.path.basename(svg_path)}")

    # Visa diagrammet (valfritt)
    # diagram.show()


if __name__ == '__main__':
    main()
