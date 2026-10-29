"""MOON CAT · SHADOW LAB — a self-contained light-and-shadow puzzle prototype.

Save next to your existing main.py and run: uv run shadow_lab.py
Requires only pygame-ce (already installed in the MoonCat project).
Does NOT modify main.py or the original MOON CAT progress files.
"""
import math
import random
from collections import deque
from pathlib import Path

import pygame

# ----- Pure puzzle logic, separate from rendering -------------------------
LEFT = {(x, 3) for x in range(1, 6)} | {(x, y) for x in (3, 4, 5) for y in (1, 2)}
LEFT |= {(2, 4), (3, 4), (2, 5)}
RIGHT = {(x, 3) for x in range(9, 12)} | {(11, 2)}
EXIT = (11, 3)
STONE_START = (5, 2)
STONE_TARGET = (5, 3)
START = (2, 3)
MOVES = {'left': (-1, 0), 'right': (1, 0), 'up': (0, -1), 'down': (0, 1)}


def shadow_tiles(stone):
    """Parallel moonbeams come from the LEFT; the pillar shadows 3 cells to the RIGHT."""
    return {(stone[0] + n, stone[1]) for n in (1, 2, 3)}


class Puzzle:
    def __init__(self):
        self.pos = START
        self.world = 0  # 0 moonlight, 1 shadow
        self.stone = STONE_START
        self.echo = None  # (world, x, y, remaining movement steps)
        self.steps = 0
        self.solved = False

    def snapshot(self):
        return (self.pos, self.world, self.stone, self.echo, self.steps, self.solved)

    def restore(self, snap):
        self.pos, self.world, self.stone, self.echo, self.steps, self.solved = snap

    def floor(self, point, world):
        return (point in LEFT or point in RIGHT or
                (world == 1 and point in shadow_tiles(self.stone)))

    def legal(self, point, world):
        return self.floor(point, world) and not (world == 0 and point == self.stone)

    def act(self, action):
        """Returns (did_change, feedback, event_key)."""
        if self.solved:
            return False, '已完成！按 R 再试一次。', 'none'
        if action == 'q':
            other = 1 - self.world
            if not self.legal(self.pos, other):
                return False, '这个位置在另一个世界无法站立，请先移动。', 'blocked'
            self.echo = (self.world, self.pos[0], self.pos[1], 7)
            self.world = other
            return True, ('现在是暗影世界：黑影在这里会变成道路。' if other else
                          '回到了月光世界：改变石柱，就能改变影子。'), 'shift'
        if action not in MOVES:
            return False, '', 'none'
        dx, dy = MOVES[action]
        target = (self.pos[0] + dx, self.pos[1] + dy)
        if self.world == 0 and target == self.stone:
            if self.stone == STONE_START and (dx, dy) == (0, 1) and self.pos == (5, 1):
                self.stone = STONE_TARGET
                self.pos = target
                self.steps += 1
                self.tick_echo()
                return True, '成功！石柱向下移动，影子正好落在深坑上。', 'push'
            return False, '石柱只能从上方推到金色标记的位置。', 'blocked'
        if not self.legal(target, self.world):
            return False, ('深坑不能直接走过去。调整石柱，再切换世界。' if
                           target[0] in (6, 7, 8) else '这里没有道路。'), 'blocked'
        self.pos = target
        self.steps += 1
        self.tick_echo()
        if self.pos == EXIT and self.world == 1:
            self.solved = True
            return True, '你用另一个世界的影子搭起了一座桥！', 'win'
        return True, '', 'step'

    def tick_echo(self):
        if self.echo:
            world, x, y, left = self.echo
            self.echo = (world, x, y, left - 1) if left > 1 else None


# ----- Graphics ----------------------------------------------------------
pygame.mixer.pre_init(44100, -16, 1, 256)
pygame.init()
W, H = 1200, 750
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption('MOON CAT | Shadow Lab — 月光与影子')
clock = pygame.time.Clock()
TILE, OX, OY = 51, 70, 212
COLS, ROWS = 13, 7
SIDE_X = 793
CYAN = (137, 220, 235)
PINK = (253, 167, 198)
CREAM = (255, 237, 204)
YELLOW = (255, 215, 143)


