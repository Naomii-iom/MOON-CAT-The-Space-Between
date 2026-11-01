"""MOON CAT: THE SPACE BETWEEN — meteorite tile art build.

Puzzle rules, maps, controls, collision and saves remain those of Guided v1.0.
The user-provided backgrounds, cat frames and meteorite tiles load once at startup.
"""
from collections import deque
import json
import math
import random
from array import array
from pathlib import Path

import pygame
from art_assets import CatMotion, CatSprites, WorldBackgrounds, WorldTransition
from tile_art import MeteoriteTiles

pygame.mixer.pre_init(44100, -16, 1, 256)
pygame.init()

WIDTH, HEIGHT = 1060, 735
FPS = 60
NOTICE_FADE_IN_FRAMES = 12
NOTICE_HOLD_FRAMES = 138
NOTICE_FADE_OUT_FRAMES = 42
NOTICE_TOTAL_FRAMES = NOTICE_FADE_IN_FRAMES + NOTICE_HOLD_FRAMES + NOTICE_FADE_OUT_FRAMES
TILE = 54
COLS, ROWS = 15, 9
OX, OY = 50, 145
FLOAT_TILES_ENABLED = True
FLOAT_TILES_AMPLITUDE = 1.5
FLOAT_TILES_PERIOD_SECONDS = 3.4
SAVE_FILE = Path(__file__).resolve().with_name("mooncat-progress.json")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOON CAT  |  The Space Between")
clock = pygame.time.Clock()

ART_ROOT = Path(__file__).resolve().parent / "assets"
BOARD_RECT = pygame.Rect(OX-13, OY-13, COLS*TILE+26, ROWS*TILE+26)
BOARD_VIGNETTE_RECT = BOARD_RECT.inflate(140, 100)


def make_board_vignette(size):
    """Cached soft superellipse: darkens detail without drawing a panel edge."""
    small = pygame.Surface((120, 76), pygame.SRCALPHA)
    width, height = small.get_size()
    for y in range(height):
        dy = abs((y + 0.5) / height * 2 - 1)
        for x in range(width):
            dx = abs((x + 0.5) / width * 2 - 1)
            distance = (dx**4 + dy**4) ** 0.25
            fade = max(0.0, min(1.0, (1.0 - distance) / 0.28))
            fade = fade * fade * (3.0 - 2.0 * fade)
            small.set_at((x, y), (4, 7, 20, round(76 * fade)))
    return pygame.transform.smoothscale(small, size).convert_alpha()


BOARD_VIGNETTE = make_board_vignette(BOARD_VIGNETTE_RECT.size)
BACKGROUNDS = WorldBackgrounds(
    ART_ROOT / "backgrounds" / "moonlight.png",
    ART_ROOT / "backgrounds" / "shadow.png",
    (WIDTH, HEIGHT),
    BOARD_RECT,
)
CAT_SPRITES = CatSprites(ART_ROOT / "characters" / "cat", display_size=(74, 60))
METEORITE_TILES = MeteoriteTiles(
    ART_ROOT / "tiles" / "meteorites",
    TILE,
    floating_enabled=FLOAT_TILES_ENABLED,
    float_amplitude=FLOAT_TILES_AMPLITUDE,
    float_period_seconds=FLOAT_TILES_PERIOD_SECONDS,
)

# Room 3's pushable stone uses the user-provided artwork.  Crop and scale it
# once during startup; the puzzle still uses the original grid coordinate and
# collision rules.
_room3_stone_source = pygame.image.load(
    ART_ROOT / "objects" / "room3_stone.png"
).convert_alpha()
_room3_stone_bounds = _room3_stone_source.get_bounding_rect(min_alpha=8)
_room3_stone_size = _room3_stone_bounds.size
_room3_stone_limit = TILE - 6
_room3_stone_scale = min(
    _room3_stone_limit / _room3_stone_size[0],
    _room3_stone_limit / _room3_stone_size[1],
)
ROOM3_STONE_SPRITE = pygame.transform.scale(
    _room3_stone_source.subsurface(_room3_stone_bounds),
    tuple(max(1, round(value * _room3_stone_scale)) for value in _room3_stone_size),
)
WORLD_TRANSITION = WorldTransition((WIDTH, HEIGHT), duration_ms=520)


def font(size, bold=False):
    for name in ("Menlo", "DejaVu Sans Mono", "Avenir Next", "Arial"):
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    return pygame.font.Font(None, size)

F12, F14, F16, F20, F26, F34, F54 = [font(s, s in (20, 26, 34, 54)) for s in (12, 14, 16, 20, 26, 34, 54)]
WHITE = (236, 240, 255)
MUTED = (149, 159, 189)
DARK = (12, 16, 35)
LIGHT = (104, 215, 243)
SHADOW = (247, 132, 176)
GOLD = (255, 220, 133)


def line(x1, x2, y):
    return {(x, y) for x in range(x1, x2 + 1)}


def column(x, y1, y2):
    return {(x, y) for y in range(y1, y2 + 1)}


def room(name, subtitle, story, moon, shade, start, exit_at, exit_world,
         plate=None, plate_world=0, gate=None, gate_world=1,
         stone=None, lantern=None, bridge=None, memory=None, tips=()):
    return dict(name=name, subtitle=subtitle, story=story,
                floors=(moon, shade), start=start, exit=exit_at,
                exit_world=exit_world, plate=plate, plate_world=plate_world,
                gate=gate, gate_world=gate_world, stone=stone,
                lantern=lantern, bridge=set(bridge or []),
                memory=memory, tips=tips)


