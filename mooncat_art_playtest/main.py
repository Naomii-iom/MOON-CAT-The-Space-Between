"""MOON CAT: THE SPACE BETWEEN — self-contained two-world puzzle adventure.
Requires: pygame-ce. Run: uv run main.py
Moonlight art playtest: background PNG added in an independent Guided v1.0 copy.
Character, tiles, UI, puzzle rules, input, and save functions remain unchanged.
"""
from collections import deque
import json
import math
import random
from array import array
from pathlib import Path

import pygame
from background_art import MoonlightBackdrop

pygame.mixer.pre_init(44100, -16, 1, 256)
pygame.init()

WIDTH, HEIGHT = 1060, 735
FPS = 60
TILE = 44
COLS, ROWS = 15, 9
OX, OY = 51, 174
SIDE_X = 760
SAVE_FILE = Path(__file__).resolve().with_name("mooncat-progress.json")

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOON CAT  |  The Space Between")
clock = pygame.time.Clock()

# Load/scale PNG and prepare the quiet board crop once, after the display exists.
# Asset paths are relative to this file, never the terminal's working directory.
MOONLIGHT_ART = MoonlightBackdrop(
    Path(__file__).resolve().parent / "assets" / "backgrounds" / "moonlight_paper_v1.png",
    (WIDTH, HEIGHT),
    pygame.Rect(OX-13, OY-13, COLS*TILE+26, ROWS*TILE+26),
)


def font(size, bold=False):
    for name in ("Avenir Next", "Helvetica Neue", "Arial", "DejaVu Sans"):
        f = pygame.font.SysFont(name, size, bold=bold)
        if f:
            return f
    return pygame.font.Font(None, size)

F12, F14, F16, F20, F26, F34, F54 = [font(s, s in (20, 26, 34, 54)) for s in (12, 14, 16, 20, 26, 34, 54)]

# macOS has PingFang SC. Use a separate family for Chinese guidance.
def chinese_font(size, bold=False):
    # The user's macOS has PingFang; prefer the actual file so Chinese won't
    # show as empty squares even if SDL cannot match the family name.
    for filename in ("/System/Library/Fonts/PingFang.ttc",
                     "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"):
        if Path(filename).is_file():
            return pygame.font.Font(filename, size)
    for family in ("PingFang SC", "Hiragino Sans GB", "Heiti SC",
                   "Noto Sans CJK SC", "Microsoft YaHei"):
        match = pygame.font.match_font(family)
        if match:
            return pygame.font.Font(match, size)
    return pygame.font.SysFont("Arial Unicode MS", size, bold=bold)

C14, C17, C20, C26 = [chinese_font(sz) for sz in (14, 17, 20, 26)]
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
        "Push a stone in one world; another world remembers where it rests.",
        line(1, 7, 4) | column(2, 4, 6) | line(1, 3, 5),
        line(1, 6, 4) | line(10, 12, 4) | column(2, 4, 6) |
        column(12, 2, 4) | line(12, 13, 2),
        (2, 6), (13, 2), 1,
        plate=(6, 4), plate_world=0, stone=(4, 4),
        bridge={(7, 4), (8, 4), (9, 4)}, memory=(0, 1, 5),
        tips=("Blue stones can be pushed with your body. Their weight travels through worlds.",
              "Push the stone RIGHT until it sits on the blue plate at (6,4). Then Q reveals a pink bridge."),
    ),
    room(
        "04 / A LIGHT LEFT BEHIND", "Two actions, two worlds, one way through.",
        "Light a lamp before you leave a version of yourself behind.",
        line(1, 6, 4) | column(2, 4, 6),
        line(1, 8, 4) | line(10, 13, 4) | column(2, 4, 6) | column(11, 2, 4) | line(11, 13, 2),
        (2, 6), (13, 2), 1,
        plate=(5, 4), plate_world=0, gate=(7, 4), gate_world=1,
        lantern=(3, 3), bridge={(9, 4)}, memory=(1, 13, 4),
        tips=("A BLUE lantern creates a PINK bridge. An ECHO opens a different door.",
              "Stand at (3,4), press E to light the lamp. Stand at (5,4), then Q. Run across the pink gate and bridge."),
    ),
    room(
        "05 / THE SPACE BETWEEN", "The echo can hold a door for YOU.",
        "The last door asks you to leave a shadow of yourself behind.",
        line(1, 6, 4) | line(8, 13, 4) | column(2, 4, 6) | column(12, 4, 6),
        line(1, 3, 4) | line(5, 9, 4) | column(2, 4, 6),
        (2, 6), (13, 4), 0,
        plate=(8, 4), plate_world=1, gate=(11, 4), gate_world=0,
        memory=(0, 12, 6),
        tips=("The PINK plate opens the BLUE door. But the plate is on the other side of a wall.",
              "Blue to x=5 -> Q to Pink. Pink to x=8 -> Q to Blue. Your pink ECHO holds the final gate."),
    ),
]