def make_font(size, bold=False):
    for file in ('/System/Library/Fonts/PingFang.ttc',
                 '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'):
        if Path(file).is_file():
            return pygame.font.Font(file, size)
    for fam in ('PingFang SC', 'Hiragino Sans GB', 'Noto Sans CJK SC',
                'Microsoft YaHei', 'Arial Unicode MS'):
        match = pygame.font.match_font(fam)
        if match:
            return pygame.font.Font(match, size)
    return pygame.font.SysFont(None, size, bold=bold)

F12, F15, F17, F20, F24, F32 = [make_font(n) for n in (12, 15, 17, 20, 24, 32)]
STARS = [(random.Random(i * 43).randint(0, W),
          random.Random(i * 59).randint(0, H),
          1 + (i % 2)) for i in range(100)]


def txt(message, x, y, color=CREAM, f=F17, center=False):
    image = f.render(str(message), True, color)
    screen.blit(image, image.get_rect(center=(x, y)) if center else (x, y))


def round_rect(rect, fill, border=None, radius=14, width=1, surf=None):
    dest = surf if surf is not None else screen
    pygame.draw.rect(dest, fill, rect, border_radius=radius)
    if border:
        pygame.draw.rect(dest, border, rect, width, border_radius=radius)


def at(pos):
    x, y = pos
    return OX + x*TILE + TILE//2, OY + y*TILE + TILE//2


def cat_on(dest, cx, cy, fill, opacity=255, ethereal=False):
    """A small, simple, recognizable cat. Ghost is SAME silhouette, no radar rings."""
    layer = pygame.Surface((64, 64), pygame.SRCALPHA)
    col = (*fill, opacity)
    pygame.draw.polygon(layer, col, [(13, 24), (17, 8), (29, 19)])
    pygame.draw.polygon(layer, col, [(51, 24), (47, 8), (35, 19)])
    pygame.draw.ellipse(layer, col, (12, 17, 40, 36))
    if not ethereal:
        pygame.draw.polygon(layer, (241, 166, 180, opacity), [(18, 20), (19, 14), (25, 20)])
        pygame.draw.polygon(layer, (241, 166, 180, opacity), [(46, 20), (45, 14), (39, 20)])
        pygame.draw.circle(layer, (31, 35, 57, opacity), (24, 34), 2)
        pygame.draw.circle(layer, (31, 35, 57, opacity), (40, 34), 2)
        pygame.draw.circle(layer, (238, 119, 142, opacity), (32, 41), 2)
        pygame.draw.arc(layer, col, (44, 34, 18, 17), 4.1, 6.3, 3)
    else:
        pygame.draw.ellipse(layer, (243, 245, 255, min(155, opacity)), (12, 17, 40, 36), 2)
        pygame.draw.circle(layer, (255, 255, 255, opacity), (24, 34), 2)
        pygame.draw.circle(layer, (255, 255, 255, opacity), (40, 34), 2)
    dest.blit(layer, (int(cx) - 32, int(cy) - 32))


def light_gradient(world):
    screen.fill((9, 22, 44) if world == 0 else (34, 16, 43))
    for i in range(6):
        col = ((14 + i*3, 32 + i*2, 55 + i*4) if world == 0
               else (44 + i*2, 20 + i*2, 57 + i*3))
        pygame.draw.rect(screen, col, (0, 0, W, 105 - i*13))
    for x, y, rad in STARS:
        pygame.draw.circle(screen, (78, 107, 139) if world == 0 else (106, 68, 115), (x, y), rad)


def dotted_line(color, start, end, seg=12):
    x0,y0=start; x1,y1=end
    length=math.hypot(x1-x0, y1-y0)
    if length<1: return
    n=max(1,int(length/seg))
    for i in range(n):
        if i%2==0:
            t0=i/n; t1=min(1,(i+.70)/n)
            pygame.draw.line(screen,color,(int(x0+(x1-x0)*t0),int(y0+(y1-y0)*t0)),
                             (int(x0+(x1-x0)*t1),int(y0+(y1-y0)*t1)),2)


def draw_tile(x,y,fill,border):
    px,py=OX+x*TILE, OY+y*TILE
    round_rect((px+3,py+3,TILE-6,TILE-6),fill,border,10)