ROOMS = [
    room(
        "01 / THE MISSING STEP", "A doorway exists in both worlds. The path does not.",
        "One world ends where the other begins.",
        line(1, 6, 4) | line(8, 9, 4) | column(9, 2, 4) |
        line(9, 13, 2) | column(2, 4, 6) | line(1, 3, 6),
        line(1, 3, 4) | line(5, 10, 4) | column(2, 4, 6),
        (2, 6), (13, 2), 0,
        memory=(0, 1, 6),
        tips=("A wall in one world may be a road in another.",
              "Reach the gap in BLUE. Press Q. Continue in PINK, then press Q again near x=9."),
    ),
    room(
        "02 / SOMEONE MUST STAY", "A door needs a friend on the other side.",
        "When you leave, something of you remains.",
        line(1, 6, 4) | column(2, 4, 6),
        line(1, 11, 4) | column(2, 4, 6) | column(11, 2, 4) | line(11, 13, 2),
        (2, 6), (13, 2), 1,
        plate=(5, 4), plate_world=0, gate=(7, 4), gate_world=1,
        memory=(1, 1, 4),
        tips=("The BLUE pressure plate can open a PINK door. But who will stand on it?",
              "Stand on the blue plate at x=5, y=4. Press Q to leave an ECHO there. Cross the pink gate."),
    ),
    room(
        "03 / THE STONE'S SHADOW", "Some things have weight across worlds.",
        "Push here; another world remembers.",
        line(1, 7, 4) | column(2, 4, 6) | line(1, 3, 5),
        line(1, 6, 4) | line(10, 12, 4) | column(2, 4, 6) |
        column(12, 2, 4) | line(12, 13, 2),
        (2, 6), (13, 2), 1,
        plate=(6, 4), plate_world=0, stone=(4, 4),
        bridge={(7, 4), (8, 4), (9, 4)}, memory=(0, 1, 5),
        tips=("Push Moonlight stones with your body.",
              "Push right onto the plate. Then press Q."),
    ),
    room(
        "04 / A LIGHT LEFT BEHIND", "Two actions, two worlds, one way through.",
        "Light the lamp, then leave an Echo.",
        line(1, 6, 4) | column(2, 4, 6),
        line(1, 8, 4) | line(10, 13, 4) | column(2, 4, 6) | column(11, 2, 4) | line(11, 13, 2),
        (2, 6), (13, 2), 1,
        plate=(5, 4), plate_world=0, gate=(7, 4), gate_world=1,
        lantern=(3, 3), bridge={(9, 4)}, memory=(1, 13, 4),
        tips=("The lamp builds; Echo holds.",
              "Light the lamp. Echo the plate. Cross."),
    ),
    room(
        "05 / THE SPACE BETWEEN", "The echo can hold a door for YOU.",
        "Leave an Echo to open the final gate.",
        line(1, 6, 4) | line(8, 13, 4) | column(2, 4, 6) | column(12, 4, 6),
        line(1, 3, 4) | line(5, 9, 4) | column(2, 4, 6),
        (2, 6), (13, 4), 0,
        plate=(8, 4), plate_world=1, gate=(11, 4), gate_world=0,
        memory=(0, 12, 6),
        tips=("The Shadow plate opens Moonlight's gate.",
              "Reach Shadow's plate. Press Q. Exit right."),
    ),
]


# The first thing players see in every new room: intent, rules, and a plan.
# The details are deliberately clear; discovering the execution is still fun.
GUIDES = [
    {
        "title": "01 / THE MISSING STEP", "goal": "Reach the glowing exit.",
        "steps": [
            "Walk to the Moonlight path's gap.",
            "Press Q. A Shadow path appears here.",
            "Cross, then press Q near the upper path.",
        ],
        "rule": "Shift only where both worlds share ground.",
        "short": "Reach the gap, then press Q.",
    },
    {
        "title": "02 / SOMEONE MUST STAY", "goal": "Open the Shadow gate.",
        "steps": [
            "Step onto the Moonlight pressure plate.",
            "Press Q there to leave an Echo.",
            "Cross before the Echo fades.",
        ],
        "rule": "Echo holds the plate for ten moves.",
        "short": "Press Q on the plate, then cross.",
    },
    {
        "title": "03 / THE STONE'S SHADOW", "goal": "Create the Shadow bridge.",
        "steps": [
            "Stand left of the Moonlight stone.",
            "Push right until it reaches the plate.",
            "Press Q, then cross the new bridge.",
        ],
        "rule": "The stone powers a bridge across worlds.",
        "short": "Push the stone right, then press Q.",
    },
    {
        "title": "04 / A LIGHT LEFT BEHIND", "goal": "Light the bridge and open the gate.",
        "steps": [
            "Press E beside the Moonlight lamp.",
            "Then reach the pressure plate.",
            "Press Q and cross before Echo fades.",
        ],
        "rule": "The lamp builds; Echo holds.",
        "short": "Light the lamp, then Echo the plate.",
    },
    {
        "title": "05 / THE SPACE BETWEEN", "goal": "Open the Moonlight gate.",
        "steps": [
            "Reach the right Moonlight gap.",
            "Press Q and find the Shadow plate.",
            "Press Q there, then reach the exit.",
        ],
        "rule": "A Shadow Echo opens Moonlight's gate.",
        "short": "Leave Echo on the Shadow plate.",
    },
]

KEY_LABELS = {"left": "A / LEFT", "right": "D / RIGHT", "up": "W / UP",
              "down": "S / DOWN", "q": "Q / SHIFT", "e": "E / USE"}