# The first thing players see in every new room: intent, rules, and a plan.
# The details are deliberately clear; discovering the execution is still fun.
GUIDES = [
    {
        "title": "01 / 消失的道路", "goal": "找到右上角发光的出口。",
        "steps": [
            "先用 WASD / 方向键走到蓝色道路的断口。",
            "按 Q 切换到粉色世界：同一位置有另一条路。",
            "越过缺口后再按 Q 返回蓝色，走向出口。",
        ],
        "rule": "只有两个世界都能站立的格子，才能直接切换。",
        "short": "先到断口，再按 Q 换路。",
    },
    {
        "title": "02 / 留下一个自己", "goal": "让蓝色机关打开粉色大门。",
        "steps": [
            "先走到蓝色世界的黄色踏板上。",
            "站在踏板上按 Q：原地留下小猫残影 Echo。",
            "残影只维持 10 步，迅速从粉色世界穿过门。",
        ],
        "rule": "Echo 会帮你压住离开世界的踏板。",
        "short": "站上黄色踏板按 Q，留下残影开门。",
    },
    {
        "title": "03 / 石头的影子", "goal": "推动石头，让另一世界出现一座桥。",
        "steps": [
            "在蓝色世界，走到灰白色石头的左边。",
            "按 D / → 向右推石头，直到压住黄色踏板。",
            "石头到位后会锁住。按 Q 换到粉色世界过桥。",
        ],
        "rule": "蓝色石头压住踏板，粉色桥才会出现。推错可按 Z。",
        "short": "从左边推石头到黄色踏板，再按 Q。",
    },
    {
        "title": "04 / 留下的月光", "goal": "点灯造桥，并用 Echo 开门。",
        "steps": [
            "蓝色世界先走到月光灯附近，按 E 点亮它。",
            "灯会让粉色世界的断桥出现。再走到黄色踏板。",
            "站在踏板上按 Q 留下 Echo，然后快速穿门过桥。",
        ],
        "rule": "这一关要组合两种跨世界因果：点灯造桥＋残影开门。",
        "short": "先按 E 点灯，再站上踏板按 Q。",
    },
    {
        "title": "05 / 世界之间", "goal": "用粉色世界的残影打开蓝色世界的门。",
        "steps": [
            "在蓝色世界沿着道路走到右侧断口附近。",
            "按 Q 进入粉色世界，走到黄色踏板 (右边)。",
            "站在踏板上按 Q，留下 Echo，再往右走向出口。",
        ],
        "rule": "前面是蓝色开粉色门；最后一关要反过来！",
        "short": "在粉色踏板上按 Q，让蓝色的门打开。",
    },
]

KEY_ZH = {"left": "A / ← 向左", "right": "D / → 向右", "up": "W / ↑ 向上",
          "down": "S / ↓ 向下", "q": "Q 切换世界", "e": "E 激活机关"}