def next_step(s):
    if s.solved:
        return '你让影子成为了通往右岸的桥！'
    if s.stone == STONE_START:
        if s.world == 1:
            return '影子还在上方，无法通到右岸。按 Q 回月光世界。'
        if s.pos == (5,1):
            return '按 S / ↓ 推动石柱，让它的影子向下移动一格。'
        return '走到石柱正上方（标记处），再向下推石柱。'
    if s.world == 0:
        return '看！影子对准缺口了。按 Q 切换到暗影世界。'
    return '影子已经变成桥，沿着粉色格子向右走到出口。'


def draw_board(s,t):
    pal=(CYAN if s.world==0 else PINK)
    board=(OX-16, OY-16, COLS*TILE+32, ROWS*TILE+32)
    round_rect(board,(14,29,51) if s.world==0 else (41,21,49),
               (67,105,126) if s.world==0 else (124,75,109),20,2)
    for y in range(ROWS):
        for x in range(COLS):
            pos=(x,y)
            if pos in LEFT or pos in RIGHT:
                if s.world==0:
                    draw_tile(x,y,(46,91,113),(83,142,167))
                else:
                    draw_tile(x,y,(98,54,94),(147,91,136))
            else:
                px,py=OX+x*TILE,OY+y*TILE
                pygame.draw.rect(screen,(31,46,64) if s.world==0 else (55,34,62),
                                 (px+6,py+6,TILE-12,TILE-12),1,border_radius=8)

    # From the far left, large distant moonlight travels almost parallel toward the pillar.
    rock_x,rock_y=at(s.stone)
    if s.world==0:
        for delta in (-20,-9,9,20):
            dotted_line((76,140,165),(OX+16,rock_y+delta),(rock_x-18,rock_y+delta),13)
        moon_y = OY + 3*TILE + TILE//2  # fixed moonlight source
        pygame.draw.circle(screen,(71,117,144),(OX+14,moon_y),15,2)
        txt('☾',OX+14,moon_y,(192,229,231),F24,True)
        # Moonlight shows a harmless, flat SHADOW tracing over the pit.
        for p in sorted(shadow_tiles(s.stone)):
            x,y=p
            px,py=OX+x*TILE,OY+y*TILE
            layer=pygame.Surface((TILE-6,TILE-6),pygame.SRCALPHA)
            round_rect((0,0,TILE-6,TILE-6),(23,13,51,166),(147,100,160,160),9,2,layer)
            screen.blit(layer,(px+3,py+3))
            pygame.draw.line(screen,(152,111,179),(px+12,py+33),(px+39,py+16),1)
        pygame.draw.line(screen,(211,184,234),(rock_x+18,rock_y),(at((8,s.stone[1]))[0]+21,rock_y),2)
    else:
        # The SAME projected shadow becomes walkable ONLY in the shadow realm.
        for p in sorted(shadow_tiles(s.stone)):
            x,y=p
            col=(179,105,167) if s.stone==STONE_TARGET else (126,73,125)
            draw_tile(x,y,col,(245,171,220))
            px,py=at(p)
            pygame.draw.line(screen,(255,196,226),(px-15,py),(px+15,py),2)
            pygame.draw.circle(screen,(255,211,231),(px,py-9),2)

    # Target landing pad and lever/pillar only exist in moonlight world.
    if s.world==0:
        tx,ty=at(STONE_TARGET)
        pygame.draw.circle(screen,YELLOW,(tx,ty),19,2)
        pygame.draw.circle(screen,YELLOW,(tx,ty),4)
        if s.stone==STONE_START:
            gx,gy=at((5,1))
            if s.pos!=(5,1):
                pygame.draw.circle(screen,YELLOW,(gx,gy),18+round(3*math.sin(t*4)),2)
            txt('↓',rock_x,rock_y+22,YELLOW,F20,True)
        pygame.draw.polygon(screen,(150,178,200),[(rock_x-19,rock_y-12),(rock_x-8,rock_y-23),
                                                  (rock_x+20,rock_y-15),(rock_x+23,rock_y+13),
                                                  (rock_x+5,rock_y+23),(rock_x-19,rock_y+13)])
        pygame.draw.line(screen,(223,231,248),(rock_x-6,rock_y-17),(rock_x+8,rock_y-9),2)
        if s.stone==STONE_TARGET:
            pygame.draw.circle(screen,YELLOW,(rock_x,rock_y),26+round(math.sin(t*3)*2),2)
    else:
        # The pillar is not solid in Shadow World, but its projected silhouette still shows the source.
        px,py=at(s.stone)
        pygame.draw.circle(screen,(129,87,136),(px,py),15,1)

    # Exit and direction cue
    ex,ey=at(EXIT)
    pygame.draw.circle(screen,YELLOW,(ex,ey),17+int(math.sin(t*4)*2),3)
    pygame.draw.circle(screen,(255,247,224),(ex,ey),7)
    if s.world==0:
        txt('暗影世界出口',ex,ey-47,(186,173,187),F12,True)

    # Single unobtrusive translucent echo, not a radar signal.
    if s.echo:
        ew,x,y,remaining=s.echo
        if ew != s.world:
            gx,gy=at((x,y))
            strength=int(60+remaining/7*65)
            cat_on(screen,gx,gy-9 if s.pos==(x,y) else gy,
                   CYAN if ew==0 else PINK,strength,ethereal=True)
            for j in range(3):
                phase=t*1.5+j*math.tau/3
                pygame.draw.circle(screen,CYAN if ew==0 else PINK,
                                   (int(gx+22*math.cos(phase)),int(gy+20*math.sin(phase))),1)

    # Main cat, above other elements.
    px,py=at(s.pos)
    cat_on(screen,px,py,(254,241,226) if s.world==0 else (255,209,227))
    pygame.draw.circle(screen,CYAN if s.world==0 else PINK,(px,py),24,1)
    return board