def guide_goal(s):
    """Contextual, non-spoiler task and one glowing board target."""
    if s.index == 0:
        if s.world == 0 and s.player[0] < 6:
            return "Reach the Moonlight gap. Press Q.", (6, 4), 0
        if s.world == 1:
            return "Follow Shadow right. Press Q near the steps.", (9, 4), 1
        return "Climb toward the glowing exit.", s.level["exit"], 0
    if s.index == 1:
        if s.world == 0:
            return ("Press Q to leave Echo here." if s.player == s.level["plate"]
                    else "Step onto the Moonlight plate."), s.level["plate"], 0
        if not s.plate_on():
            return "Return to the plate. Press Q.", s.level["plate"], 0
        return "Echo is fading. Cross the gate.", s.level["gate"], 1
    if s.index == 2:
        if not s.plate_on():
            if s.world == 1:
                return "Return to Moonlight. Push the stone.", s.level["plate"], 0
            return "Push the stone right onto the plate.", s.level["plate"], 0
        if s.world == 0:
            return "Bridge ready. Press Q.", s.level["plate"], 0
        return "Cross the bridge toward the exit.", s.level["exit"], 1
    if s.index == 3:
        if not s.lit:
            return ("Return to Moonlight. Light the lamp." if s.world == 1
                    else "Press E beside the lamp."), s.level["lantern"], 0
        if s.world == 0:
            return "Press Q while standing on the plate.", s.level["plate"], 0
        return "Bridge ready. Move right.", s.level["exit"], 1
    if s.world == 0:
        if s.plate_on():
            return "Echo holds the gate. Reach the exit.", s.level["exit"], 0
        return "Reach the gap. Press Q.", (5, 4), 0
    return "Press Q while standing on the plate.", s.level["plate"], 1


def solution_hint(state):
    """Compute a real next move from the CURRENT puzzle state, not a canned answer."""
    actions = ("up", "right", "down", "left", "q", "e")
    queue = deque([(state.copy(), None, 0)])
    visited = set()
    while queue and len(visited) < 35000:
        candidate, first_move, length = queue.popleft()
        key = (candidate.player, candidate.world, candidate.stone,
               candidate.lit, candidate.echo)
        if key in visited:
            continue
        visited.add(key)
        if candidate.exit_reached():
            return first_move, length
        for act in actions:
            nxt = candidate.copy()
            changed, _, _, _ = execute(nxt, act)
            if changed:
                queue.append((nxt, act if first_move is None else first_move, length+1))
    return None, 0



class State:
    def __init__(self, room_index):
        self.index = room_index
        self.level = ROOMS[room_index]
        self.player = self.level["start"]
        self.world = 0
        self.stone = self.level["stone"]
        self.lit = False
        self.echo = None  # (world, x, y, remaining player moves)
        self.memory = False
        self.moves = 0

    def copy(self):
        # Level maps are read-only, so a shallow snapshot is enough.
        new = object.__new__(State)
        new.__dict__ = self.__dict__.copy()
        return new

    def floor(self, point, world):
        return (point in self.level["floors"][world] or
                (world == 1 and point in self.level["bridge"] and self.bridge_on()))

    def plate_on(self):
        p = self.level["plate"]
        if p is None:
            return False
        w = self.level["plate_world"]
        # The stone puzzle requires the stone itself, not a passing cat.
        if self.index == 2:
            return self.stone == p
        if self.stone == p and w == 0:
            return True
        if self.world == w and self.player == p:
            return True
        if self.echo and self.echo[0] == w and self.echo[1:3] == p and self.echo[3] > 0:
            return True
        return False

    def bridge_on(self):
        # In room 3 the stone creates a bridge; in room 4 a lantern does.
        if self.index == 2:
            return self.stone == self.level["plate"]
        return self.lit

    def passable(self, at, world):
        if not self.floor(at, world):
            return False
        if at == self.level["gate"] and world == self.level["gate_world"]:
            return self.plate_on()
        return True

    def exit_reached(self):
        return self.player == self.level["exit"] and self.world == self.level["exit_world"]

    def collect(self):
        m = self.level["memory"]
        if m and not self.memory and (self.world, *self.player) == m:
            self.memory = True
            return True
        return False


def execute(state, action):
    """Pure puzzle rules. Returns (changed, feedback, completed, collected)."""
    if action == "q":
        w = 1 - state.world
        if not state.passable(state.player, w):
            return False, "That spot is solid elsewhere. Move first.", False, False
        state.echo = (state.world, *state.player, 10)
        state.world = w
        collected = state.collect()
        return True, "Echo stays here for ten moves.", state.exit_reached(), collected

    if action == "e":
        lamp = state.level["lantern"]
        if (lamp and state.world == 0 and not state.lit and
                abs(state.player[0]-lamp[0]) + abs(state.player[1]-lamp[1]) <= 1):
            state.lit = True
            return True, "A light in BLUE creates a bridge in PINK!", False, False
        return False, "There is nothing to activate here.", False, False

    offsets = {"up": (0, -1), "down": (0, 1), "left": (-1, 0), "right": (1, 0)}
    if action not in offsets:
        return False, "", False, False
    dx, dy = offsets[action]
    nx, ny = state.player[0] + dx, state.player[1] + dy
    target = (nx, ny)
    if state.world == 0 and target == state.stone:
        pushed = (nx + dx, ny + dy)
        if state.index == 2:
            # Prevent the soft-lock seen in playtesting: stone can no longer
            # be pushed past the plate or into a corner with no way back.
            if state.stone == state.level["plate"]:
                return False, "Stone locked. Press Q.", False, False
            if dx != 1 or pushed[0] > state.level["plate"][0]:
                return False, "Push from the left toward the plate.", False, False
        if not state.floor(pushed, 0) or pushed == state.level["gate"]:
            return False, "The stone cannot move that way.", False, False
        state.stone = pushed
    elif not state.passable(target, state.world):
        if target == state.level["gate"]:
            return False, "The door needs pressure from the OTHER world.", False, False
        if target in state.level["bridge"]:
            return False, "Bridge missing. Find its trigger.", False, False
        return False, "No path here. Look at the other world's map.", False, False
    state.player = target
    state.moves += 1
    if state.echo:
        w, x, y, count = state.echo
        count -= 1
        state.echo = (w, x, y, count) if count > 0 else None
    collected = state.collect()
    return True, "A hidden memory found!" if collected else "", state.exit_reached(), collected