def guide_goal(s):
    """Contextual, non-spoiler task and one glowing board target."""
    if s.index == 0:
        if s.world == 0 and s.player[0] < 6:
            return "走到蓝色断口附近，按 Q 找另一条路。", (6, 4), 0
        if s.world == 1:
            return "沿粉色道路向右，到了台阶入口再按 Q。", (9, 4), 1
        return "沿着蓝色台阶走向右上角的发光出口。", s.level["exit"], 0
    if s.index == 1:
        if s.world == 0:
            return ("站在黄色踏板上，按 Q 留下残影。" if s.player == s.level["plate"]
                    else "先找到蓝色世界的黄色踏板，走上去。"), s.level["plate"], 0
        if not s.plate_on():
            return "门还锁着！回蓝色世界踩住踏板，再按 Q。", s.level["plate"], 0
        return "Echo 正在计步！向右赶路，穿过粉色门。", s.level["gate"], 1
    if s.index == 2:
        if not s.plate_on():
            if s.world == 1:
                return "桥还没出现，先回蓝色世界推动石头。", s.level["plate"], 0
            return "站到石头左侧，向右推到黄色踏板。", s.level["plate"], 0
        if s.world == 0:
            return "机关已触发！按 Q，去粉色世界走新桥。", s.level["plate"], 0
        return "粉色桥已出现，沿桥前往右侧出口。", s.level["exit"], 1
    if s.index == 3:
        if not s.lit:
            return ("先回蓝色世界点灯，再来粉色世界。" if s.world == 1
                    else "靠近蓝色小灯按 E，先点亮粉色桥。"), s.level["lantern"], 0
        if s.world == 0:
            return "再站上黄色踏板按 Q，留下 Echo 开门。", s.level["plate"], 0
        return "桥和门已准备好，赶快向右通关。", s.level["exit"], 1
    if s.world == 0:
        if s.plate_on():
            return "粉色残影已经开门，沿蓝色道路去出口。", s.level["exit"], 0
        return "蓝色走到断口，按 Q 转入粉色世界。", (5, 4), 0
    return "去粉色踏板上按 Q，把残影留在那里。", s.level["plate"], 1


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
            return False, "That spot is solid in the other world. Move before shifting.", False, False
        state.echo = (state.world, *state.player, 10)
        state.world = w
        collected = state.collect()
        return True, "An echo stays where you shifted. It fades after 10 steps.", state.exit_reached(), collected

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
                return False, "石头已经卡进机关！按 Q 去粉色世界。", False, False
            if dx != 1 or pushed[0] > state.level["plate"][0]:
                return False, "从石头左边向右推，目标是黄色踏板。", False, False
        if not state.floor(pushed, 0) or pushed == state.level["gate"]:
            return False, "The stone cannot move that way.", False, False
        state.stone = pushed
    elif not state.passable(target, state.world):
        if target == state.level["gate"]:
            return False, "The door needs pressure from the OTHER world.", False, False
        if target in state.level["bridge"]:
            return False, "There should be a bridge here. Find what makes it appear.", False, False
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
    global notice, notice_ttl
    notice, notice_ttl = msg, frames


def begin(index):
    global current, mode, hint_level, history, particles, transition, notice_ttl
    global guide_open, hint_text
    current = State(index)
    history = []
    particles = []
    transition = 0
    hint_level = 0
    hint_text = ""
    guide_open = True  # Every room first opens with an explicit walkthrough.
    notice_ttl = 0
    mode = "play"
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
    old = current.copy()
    prevstone = current.stone
    changed, feedback, completed, collected = execute(current, action)
    if changed:
        if hint_level >= 3:
            hint_text = "已前进一步。再按 H 查看新的下一步。"
        else:
            hint_text = ""
        history.append(old)
        history[:] = history[-120:]
        if action == "q":
            phase_flash = 19
            sound("shift")
        elif action == "e":
            sound("lamp")
        elif prevstone != current.stone:
            sound("push")
            spark_at(current.stone, 8)
        else:
            sound("step")
        if collected:
            memories.add(current.index)
            save_progress()
            spark_at(current.player, 30)
            sound("gem")
        # Player receives meaningful visual + text feedback when a cross-world
        # dependency is solved, not just an invisible boolean update.
        if current.index == 2 and not old.plate_on() and current.plate_on():
            message("成功！石头压住机关，粉色世界的桥出现了！按 Q 切换。", 310)
            spark_at(current.stone, 42)
        elif current.index == 3 and not old.lit and current.lit:
            message("灯亮了！粉色世界已经出现新的桥。下一步找踏板。", 300)
        elif (action == "q" and current.echo is not None and
              current.level["plate"] == current.echo[1:3] and current.plate_on()):
            message("Echo 压住机关！门已经打开，快向右走！", 240)
        elif collected:
            message("找到隐藏的记忆碎片！", 200)
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


def pill(x, y, text, active=False, color=LIGHT):
    width = max(80, F14.size(text)[0]+26)
    rounded((x,y,width,28), (40,65,80) if active else (30,34,58), 14,
            color if active else (66,74,110))
    put_text(text,x+width/2,y+14,F14,WHITE if active else MUTED,True)
    return width