def draw_preview(s):
    x0,y0=SIDE_X+16,316
    off=1-s.world
    scale=21
    color=CYAN if off==0 else PINK
    txt('另一个世界 / '+('月光' if off==0 else '暗影'),x0,y0-35,color,F20)
    for p in LEFT | RIGHT:
        x,y=p
        round_rect((x0+x*scale,y0+y*scale,scale-3,scale-3),
                   (48,92,111) if off==0 else (97,54,95),None,4)
    for p in shadow_tiles(s.stone):
        x,y=p
        if off==1:
            round_rect((x0+x*scale,y0+y*scale,scale-3,scale-3),(201,120,182),(253,175,219),4)
        else:
            round_rect((x0+x*scale,y0+y*scale,scale-3,scale-3),(33,26,60),(114,89,130),4)
    x,y=EXIT
    pygame.draw.circle(screen,YELLOW,(x0+x*scale+9,y0+y*scale+9),6,2)
    if off==0:
        x,y=s.stone
        pygame.draw.circle(screen,(192,208,218),(x0+x*scale+9,y0+y*scale+9),8)
    # Show player's corresponding coordinate as outline in the other world.
    x,y=s.pos
    pygame.draw.circle(screen,color,(x0+x*scale+9,y0+y*scale+9),8,1)


def draw_help_box(s):
    x=SIDE_X
    round_rect((x,164,383,427),(19,29,51) if s.world==0 else (43,27,54),
               (67,92,120) if s.world==0 else (127,73,111),20)
    txt('规则：光 → 物体 → 影子',x+23,188,YELLOW,F20)
    txt('月光从左往右照来。',x+23,233,(213,225,239),F17)
    txt('石柱挡住光，右侧就有影子。',x+23,261,(213,225,239),F17)
    txt('只有在暗影世界，影子才能踩。',x+23,289,(213,225,239),F17)
    draw_preview(s)
    status=('对准了！影子已连通深坑。' if s.stone==STONE_TARGET else
            '没对准：影子在上方，无法过桥。')
    txt(status,x+23,532, (145,239,181) if s.stone==STONE_TARGET else YELLOW,F17)
    txt('月光世界：蓝色  /  暗影世界：粉色',x+23,562,(158,172,196),F12)