# -- Progress is saved alongside the game, not inside any school repository. --
def load_progress():
    try:
        data = json.loads(SAVE_FILE.read_text(encoding="utf-8"))
        unlocked = max(1, min(len(ROOMS), int(data.get("unlocked", 1))))
        secrets = {int(x) for x in data.get("memories", []) if 0 <= int(x) < len(ROOMS)}
        return unlocked, secrets
    except (FileNotFoundError, ValueError, TypeError, OSError):
        return 1, set()


def save_progress():
    try:
        SAVE_FILE.write_text(json.dumps({"unlocked": unlocked, "memories": sorted(memories)}), encoding="utf-8")
    except OSError:
        pass


unlocked, memories = load_progress()
current = State(0)
mode = "menu"       # menu, play, clear, finished
history = []
notice = ""
notice_ttl = 0
notice_duration = 0
hint_level = 0
guide_open = False
hint_text = ""
transition = 0
phase_flash = 0
shakes = 0
particles = []
stars = [(random.randrange(WIDTH), random.randrange(HEIGHT), random.random()*1.6+.5, random.random()*2*math.pi) for _ in range(115)]


def sound_tone(hz, duration=0.12, amp=0.13):
    try:
        if not pygame.mixer.get_init():
            return None
        sr = 44100
        samples = array("h", [
            int(32767 * amp * math.sin(2*math.pi*hz*i/sr) * (1 - i / max(1, int(sr*duration))))
            for i in range(int(sr*duration))
        ])
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except (pygame.error, ValueError):
        return None


SOUNDS = {k: sound_tone(freq, length) for k, freq, length in [
    ("step", 220, .055), ("shift", 590, .18), ("push", 155, .13),
    ("error", 132, .16), ("gem", 880, .28), ("win", 740, .4),
    ("lamp", 440, .3)]}


def sound(key):
    s = SOUNDS.get(key)
    if s:
        s.play()


def message(msg, frames=160):
    global notice, notice_ttl, notice_duration
    frames = NOTICE_TOTAL_FRAMES
    notice, notice_ttl, notice_duration = msg, frames, frames


def begin(index):
    global current, mode, hint_level, history, particles, transition, notice_ttl, notice_duration
    global guide_open, hint_text
    current = State(index)
    history = []
    particles = []
    transition = 0
    hint_level = 0
    hint_text = ""
    guide_open = True  # Every room first opens with an explicit walkthrough.
    notice_ttl = 0
    notice_duration = 0
    mode = "play"
    WORLD_TRANSITION.cancel()
    CAT_MOTION.reset(tile_center(current.player), "down")
    message(current.level["story"], 230)


def spark_at(point, count=22):
    x, y = tile_center(point)
    for _ in range(count):
        angle = random.random()*math.tau
        speed = random.uniform(1, 4)
        particles.append([x, y, math.cos(angle)*speed, math.sin(angle)*speed, random.randint(20, 43)])


def player_action(action):
    global mode, unlocked, hint_level, phase_flash, shakes, hint_text
    if mode != "play":
        return
    if action in ("up", "right", "down", "left"):
        CAT_MOTION.facing = action
    old = current.copy()
    old_frame = screen.copy() if action == "q" else None
    prevstone = current.stone
    changed, feedback, completed, collected = execute(current, action)
    if changed:
        if hint_level >= 3:
            hint_text = "Progress made. Press H for another hint."
        else:
            hint_text = ""
        history.append(old)
        history[:] = history[-120:]
        if action == "q":
            phase_flash = 0
            WORLD_TRANSITION.start(
                old_frame,
                visual_tile_center(current.player),
                old.world,
                current.world,
            )
            sound("shift")
        elif action == "e":
            sound("lamp")
        elif prevstone != current.stone:
            sound("push")
            spark_at(current.stone, 8)
        else:
            sound("step")
        if action in ("up", "right", "down", "left") and old.player != current.player:
            CAT_MOTION.start_move(tile_center(current.player), action)
        if collected:
            memories.add(current.index)
            save_progress()
            spark_at(current.player, 30)
            sound("gem")
        # Player receives meaningful visual + text feedback when a cross-world
        # dependency is solved, not just an invisible boolean update.
        if current.index == 2 and not old.plate_on() and current.plate_on():
            message("Stone locked. Shadow bridge ready.")
            spark_at(current.stone, 42)
        elif current.index == 3 and not old.lit and current.lit:
            message("Lamp lit. Shadow bridge ready.")
        elif (action == "q" and current.echo is not None and
              current.level["plate"] == current.echo[1:3] and current.plate_on()):
            message("Echo holds the plate. Gate open.")
        elif collected:
            message("Hidden memory found!")
        elif feedback:
            message(feedback, 145)
        if completed:
            spark_at(current.player, 70)
            sound("win")
            unlocked = max(unlocked, min(len(ROOMS), current.index + 2))
            save_progress()
            mode = "clear" if current.index < len(ROOMS)-1 else "finished"
    else:
        if feedback:
            message(feedback, 135)
        if action not in ("e",):
            shakes = 5
            sound("error")