def draw_cat(x, y, tint):
    # soft shadow, upright cat with pointed ears and tiny whiskers
    pygame.draw.ellipse(screen, (9,12,30), (x-14,y+10,29,10))
    pygame.draw.polygon(screen, tint, [(x-14,y-6),(x-12,y-24),(x-1,y-13)])
    pygame.draw.polygon(screen, tint, [(x+14,y-6),(x+12,y-24),(x+1,y-13)])
    pygame.draw.ellipse(screen, tint, (x-16,y-17,32,34))
    pygame.draw.polygon(screen, (241,180,197), [(x-10,y-12),(x-10,y-20),(x-4,y-13)])
    pygame.draw.polygon(screen, (241,180,197), [(x+10,y-12),(x+10,y-20),(x+4,y-13)])
    pygame.draw.circle(screen, (26,31,54), (x-7,y-1), 2)
    pygame.draw.circle(screen, (26,31,54), (x+7,y-1), 2)
    pygame.draw.circle(screen, (249,139,164), (x,y+5), 2)
    pygame.draw.arc(screen,tint,(x+8,y,22,20),4.1,6.6,3)


def world_palette(world):
    if world == 0:
        return dict(accent=LIGHT, fill=(36,72,98), solid=(23,38,68), edge=(87,164,202), bg=(10,22,43))
    return dict(accent=SHADOW, fill=(91,49,86), solid=(47,25,55), edge=(182,97,149), bg=(35,18,42))