def draw_ui(s,t,toast,toast_until,show_help,won):
    light_gradient(s.world)
    txt('MOON CAT',60,37,CREAM,F32)
    txt('SHADOW LAB  /  影子会变成桥',60,81,CYAN if s.world==0 else PINK,F17)
    txt('01  ·  The Bridge of Shadows',470,65,(187,205,224),F17)
    round_rect((823,50,294,42),(34,77,88) if s.world==0 else (96,51,81),
               CYAN if s.world==0 else PINK,18)
    txt('月光世界' if s.world==0 else '暗影世界',970,70,CREAM,F20,True)
    txt('把影子移动到深坑上，再到另一世界走过它。',67,164,(189,205,223),F17)
    draw_board(s,t)
    draw_help_box(s)
    round_rect((50,605,1100,103),(19,28,48),(74,88,116),16)
    txt('现在做什么？',75,621,YELLOW,F17)
    txt(next_step(s),75,650,CREAM,F20)
    txt('WASD / 方向键 移动     Q 切换世界     Z 撤销     H 提示     G 教学     R 重来',75,685,(167,188,211),F15)
    if toast and t<toast_until:
        rounded=pygame.Surface((740,48),pygame.SRCALPHA)
        pygame.draw.rect(rounded,(23,44,62,230),(0,0,740,48),border_radius=12)
        screen.blit(rounded,(68,108))
        txt(toast,86,120,(240,232,216),F17)
    if show_help:
        lay=pygame.Surface((W,H),pygame.SRCALPHA)
        lay.fill((8,10,25,210))
        screen.blit(lay,(0,0))
        round_rect((208,155,782,439),(26,39,62),(123,179,197),26,2)
        txt('这次不需要猜机关是什么意思',250,194,YELLOW,F24)
        txt('① 月光从左边照过来，石柱在右边留下影子。',250,260,CREAM,F20)
        txt('② 在月光世界走到石柱上方，按 S / ↓ 推它。',250,310,CREAM,F20)
        txt('③ 影子会随石柱下移，对准中间的深坑。',250,360,CREAM,F20)
        txt('④ 按 Q 切换到暗影世界，那道影子就变成桥。',250,410,CREAM,F20)
        txt('影子不是现实中的桥，而是这款游戏的魔法规则。',250,473,(156,208,223),F17)
        txt('按 Space / Enter 开始   ·   随时按 G 重看',250,543,YELLOW,F17)
    if won:
        lay=pygame.Surface((W,H),pygame.SRCALPHA)
        lay.fill((10,16,33,195))
        screen.blit(lay,(0,0))
        round_rect((265,210,676,310),(30,49,68),(136,213,210),26,2)
        txt('解开了！',475,250,YELLOW,F32)
        txt('你改变了石柱的位置，也改变了另一个世界。',337,330,CREAM,F20)
        txt('原本只是影子，现在真的能承载脚步。',348,370,CREAM,F20)
        txt(f'本次移动 {s.steps} 步  ·  按 R 再玩一次',375,452,CYAN,F20)


puzzle=Puzzle()
history=[]
show_guide=True
notice=''
notice_until=0
running=True
while running:
    dt=min(clock.tick(60)/1000,0.06)
    tick=pygame.time.get_ticks()/1000
    for ev in pygame.event.get():
        if ev.type==pygame.QUIT:
            running=False
        if ev.type==pygame.KEYDOWN:
            if ev.key==pygame.K_ESCAPE:
                running=False
            elif ev.key==pygame.K_g:
                show_guide=not show_guide
            elif ev.key in (pygame.K_RETURN,pygame.K_SPACE) and show_guide:
                show_guide=False
            elif ev.key==pygame.K_r:
                puzzle=Puzzle();history=[];show_guide=False;notice=''
            elif not show_guide:
                if ev.key==pygame.K_z and history:
                    puzzle.restore(history.pop()); notice='撤销成功';notice_until=tick+1.4
                elif ev.key==pygame.K_h:
                    notice=next_step(puzzle);notice_until=tick+5
                else:
                    keymap={pygame.K_q:'q',pygame.K_a:'left',pygame.K_LEFT:'left',
                            pygame.K_d:'right',pygame.K_RIGHT:'right',
                            pygame.K_w:'up',pygame.K_UP:'up',
                            pygame.K_s:'down',pygame.K_DOWN:'down'}
                    action=keymap.get(ev.key)
                    if action:
                        snap=puzzle.snapshot()
                        changed,feedback,event=puzzle.act(action)
                        if changed:
                            history.append(snap)
                            if len(history)>100:history.pop(0)
                        if feedback:
                            notice=feedback;notice_until=tick+(3.5 if event in ('push','shift','win') else 2)
    draw_ui(puzzle,tick,notice,notice_until,show_guide,puzzle.solved)
    pygame.display.flip()
pygame.quit()