def put_text(text, x, y, f=F16, color=WHITE, center=False):
    img = f.render(str(text), True, color)
    rect = img.get_rect(center=(x,y)) if center else img.get_rect(topleft=(x,y))
    screen.blit(img, rect)
    return rect


def rounded(rect, fill, rad=12, border=None, width=1):
    pygame.draw.rect(screen, fill, rect, border_radius=rad)
    if border:
        pygame.draw.rect(screen, border, rect, width, border_radius=rad)


def tile_center(point):
    return (OX + point[0]*TILE + TILE//2, OY + point[1]*TILE + TILE//2)


def tile_bob(point, now_ms=None):
    """Presentation-only integer offset for the current room's floating road."""
    return METEORITE_TILES.pixel_offset(current.index, point, current.level, now_ms)


def visual_tile_center(point, now_ms=None):
    x, y = tile_center(point)
    return (x, y + tile_bob(point, now_ms))


CAT_MOTION = CatMotion(duration_ms=150)
CAT_MOTION.reset(tile_center(current.player), "down")


def pill(x, y, text, active=False, color=LIGHT):
    width = max(80, F14.size(text)[0]+26)
    rounded((x,y,width,28), (40,65,80) if active else (30,34,58), 14,
            color if active else (66,74,110))
    put_text(text,x+width/2,y+14,F14,WHITE if active else MUTED,True)
    return width


def draw_cat(x, y, tint):
    """Compatibility helper for menu/echo positions from Guided v1.0."""
    echo = tint == (130,117,206)
    CAT_SPRITES.draw(
        screen,
        (x, y + 18),
        "down",
        False,
        pygame.time.get_ticks(),
        alpha=112 if echo else 255,
        tint=(24, 8, 72) if echo else None,
    )


def world_palette(world):
    if world == 0:
        return dict(accent=LIGHT, fill=(36,72,98), solid=(23,38,68), edge=(87,164,202), bg=(10,22,43))
    return dict(accent=SHADOW, fill=(91,49,86), solid=(47,25,55), edge=(182,97,149), bg=(35,18,42))


def draw_board():
    s = current
    p = world_palette(s.world)
    brect = BOARD_RECT
    screen.blit(BOARD_VIGNETTE, BOARD_VIGNETTE_RECT)
    now_ms = pygame.time.get_ticks()
    now = now_ms/1000
    shake_x = random.randint(-2,2) if shakes else 0
    for y in range(ROWS):
        for x in range(COLS):
            at=(x,y)
            px=OX+x*TILE + shake_x
            py=OY+y*TILE
            inside=s.floor(at,s.world)
            bob = METEORITE_TILES.pixel_offset(s.index, at, s.level, now_ms)
            if inside:
                kind = METEORITE_TILES.kind_for(s.index, at, s.world, s.level)
                METEORITE_TILES.draw(screen, (px, py), s.world, kind, bob)
            elif s.floor(at,1-s.world):
                # Other-world-only paths stay non-solid: only a faint cached
                # meteorite silhouette is shown, never a walkable-looking tile.
                other_world = 1-s.world
                kind = METEORITE_TILES.kind_for(s.index, at, other_world, s.level)
                METEORITE_TILES.draw_preview(screen, (px, py), other_world, kind, bob)

    # In-game guide marker: a pulsing ring is drawn on the next relevant tile.
    task, target, target_world = guide_goal(s)
    if target and target_world == s.world:
        hx,hy=visual_tile_center(target, now_ms)
        radius=24 + int(3*math.sin(now*4))
        pygame.draw.circle(screen,GOLD,(hx,hy),radius,2)
        pygame.draw.circle(screen,GOLD,(hx,hy),radius+6,1)

    # Bridges, door, plate, lamp, stone, echo, secret, portal, player
    if s.world == 1:
        for at in s.level["bridge"]:
            xx, yy=visual_tile_center(at, now_ms)
            if s.bridge_on():
                rounded((xx-18,yy-17,36,34),(158,101,153),8,(251,171,208),2)
                pygame.draw.line(screen,(255,195,222),(xx-14,yy),(xx+14,yy),2)
            else:
                pygame.draw.line(screen,(126,73,104),(xx-18,yy-10),(xx+18,yy+10),2)
                pygame.draw.line(screen,(126,73,104),(xx-18,yy+10),(xx+18,yy-10),2)

    gate=s.level["gate"]
    if gate is not None and s.world == s.level["gate_world"]:
        x,y=visual_tile_center(gate, now_ms)
        if s.plate_on():
            pygame.draw.circle(screen,(130,235,174),(x,y),15,3)
            pygame.draw.line(screen,(130,235,174),(x-6,y),(x-1,y+5),3)
            pygame.draw.line(screen,(130,235,174),(x-1,y+5),(x+8,y-7),3)
        else:
            rounded((x-17,y-20,34,40),(185,79,114),7,(255,190,200),2)
            for xx in range(x-10,x+12,9):
                pygame.draw.line(screen,(63,28,60),(xx,y-16),(xx,y+16),3)

    plate=s.level["plate"]
    if plate is not None and s.world == s.level["plate_world"]:
        x,y=visual_tile_center(plate, now_ms)
        activated=s.plate_on()
        c=(125,240,165) if activated else GOLD
        rounded((x-17,y-9,34,20),(38,51,68),7,c,3)
        pygame.draw.circle(screen,c,(x,y),4)
        if activated:
            pygame.draw.circle(screen,c,(x,y),20 + int(2*math.sin(now*4)),2)
        elif s.index in (1,2,3,4):
            put_text("!",x,y-31,F14,GOLD,True)

    lamp=s.level["lantern"]
    if lamp and s.world==0:
        x,y=visual_tile_center(lamp, now_ms)
        c=GOLD if s.lit else (102,103,127)
        pygame.draw.circle(screen,c,(x,y),13)
        pygame.draw.line(screen,(190,200,210),(x,y+12),(x,y+22),3)
        if s.lit:
            pygame.draw.circle(screen,(247,201,102),(x,y),20 + int(2*math.sin(now*3)),2)
        else:
            put_text("E",x+13,y-22,F12,MUTED,True)

    if s.stone is not None:
        x,y=visual_tile_center(s.stone, now_ms)
        if s.world==0:
            stone_rect = ROOM3_STONE_SPRITE.get_rect(center=(x, y-1))
            screen.blit(ROOM3_STONE_SPRITE, stone_rect)
        else:
            pygame.draw.circle(screen,(110,77,108),(x,y),12,1)

    if s.echo and s.echo[0]==s.world:
        w,x,y,ttl=s.echo
        cx,cy=visual_tile_center((x,y), now_ms)
        draw_cat(cx,cy,(130,117,206))
        pygame.draw.circle(screen,(200,165,255),(cx,cy),22,1)
        put_text(str(ttl),cx,cy+26,F12,(225,183,246),True)

    m=s.level["memory"]
    if m and m[0]==s.world and not s.memory:
        x,y=visual_tile_center(m[1:], now_ms)
        pulse=math.sin(now*4)*3
        pygame.draw.circle(screen,(252,211,124),(x,y),8+int(pulse),2)
        pygame.draw.circle(screen,WHITE,(x,y),4)

    ex=s.level["exit"]
    if s.world==s.level["exit_world"]:
        x,y=visual_tile_center(ex, now_ms)
        rad=16 + int(math.sin(now*3)*2)
        pygame.draw.circle(screen,p["accent"],(x,y),rad,3)
        pygame.draw.circle(screen,(224,245,255),(x,y),7)
    else:
        # subtle compass hint: the goal is in the other world
        pass

    x,y=CAT_MOTION.position(now_ms)
    y += tile_bob(s.player, now_ms)
    pygame.draw.ellipse(screen, (8,10,27), (round(x-17),round(y+11),34,10))
    CAT_SPRITES.draw(
        screen,
        (x, y + 18),
        CAT_MOTION.facing,
        CAT_MOTION.moving,
        pygame.time.get_ticks(),
    )
    pygame.draw.circle(screen,p["accent"],(round(x),round(y)),23,1)
    return brect


def draw_mini_world(x0,y0,w):
    s=current
    off=1-s.world
    p=world_palette(off)
    put_text("OTHER WORLD  /  " + ("MOONLIGHT" if off==0 else "SHADOW"),x0,y0,F12,MUTED)
    scale=w/(COLS+1)
    px0=x0+scale/2
    yy=y0+26
    for y in range(ROWS):
        for x in range(COLS):
            pt=(x,y)
            valid=s.floor(pt,off)
            v=(x0+scale*(x+.45),yy+scale*y)
            if valid:
                fill=p["fill"]
                pygame.draw.rect(screen,fill,(*v,scale-2,scale-2),border_radius=2)
    pt=s.level["plate"]
    if pt and off==s.level["plate_world"]:
        x,y=pt
        pygame.draw.circle(screen,GOLD,(int(px0+scale*x),int(yy+scale*y+scale/2)),3)
    gate=s.level["gate"]
    if gate and off==s.level["gate_world"]:
        x,y=gate
        pygame.draw.rect(screen,(111,216,160) if s.plate_on() else SHADOW,
                         (x0+scale*(x+.45),yy+scale*y,scale-2,scale-2))
    if s.echo and s.echo[0]==off:
        _,ex,ey,ttl = s.echo
        pygame.draw.circle(screen,SHADOW,(int(px0+scale*ex),int(yy+scale*ey+scale/2)),5,2)
    xx,yy0=s.player
    pygame.draw.circle(screen,WHITE,(int(px0+scale*xx),int(yy+scale*yy0+scale/2)),3,1)
    _,target,target_world=guide_goal(s)
    if target and target_world==off:
        tx,ty=target
        pygame.draw.circle(screen,GOLD,
                           (int(px0+scale*tx),int(yy+scale*ty+scale/2)),7,2)


def draw_backdrop():
    if mode != "menu":
        BACKGROUNDS.draw_scene(screen, current.world)
        return
    screen.fill((9,13,29))
    now=pygame.time.get_ticks()/1000
    for x,y,r,offset in stars:
        twinkle=140+int(80*math.sin(now*1.7+offset))
        pygame.draw.circle(screen,(twinkle//2,twinkle//2,twinkle),(x,y),max(1,int(r)))
    pygame.draw.circle(screen,(27,39,72),(1043,35),200)
    pygame.draw.circle(screen,(48,50,85),(1050,42),155,2)


def draw_play():
    draw_backdrop()
    draw_board()
    draw_play_ui()


def draw_floating_prompt(text, y, alpha=255, font_obj=F16, colour=(255, 232, 184)):
    """Centered text with only a restrained shadow—never a panel or tab."""
    if not text or alpha <= 0:
        return
    image = font_obj.render(str(text), True, colour)
    image.set_alpha(alpha)
    shadow = font_obj.render(str(text), True, (5, 8, 20))
    shadow.set_alpha(round(alpha * 0.7))
    rect = image.get_rect(center=(WIDTH // 2, y))
    screen.blit(shadow, rect.move(2, 2))
    screen.blit(image, rect)


def draw_play_ui():
    """Minimal full-screen HUD; the enlarged board remains the visual focus."""
    s=current
    p=world_palette(s.world)
    put_text(s.level["name"],34,28,F16,WHITE)
    pill(309,52,"MOONLIGHT",s.world==0,LIGHT)
    pill(408,52,"SHADOW",s.world==1,SHADOW)
    put_text("Q  SHIFT",510,59,F14,p["accent"])

    # Echo steps are a small, shape-neutral HUD, visually separate from tiles.
    echo_hud=pygame.Surface((150,58),pygame.SRCALPHA)
    pygame.draw.rect(echo_hud,(5,9,24,128),echo_hud.get_rect(),border_radius=13)
    ttl=s.echo[3] if s.echo else None
    echo_hud.blit(F12.render("ECHO",True,MUTED),(12,9))
    number=F26.render(f"{ttl:02d}" if ttl is not None else "--",True,SHADOW if ttl is not None else MUTED)
    echo_hud.blit(number,(48,14))
    echo_hud.blit(F12.render("/ 10",True,WHITE),(101,29))
    screen.blit(echo_hud,(625,24))

    # The other-world map stays compact and clear of the Echo counter.
    draw_mini_world(850,18,170)
    put_text(f"MEMORIES  {len(memories)} / 5",790,116,F12,GOLD)

    if notice_ttl > 0 and notice_duration > 0:
        elapsed=notice_duration-notice_ttl
        fade=min(
            1.0,
            elapsed/NOTICE_FADE_IN_FRAMES,
            notice_ttl/NOTICE_FADE_OUT_FRAMES,
        )
        draw_floating_prompt(notice[:50],681,round(255*fade),F14,(255,240,205))
    put_text("WASD move  ·  Q shift  ·  E interact  ·  G guide  ·  H hint  ·  Z undo  ·  R restart",
             WIDTH//2,710,F12,(173,182,204),True)



def draw_guide():
    """An in-game onboarding card, reopened with G at any time."""
    guide = GUIDES[current.index]
    mask=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    mask.fill((5,9,24,225))
    screen.blit(mask,(0,0))
    x,y,w,h=161,108,738,518
    rounded((x,y,w,h),(19,29,52),22,(103,171,201),2)
    # Connected-world diagram; colors mean gameplay states, not decoration.
    pygame.draw.circle(screen,LIGHT,(x+57,y+62),24,3)
    pygame.draw.circle(screen,SHADOW,(x+113,y+62),24,3)
    pygame.draw.line(screen,GOLD,(x+81,y+62),(x+90,y+62),3)
    put_text("ROOM GUIDE",x+154,y+49,F20,WHITE)
    put_text(guide["title"],x+45,y+108,F26,GOLD)
    put_text("GOAL  " + guide["goal"],x+45,y+160,F20,WHITE)
    for i,step in enumerate(guide["steps"]):
        yy=y+214+i*58
        pygame.draw.circle(screen,LIGHT if i%2==0 else SHADOW,(x+60,yy+11),17)
        put_text(str(i+1),x+60,yy+11,F20,(18,28,48),True)
        put_text(step,x+94,yy,F16,WHITE)
    rounded((x+40,y+409,w-80,45),(34,45,74),10)
    put_text("RULE: " + guide["rule"],x+53,y+421,F14,(193,218,237))
    rounded((x+160,y+468,w-320,40),(56,84,102),12,(113,202,222),1)
    put_text("ENTER START  /  G CLOSE",x+w/2,y+488,F16,WHITE,True)
    put_text("H HINT  ·  Z UNDO  ·  R RESTART",x+w/2,y+455,F14,MUTED,True)



def draw_overlay(head, description, action, note=""):
    overlay=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
    overlay.fill((6,9,23,203))
    screen.blit(overlay,(0,0))
    rounded((208,193,644,336),(19,28,49),24,(102,133,166),2)
    put_text(head,WIDTH/2,262,F54,GOLD,True)
    put_text(description,WIDTH/2,349,F20,WHITE,True)
    if note:
        put_text(note,WIDTH/2,391,F14,MUTED,True)
    rounded((347,442,366,55),(54,77,105),16,(106,202,218),1)
    put_text(action,WIDTH/2,468,F20,WHITE,True)


def draw_menu():
    draw_backdrop()
    t=pygame.time.get_ticks()/1000
    # Giant hand-drawn eclipse, world-shift symbolism
    pygame.draw.circle(screen,(38,60,104),(530,211),115)
    pygame.draw.circle(screen,(128,210,230),(530,211),93,3)
    pygame.draw.circle(screen,(200,105,145),(555+int(math.sin(t)*10),197),87)
    pygame.draw.circle(screen,(17,21,40),(566+int(math.sin(t)*10),188),78)
    draw_cat(529,229,(255,233,222))
    put_text("MOON CAT",WIDTH/2,373,F54,WHITE,True)
    put_text("T H E   S P A C E   B E T W E E N",WIDTH/2,421,F20,(160,196,221),True)
    put_text("Five handcrafted puzzle rooms. Two connected worlds.",WIDTH/2,465,F16,MUTED,True)
    rounded((322,517,416,61),(42,74,88),15,(101,213,229),2)
    put_text("PRESS ENTER TO BEGIN",WIDTH/2,548,F20,WHITE,True)
    put_text("A/W/S/D move   ·   Q shift worlds   ·   Z undo   ·   H hints",WIDTH/2,618,F14,MUTED,True)
    put_text(f"Unlocked: {unlocked}/5   •   Secrets: {len(memories)}/5",WIDTH/2,655,F14,GOLD,True)
    put_text("Choose unlocked room: 1  2  3  4  5",WIDTH/2,680,F14,MUTED,True)


def render():
    if mode=="menu":
        draw_menu()
    else:
        draw_play()
        if mode=="clear":
            draw_overlay("ROOM SOLVED", "The two worlds remember what you did.",
                         "ENTER  /  NEXT ROOM", f"Room {current.index+1} of {len(ROOMS)} complete  •  Z to replay not needed")
        elif mode=="finished":
            draw_overlay("YOU FOUND THE WAY", "Not by running faster — by thinking differently.",
                         "ENTER  /  BACK TO MENU", f"Hidden memories found: {len(memories)} / 5")
        elif mode=="play" and guide_open:
            draw_guide()
    # Tiny glow particles from puzzle completion
    for q in particles:
        x,y,vx,vy,ttl=q
        if ttl>0:
            pygame.draw.circle(screen,GOLD,(int(x),int(y)),max(1,ttl//13))
    if mode=="play" and WORLD_TRANSITION.is_active():
        WORLD_TRANSITION.draw(screen)
        # The landscapes and board crossfade, while interface text remains
        # single, crisp and immediately reflects the authoritative new world.
        draw_play_ui()
    pygame.display.flip()


# Used for held keys as well as discrete key events. No timer continues in the background.
pygame.key.set_repeat(190, 105)
running=True
while running:
    clock.tick(FPS)
    if notice_ttl>0:
        notice_ttl-=1
    if phase_flash>0:
        phase_flash-=1
    if shakes>0:
        shakes-=1
    for q in particles[:]:
        q[0]+=q[2]
        q[1]+=q[3]
        q[4]-=1
        if q[4]<=0:
            particles.remove(q)
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type!=pygame.KEYDOWN:
            continue
        k=event.key
        # Keyboard autorepeat is useful for walking, but not for swapping worlds.
        if getattr(event, "repeat", False) and k not in (
            pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_s,
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN
        ):
            continue
        if k==pygame.K_ESCAPE:
            WORLD_TRANSITION.cancel()
            if mode=="menu":
                running=False
            else:
                mode="menu"
            continue
        # Collision state changes at the start of a legal Q switch, then input
        # is held for the brief visual crossfade so display and rules cannot race.
        if WORLD_TRANSITION.is_active():
            continue
        if mode=="menu":
            if k in (pygame.K_RETURN,pygame.K_SPACE):
                begin(0)
            elif pygame.K_1<=k<=pygame.K_5:
                chosen=k-pygame.K_1
                if chosen<unlocked:
                    begin(chosen)
                else:
                    message("Solve earlier rooms to unlock this one.")
            continue
        if mode in ("clear","finished"):
            if k in (pygame.K_RETURN,pygame.K_SPACE):
                if mode=="finished":
                    mode="menu"
                else:
                    begin(current.index+1)
            elif k==pygame.K_r:
                begin(current.index)
            continue
        # Guides are an optional pause overlay: no accidental movement behind it.
        if k==pygame.K_g:
            guide_open = not guide_open
            continue
        if guide_open:
            if k in (pygame.K_RETURN, pygame.K_SPACE):
                guide_open = False
            elif k == pygame.K_h:
                guide_open = False
                hint_level = 0
                hint_text = "Guide closed. Press H for a hint."
            continue
        if k==pygame.K_r:
            begin(current.index)
        elif k==pygame.K_h:
            if hint_level == 0:
                hint_text = "HINT 1: " + GUIDES[current.index]["short"]
            elif hint_level == 1:
                hint_text = "HINT 2: " + GUIDES[current.index]["steps"][-1]
            else:
                move, distance = solution_hint(current)
                if move:
                    hint_text = f"NEXT: {KEY_LABELS[move]}. Press H again."
                else:
                    hint_text = "No route. Press Z or R."
            hint_level += 1
            message(hint_text, 180)
        elif k in (pygame.K_z, pygame.K_BACKSPACE):
            if history:
                current=history.pop()
                WORLD_TRANSITION.cancel()
                CAT_MOTION.reset(tile_center(current.player))
                sound("shift")
                message("One step back. Try another possibility.",100)
            else:
                message("Nothing to undo yet.")
        elif k==pygame.K_q:
            player_action("q")
        elif k==pygame.K_e:
            player_action("e")
        elif k in (pygame.K_a,pygame.K_LEFT):
            player_action("left")
        elif k in (pygame.K_d,pygame.K_RIGHT):
            player_action("right")
        elif k in (pygame.K_w,pygame.K_UP):
            player_action("up")
        elif k in (pygame.K_s,pygame.K_DOWN):
            player_action("down")
    render()

pygame.quit()