def draw_board():
    s = current
    p = world_palette(s.world)
    brect = pygame.Rect(OX-13,OY-13,COLS*TILE+26,ROWS*TILE+26)
    if s.world == 0:
        # Background only: keep the original frame, tile shapes and all objects.
        MOONLIGHT_ART.draw_board(screen)
        pygame.draw.rect(screen, (62,83,104), brect, 2, border_radius=20)
    else:
        rounded(brect,p["bg"],20,(128,67,106),2)
    now = pygame.time.get_ticks()/1000
    shake_x = random.randint(-2,2) if shakes else 0
    for y in range(ROWS):
        for x in range(COLS):
            at=(x,y)
            px=OX+x*TILE + shake_x
            py=OY+y*TILE
            inside=s.floor(at,s.world)
            tile=pygame.Rect(px+2,py+2,TILE-4,TILE-4)
            if inside:
                # Visual material language: floor tiles are large, clear squares.
                fill=tuple(min(255,v + (3 if (x+y)%2 else 0)) for v in p["fill"])
                rounded(tile,fill,7,(p["edge"] if (x*7+y*3)%6==0 else p["solid"]),1)
                if (x+y*9)%7 == 0:
                    pygame.draw.circle(screen,p["edge"],(px+11,py+11),2)
            else:
                pygame.draw.rect(screen,(p["bg"][0]+3,p["bg"][1]+3,p["bg"][2]+4),tile,1,border_radius=5)
                # Other-world-only tiles are hinted as faint dashed blueprints.
                if s.floor(at,1-s.world):
                    pygame.draw.rect(screen,(64,55,80),(px+10,py+10,24,24),1,border_radius=3)

    # In-game guide marker: a pulsing ring is drawn on the next relevant tile.
    task, target, target_world = guide_goal(s)
    if target and target_world == s.world:
        hx,hy=tile_center(target)
        radius=24 + int(3*math.sin(now*4))
        pygame.draw.circle(screen,GOLD,(hx,hy),radius,2)
        pygame.draw.circle(screen,GOLD,(hx,hy),radius+6,1)

    # Bridges, door, plate, lamp, stone, echo, secret, portal, player
    if s.world == 1:
        for at in s.level["bridge"]:
            xx, yy=tile_center(at)
            if s.bridge_on():
                rounded((xx-18,yy-17,36,34),(158,101,153),8,(251,171,208),2)
                pygame.draw.line(screen,(255,195,222),(xx-14,yy),(xx+14,yy),2)
            else:
                pygame.draw.line(screen,(126,73,104),(xx-18,yy-10),(xx+18,yy+10),2)
                pygame.draw.line(screen,(126,73,104),(xx-18,yy+10),(xx+18,yy-10),2)

    gate=s.level["gate"]
    if gate is not None and s.world == s.level["gate_world"]:
        x,y=tile_center(gate)
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
        x,y=tile_center(plate)
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
        x,y=tile_center(lamp)
        c=GOLD if s.lit else (102,103,127)
        pygame.draw.circle(screen,c,(x,y),13)
        pygame.draw.line(screen,(190,200,210),(x,y+12),(x,y+22),3)
        if s.lit:
            pygame.draw.circle(screen,(247,201,102),(x,y),20 + int(2*math.sin(now*3)),2)
        else:
            put_text("E",x+13,y-22,F12,MUTED,True)

    if s.stone is not None:
        x,y=tile_center(s.stone)
        if s.world==0:
            pygame.draw.polygon(screen,(160,188,216),[(x-16,y-10),(x-5,y-18),(x+16,y-12),(x+18,y+11),(x+4,y+17),(x-15,y+10)])
            pygame.draw.line(screen,(215,230,243),(x-5,y-13),(x+5,y-7),2)
        else:
            pygame.draw.circle(screen,(110,77,108),(x,y),12,1)

    if s.echo and s.echo[0]==s.world:
        w,x,y,ttl=s.echo
        cx,cy=tile_center((x,y))
        draw_cat(cx,cy,(130,117,206))
        pygame.draw.circle(screen,(200,165,255),(cx,cy),22,1)
        put_text(str(ttl),cx,cy+26,F12,(225,183,246),True)

    m=s.level["memory"]
    if m and m[0]==s.world and not s.memory:
        x,y=tile_center(m[1:])
        pulse=math.sin(now*4)*3
        pygame.draw.circle(screen,(252,211,124),(x,y),8+int(pulse),2)
        pygame.draw.circle(screen,WHITE,(x,y),4)

    ex=s.level["exit"]
    if s.world==s.level["exit_world"]:
        x,y=tile_center(ex)
        rad=16 + int(math.sin(now*3)*2)
        pygame.draw.circle(screen,p["accent"],(x,y),rad,3)
        pygame.draw.circle(screen,(224,245,255),(x,y),7)
    else:
        # subtle compass hint: the goal is in the other world
        pass

    x,y=tile_center(s.player)
    draw_cat(x,y,(255,244,225) if s.world==0 else (247,202,230))
    pygame.draw.circle(screen,p["accent"],(x,y),22,1)
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
    # Stage 1: moonlight gameplay only. Menu/shadow retain the original artwork
    # until the user approves the new visual direction.
    if mode != "menu" and current.world == 0:
        MOONLIGHT_ART.draw(screen)
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
    s=current
    p=world_palette(s.world)
    put_text("MOON CAT",51,37,F34,WHITE)
    put_text("THE SPACE BETWEEN",53,82,F14,MUTED)
    rounded((335,40,280,36),(22,32,54),17,(61,86,104),1)
    put_text(s.level["name"],475,58,F14,WHITE,True)
    rounded((OX-13,129,686,32),(19,30,48),9)
    put_text(s.level["subtitle"],OX,137,F14,MUTED)
    pill(766,43,"MOONLIGHT",s.world==0,LIGHT)
    pill(865,43,"SHADOW",s.world==1,SHADOW)
    put_text("Q  SHIFT",765,92,F14,p["accent"])
    draw_board()
    rounded((748,164,276,418),(17,24,44),17,(53,68,100),1)
    draw_mini_world(770,185,224)
    pygame.draw.line(screen,(49,61,88),(768,345),(1005,345),1)
    put_text("WHAT CHANGES?",771,362,F14,WHITE)
    msg=[]
    if s.level["plate"]:
        side="BLUE" if s.level["plate_world"]==0 else "PINK"
        if s.index==2:
            msg.append(("STONE ON BLUE PLATE",s.plate_on()))
        else:
            msg.append((f"{side} PRESSURE PLATE",s.plate_on()))
    if s.level["lantern"]:
        msg.append(("BLUE LANTERN",s.lit))
    if s.level["bridge"]:
        msg.append(("PINK BRIDGE",s.bridge_on()))
    if s.level["gate"]:
        msg.append(("OTHER-WORLD DOOR",s.plate_on()))
    if not msg:
        msg=[("THE TWO MAPS DIFFER",True)]
    for i,(label,ok) in enumerate(msg):
        y=400+i*34
        pygame.draw.circle(screen,(132,226,172) if ok else (116,92,117),(781,y+8),6)
        put_text(label,797,y,F12,WHITE if ok else MUTED)
    pygame.draw.line(screen,(49,61,88),(768,503),(1005,503),1)
    put_text("ECHO  /  10 STEPS",771,522,F14,MUTED)
    if s.echo:
        w,x,y,ttl=s.echo
        put_text(f"{ttl} STEPS LEFT",771,544,F14,SHADOW)
        pygame.draw.rect(screen,(51,44,72),(897,547,107,8),border_radius=4)
        pygame.draw.rect(screen,SHADOW,(897,547,int(107*ttl/10),8),border_radius=4)
    else:
        put_text("Q leaves your double behind",771,543,F12,MUTED)

    rounded((38,593,986,110),(16,23,43),16,(52,67,96),1)
    put_text("A / D / W / S     MOVE",56,608,F14,WHITE)
    put_text("Q     SHIFT + ECHO",281,608,F14,p["accent"])
    put_text("E     INTERACT",501,608,F14,WHITE)
    put_text("Z     UNDO",683,608,F14,WHITE)
    put_text("H     HINT",854,608,F14,WHITE)
    task, target, target_world = guide_goal(s)
    put_text("下一步 / NEXT: " + task,55,643,C17,GOLD)
    if hint_text:
        put_text(hint_text[:45],55,668,C14,(175,217,235))
    elif notice_ttl > 0:
        # Chinese character coverage requires CJK font, not the Latin HUD font.
        put_text(notice[:45],55,668,C14,(175,217,235))
    else:
        put_text("按 G 看本关教程  ·  按 H 获得逐级提示  ·  Z 撤销  ·  R 重来",55,668,C14,MUTED)
    put_text("G guide · H hint · Z undo · R restart · ESC menu",55,689,F12,MUTED)
    put_text(f"MEMORIES  {len(memories)} / 5",863,679,F12,GOLD)



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
    put_text("ROOM GUIDE / 关卡指南",x+154,y+49,C20,WHITE)
    put_text(guide["title"],x+45,y+108,C26,GOLD)
    put_text("目标  " + guide["goal"],x+45,y+160,C20,WHITE)
    for i,step in enumerate(guide["steps"]):
        yy=y+214+i*58
        pygame.draw.circle(screen,LIGHT if i%2==0 else SHADOW,(x+60,yy+11),17)
        put_text(str(i+1),x+60,yy+11,F20,(18,28,48),True)
        put_text(step,x+94,yy,C17,WHITE)
    rounded((x+40,y+409,w-80,45),(34,45,74),10)
    put_text("关键规则：" + guide["rule"],x+53,y+421,C14,(193,218,237))
    rounded((x+160,y+468,w-320,40),(56,84,102),12,(113,202,222),1)
    put_text("按 Enter 开始  /  G 关闭",x+w/2,y+488,C17,WHITE,True)
    put_text("H 提示  ·  Z 撤销  ·  R 重来",x+w/2,y+455,C14,MUTED,True)



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
    if phase_flash>0 and mode=="play":
        flash=pygame.Surface((WIDTH,HEIGHT),pygame.SRCALPHA)
        flash.fill((*world_palette(current.world)["accent"],min(85,phase_flash*4)))
        screen.blit(flash,(0,0))
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
            if mode=="menu":
                running=False
            else:
                mode="menu"
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
                hint_text = "已关闭教程。再按 H 看第一条提示。"
            continue
        if k==pygame.K_r:
            begin(current.index)
        elif k==pygame.K_h:
            if hint_level == 0:
                hint_text = "线索 1：" + GUIDES[current.index]["short"]
            elif hint_level == 1:
                hint_text = "线索 2：" + GUIDES[current.index]["steps"][-1]
            else:
                move, distance = solution_hint(current)
                if move:
                    hint_text = f"下一步：按 {KEY_ZH[move]}（按 H 可继续查看）。"
                else:
                    hint_text = "暂时找不到可行路线，按 Z 撤销或 R 重来。"
            hint_level += 1
            message(hint_text, 400)
        elif k in (pygame.K_z, pygame.K_BACKSPACE):
            if history:
                current=history.pop()
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
