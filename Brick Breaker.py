import json
import math
import os
import random
import sys
import pygame

pygame.init()
WIDTH, HEIGHT = 920, 880
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Brick Breaker Deluxe")
clock = pygame.time.Clock()

SAVE_FILE = "scores.json"

BRICK_COLORS = [
    (255, 55, 95),
    (255, 140, 35),
    (250, 215, 40),
    (40, 225, 115),
    (45, 175, 255),
    (180, 75, 255),
]


def make_space_bg():
    surf = pygame.Surface((WIDTH, HEIGHT))
    for y in range(HEIGHT):
        p = y / HEIGHT
        r = int(8 + (p ** 1.5) * 38)
        g = int(10 + (p ** 1.3) * 18)
        b = int(28 + p * 65)
        pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    neb_Check = [
        (220, 240, 210, (140, 40, 190, 28)),
        (700, 320, 250, (30, 120, 220, 26)),
        (460, 520, 280, (210, 40, 110, 22)),
    ]
    for nx, ny, nr, ncol in neb_Check:
        for i in range(6, 0, -1):
            rad = int(nr * (i / 6))
            ns = pygame.Surface((rad * 2, rad * 2), pygame.SRCALPHA)
            pygame.draw.circle(ns, ncol, (rad, rad), rad)
            surf.blit(ns, (nx - rad, ny - rad))

    px, py, pr = 770, 170, 52
    planet_s = pygame.Surface((220, 220), pygame.SRCALPHA)
    pygame.draw.circle(planet_s, (70, 140, 255, 45), (110, 110), pr + 16)
    pygame.draw.circle(planet_s, (45, 95, 205), (110, 110), pr)
    pygame.draw.circle(planet_s, (95, 175, 255), (96, 96), int(pr * 0.75))
    pygame.draw.ellipse(planet_s, (200, 230, 255, 180), (25, 92, 170, 38), 4)
    surf.blit(planet_s, (px - 110, py - 110))
    return surf


BG_BASE = make_space_bg()


def draw_star(surface, cx, cy, r, color):
    pts = []
    for i in range(10):
        ang = i * math.pi / 5 - math.pi / 2
        d = r if i % 2 == 0 else r * 0.42
        pts.append((cx + d * math.cos(ang), cy + d * math.sin(ang)))
    pygame.draw.polygon(surface, color, pts)
    pygame.draw.polygon(surface, (255, 255, 255), pts, 2)


def draw_heart(surface, cx, cy, r, color):
    pygame.draw.circle(surface, color, (cx - r // 2, cy - r // 4), int(r * 0.6))
    pygame.draw.circle(surface, color, (cx + r // 2, cy - r // 4), int(r * 0.6))
    pts = [(cx - int(r * 1.05), cy - r // 8), (cx + int(r * 1.05), cy - r // 8), (cx, cy + r)]
    pygame.draw.polygon(surface, color, pts)


def draw_medal(surface, cx, cy, rank):
    if rank == 1:
        col, border = (255, 215, 0), (185, 135, 0)
    elif rank == 2:
        col, border = (215, 220, 230), (130, 135, 145)
    else:
        col, border = (215, 140, 75), (140, 80, 30)

    pygame.draw.polygon(surface, (220, 50, 60), [(cx - 8, cy - 16), (cx - 2, cy - 16), (cx - 3, cy)])
    pygame.draw.polygon(surface, (50, 130, 230), [(cx + 2, cy - 16), (cx + 8, cy - 16), (cx + 3, cy)])
    pygame.draw.circle(surface, col, (cx, cy + 3), 12)
    pygame.draw.circle(surface, border, (cx, cy + 3), 12, 2)
    draw_star(surface, cx, cy + 3, 6, (255, 255, 255))


class BackgroundFX:

    def __init__(self):
        self.stars = []
        for _ in range(85):
            self.stars.append([
                random.uniform(0, WIDTH),
                random.uniform(0, HEIGHT),
                random.uniform(0.2, 1.4),
                random.randint(1, 3),
                random.choice([(255, 255, 255), (160, 220, 255), (255, 200, 240)]),
            ])
        self.meteors = []
        self.grid_offset = 0.0

    def update(self):
        self.grid_offset = (self.grid_offset + 0.6) % 40
        for s in self.stars:
            s[1] += s[2]
            if s[1] > HEIGHT:
                s[1] = 0
                s[0] = random.uniform(0, WIDTH)

        if random.random() < 0.015 and len(self.meteors) < 2:
            self.meteors.append([random.randint(100, WIDTH - 50), random.randint(20, 250), random.uniform(-9, -6), random.uniform(4, 7), 35])

        for m in self.meteors[:]:
            m[0] += m[2]
            m[1] += m[3]
            m[4] -= 1
            if m[4] <= 0:
                self.meteors.remove(m)

    def draw(self, surface, ox=0, oy=0):
        surface.blit(BG_BASE, (ox, oy))

        for x, y, _, sz, col in self.stars:
            pygame.draw.circle(surface, col, (int(x + ox), int(y + oy)), sz)

        for mx, my, vx, vy, life in self.meteors:
            end_x = int(mx - vx * 4)
            end_y = int(my - vy * 4)
            pygame.draw.line(surface, (140, 220, 255), (int(mx), int(my)), (end_x, end_y), 2)
            pygame.draw.circle(surface, (255, 255, 255), (int(mx), int(my)), 3)

        horizon_y = HEIGHT - 150
        grid_surf = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
        pygame.draw.line(grid_surf, (255, 70, 190, 110), (0, 0), (WIDTH, 0), 2)

        for i in range(-8, 9):
            top_x = WIDTH // 2 + i * 35
            bot_x = WIDTH // 2 + i * 135
            pygame.draw.line(grid_surf, (190, 60, 220, 55), (top_x, 0), (bot_x, 150), 1)

        for r in range(6):
            yy = int(((r * 25 + self.grid_offset) / 150) ** 1.6 * 150)
            pygame.draw.line(grid_surf, (80, 190, 255, 50), (0, yy), (WIDTH, yy), 1)

        surface.blit(grid_surf, (0, horizon_y))


class Shockwave:

    def __init__(self, x, y, color):
        self.x = int(x)
        self.y = int(y)
        self.color = color
        self.r = 8
        self.max_r = 65
        self.life = 18

    def update(self):
        self.r += 3.2
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            w = max(1, int((self.life / 18) * 4))
            pygame.draw.circle(surface, self.color, (self.x, self.y), int(self.r), w)


class IconBtn:

    def __init__(self, x, y, size, kind, color):
        self.rect = pygame.Rect(x, y, size, size)
        self.size = size
        self.kind = kind
        self.color = color
        self.image = self.make_img(False)
        self.hover_image = self.make_img(True)

    def make_img(self, hover):
        s = self.size
        surf = pygame.Surface((s, s + 6), pygame.SRCALPHA)
        cx, cy = s // 2, s // 2 + (0 if hover else 2)

        pygame.draw.circle(surf, (5, 8, 20, 180), (s // 2, s // 2 + 5), s // 2 - 2)
        col = tuple(min(255, c + 35) for c in self.color) if hover else self.color
        pygame.draw.circle(surf, col, (cx, cy), s // 2 - 2)
        pygame.draw.circle(surf, (255, 255, 255, 90), (cx, cy - 3), int(s * 0.38))
        pygame.draw.circle(surf, (220, 240, 255), (cx, cy), s // 2 - 2, 3)

        r = int(s * 0.28)
        if self.kind == "home":
            pts = [(cx, cy - r), (cx - r, cy - 2), (cx + r, cy - 2)]
            pygame.draw.polygon(surf, (255, 255, 255), pts)
            pygame.draw.rect(surf, (255, 255, 255), (cx - r + 4, cy - 2, (r - 4) * 2, r + 2), border_radius=2)
            pygame.draw.rect(surf, col, (cx - 4, cy + 3, 8, r - 3))
        elif self.kind == "reload":
            pygame.draw.arc(surf, (255, 255, 255), (cx - r, cy - r, r * 2, r * 2), 0.6, math.pi * 1.85, 4)
            pts = [(cx + r - 2, cy - 6), (cx + r + 5, cy + 3), (cx + r - 8, cy + 3)]
            pygame.draw.polygon(surf, (255, 255, 255), pts)
        elif self.kind == "trophy":
            pygame.draw.polygon(surf, (255, 235, 80), [(cx - r, cy - r + 2), (cx + r, cy - r + 2), (cx + r // 2, cy + 3), (cx - r // 2, cy + 3)])
            pygame.draw.rect(surf, (255, 235, 80), (cx - 3, cy + 3, 6, r - 3))
            pygame.draw.rect(surf, (255, 235, 80), (cx - r // 1.4, cy + r - 2, int(r * 1.4), 5), border_radius=2)
        elif self.kind == "check":
            pts = [(cx - r, cy), (cx - r // 4, cy + r - 2), (cx + r, cy - r + 3)]
            pygame.draw.lines(surf, (255, 255, 255), False, pts, 5)
        elif self.kind == "close":
            pygame.draw.line(surf, (255, 255, 255), (cx - r + 2, cy - r + 2), (cx + r - 2, cy + r - 2), 5)
            pygame.draw.line(surf, (255, 255, 255), (cx + r - 2, cy - r + 2), (cx - r + 2, cy + r - 2), 5)
        elif self.kind == "trash":
            pygame.draw.rect(surf, (255, 255, 255), (cx - r + 3, cy - r // 2, (r - 3) * 2, int(r * 1.5)), border_radius=2)
            pygame.draw.line(surf, (255, 255, 255), (cx - r, cy - r // 2 - 2), (cx + r, cy - r // 2 - 2), 3)
        return surf

    def draw(self, surface):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        surface.blit(self.hover_image if hover else self.image, self.rect.topleft)


class StageCard:

    def __init__(self, x, y, w, h, stage_id, title):
        self.rect = pygame.Rect(x, y, w, h)
        self.stage_id = stage_id
        self.title = title
        self.image = self.make_card(w, h, False)
        self.hover_image = self.make_card(w, h, True)

    def make_card(self, w, h, hover):
        surf = pygame.Surface((w, h + 10), pygame.SRCALPHA)
        y_off = 0 if hover else 4

        pygame.draw.rect(surf, (5, 8, 22, 190), (4, 10, w - 8, h - 4), border_radius=22)

        body = pygame.Rect(0, y_off, w, h - 4)
        for yy in range(body.h):
            p = yy / body.h
            r = int((45 if hover else 30) + p * 18)
            g = int((65 if hover else 42) + p * 28)
            b = int((125 if hover else 90) + p * 35)
            pygame.draw.line(surf, (r, g, b), (6, body.y + yy), (w - 6, body.y + yy))

        border_col = (110, 230, 255) if hover else (75, 145, 225)
        pygame.draw.rect(surf, border_col, body, 3, border_radius=22)
        pygame.draw.rect(surf, (255, 255, 255, 35), (8, y_off + 5, w - 16, 22), border_radius=10)

        px, py, pw, ph = 20, y_off + 22, 92, 84
        pygame.draw.rect(surf, (12, 18, 38), (px, py, pw, ph), border_radius=10)
        pygame.draw.rect(surf, (85, 155, 235), (px, py, pw, ph), 2, border_radius=10)

        for r in range(4):
            for c in range(4):
                if self.stage_id == 2 and abs(c - 1.5) > r + 0.5:
                    continue
                if self.stage_id == 3 and r in (1, 2) and c in (1, 2):
                    continue
                if self.stage_id == 4 and (r + c) % 2 == 1:
                    continue
                col = BRICK_COLORS[(r + self.stage_id) % len(BRICK_COLORS)]
                pygame.draw.rect(surf, col, (px + 8 + c * 19, py + 10 + r * 13, 16, 9), border_radius=2)

        pygame.draw.rect(surf, (90, 225, 255), (px + 28, py + ph - 12, 36, 6), border_radius=3)

        f = pygame.font.SysFont("arial", 23, bold=True)
        shd = f.render(self.title, True, (10, 15, 35))
        txt = f.render(self.title, True, (255, 255, 255))
        surf.blit(shd, (126, y_off + 22))
        surf.blit(txt, (124, y_off + 20))
        return surf

    def draw(self, surface, font, stars, best_score):
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        y_off = 0 if hover else 4
        surface.blit(self.hover_image if hover else self.image, self.rect.topleft)

        sc_txt = font.render(f"Best: {best_score}", True, (175, 225, 255))
        surface.blit(sc_txt, (self.rect.x + 124, self.rect.y + y_off + 56))

        for i in range(3):
            scol = (255, 215, 0) if i < stars else (45, 65, 110)
            draw_star(surface, self.rect.x + 138 + i * 30, self.rect.y + y_off + 98, 12, scol)


class FloatText:

    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 48
        self.font = pygame.font.SysFont("arial", 21, bold=True)

    def update(self):
        self.y -= 1.5
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            shd = self.font.render(self.text, True, (10, 15, 30))
            txt = self.font.render(self.text, True, self.color)
            surface.blit(shd, (int(self.x - txt.get_width() // 2 + 2), int(self.y + 2)))
            surface.blit(txt, (int(self.x - txt.get_width() // 2), int(self.y)))


class Particle:

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        ang = random.uniform(0, math.pi * 2)
        spd = random.uniform(2, 8)
        self.vx = math.cos(ang) * spd
        self.vy = math.sin(ang) * spd
        self.life = random.randint(20, 42)
        self.size = random.randint(3, 8)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.16
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), max(1, int(self.size)))


class PowerUp:

    def __init__(self, x, y, kind):
        self.rect = pygame.Rect(x - 24, y - 13, 48, 26)
        self.kind = kind
        self.vy = 3.2
        self.font = pygame.font.SysFont("arial", 13, bold=True)

    def update(self):
        self.rect.y += int(self.vy)

    def draw(self, surface):
        colors = {
            "multi": (40, 185, 255),
            "fire": (255, 95, 30),
            "laser": (195, 70, 255),
            "wide": (45, 220, 115),
            "life": (250, 55, 95),
        }
        labels = {
            "multi": "3X",
            "fire": "FIRE",
            "laser": "LZR",
            "wide": "WIDE",
            "life": "+1",
        }
        col = colors[self.kind]
        glow = pygame.Rect(self.rect.x - 3, self.rect.y - 3, self.rect.w + 6, self.rect.h + 6)
        pygame.draw.rect(surface, (255, 255, 255), glow, 1, border_radius=14)
        pygame.draw.rect(surface, col, self.rect, border_radius=13)
        pygame.draw.rect(surface, (255, 255, 255), (self.rect.x + 5, self.rect.y + 3, self.rect.w - 10, 6), border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=13)
        txt = self.font.render(labels[self.kind], True, (255, 255, 255))
        surface.blit(txt, (self.rect.centerx - txt.get_width() // 2, self.rect.centery - txt.get_height() // 2 + 1))


class Laser:

    def __init__(self, x, y):
        self.rect = pygame.Rect(x - 3, y - 16, 6, 20)
        self.vy = -12

    def update(self):
        self.rect.y += self.vy

    def draw(self, surface):
        pygame.draw.rect(surface, (230, 80, 255), (self.rect.x - 2, self.rect.y, 10, 20), border_radius=5)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, border_radius=3)


class Brick:

    def __init__(self, x, y, w, h, color, hp=1, is_bomb=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = color
        self.hp = hp
        self.max_hp = hp
        self.is_bomb = is_bomb

    def draw(self, surface):
        col = (245, 70, 35) if self.is_bomb else self.color
        if self.max_hp > 1 and not self.is_bomb:
            col = (175, 195, 220) if self.max_hp == 2 else (250, 195, 45)

        dark_col = tuple(max(0, c - 60) for c in col)
        light_col = tuple(min(255, c + 65) for c in col)

        pygame.draw.rect(surface, (5, 8, 20), (self.rect.x + 4, self.rect.y + 5, self.rect.w, self.rect.h), border_radius=7)
        pygame.draw.rect(surface, dark_col, self.rect, border_radius=7)

        inner = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h - 5)
        pygame.draw.rect(surface, col, inner, border_radius=6)

        shine = pygame.Rect(self.rect.x + 5, self.rect.y + 4, self.rect.w - 10, 6)
        pygame.draw.rect(surface, light_col, shine, border_radius=3)
        pygame.draw.rect(surface, (235, 245, 255), self.rect, 1, border_radius=7)

        cx, cy = self.rect.center
        if self.is_bomb:
            pulse = 6 + int(abs(math.sin(pygame.time.get_ticks() * 0.008)) * 3)
            pygame.draw.circle(surface, (255, 235, 70), (cx, cy), pulse)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), 3)
        elif self.hp < self.max_hp:
            pygame.draw.line(surface, (30, 35, 50), (cx - 14, cy - 6), (cx - 2, cy + 3), 2)
            pygame.draw.line(surface, (30, 35, 50), (cx - 2, cy + 3), (cx + 12, cy - 4), 2)


class Ball:

    def __init__(self, x, y, vx, vy, stuck=False):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.r = 9
        self.stuck = stuck
        self.trail = []

    def update(self, px, py):
        if self.stuck:
            self.x = float(px)
            self.y = float(py - self.r - 2)
            self.trail.clear()
            return

        self.trail.append((self.x, self.y))
        if len(self.trail) > 9:
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy

        if self.x - self.r < 35:
            self.x = 35 + self.r
            self.vx = abs(self.vx)
        elif self.x + self.r > WIDTH - 35:
            self.x = WIDTH - 35 - self.r
            self.vx = -abs(self.vx)

        if self.y - self.r < 85:
            self.y = 85 + self.r
            self.vy = abs(self.vy)

    def draw(self, surface, is_fire):
        for i, (tx, ty) in enumerate(self.trail):
            rad = max(2, int(self.r * (i + 1) / len(self.trail) * 0.85))
            tcol = (255, 115, 25) if is_fire else (65, 195, 255)
            pygame.draw.circle(surface, tcol, (int(tx), int(ty)), rad)

        col = (255, 235, 80) if is_fire else (255, 255, 255)
        edge = (255, 75, 20) if is_fire else (70, 205, 255)
        pygame.draw.circle(surface, edge, (int(self.x), int(self.y)), self.r + 3)
        pygame.draw.circle(surface, col, (int(self.x), int(self.y)), self.r)


class Game:

    def __init__(self):
        self.font = pygame.font.SysFont("arial", 18, bold=True)
        self.med_font = pygame.font.SysFont("arial", 25, bold=True)
        self.big_font = pygame.font.SysFont("arial", 46, bold=True)
        self.bg_fx = BackgroundFX()
        self.state = "menu"
        self.player_name = ""
        self.pending_stage = 1
        self.stage = 1
        self.filter_mode = 0
        self.records = []
        self.best_scores = {1: 0, 2: 0, 3: 0, 4: 0}
        self.best_stars = {1: 0, 2: 0, 3: 0, 4: 0}
        self.stage_cards = []
        self.filter_tabs = []
        self.particles = []
        self.waves = []
        self.float_texts = []
        self.shake = 0
        self.load_records()
        self.setup_menu()

    def load_records(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                dedup = {}
                for r in raw:
                    key = (r.get("name", "Player").strip().lower(), r.get("stage", 1))
                    if key not in dedup or (r["score"], -r["time"]) > (dedup[key]["score"], -dedup[key]["time"]):
                        dedup[key] = r
                self.records = list(dedup.values())
                self.records.sort(key=lambda r: (-r["score"], r["time"]))
            except Exception:
                self.records = []
        self.update_bests()

    def save_record(self, score, time_taken, stars):
        name = self.player_name.strip() or "Player"
        entry = {
            "name": name,
            "stage": self.stage,
            "score": score,
            "time": time_taken,
            "stars": stars,
        }
        updated = False
        for i, r in enumerate(self.records):
            if r["name"].strip().lower() == name.lower() and r.get("stage", 1) == self.stage:
                if (score, -time_taken) > (r["score"], -r["time"]):
                    self.records[i] = entry
                updated = True
                break
        if not updated:
            self.records.append(entry)

        self.records.sort(key=lambda r: (-r["score"], r["time"]))
        self.records = self.records[:50]
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.records, f)
        except Exception:
            pass
        self.update_bests()

    def clear_records(self):
        self.records.clear()
        self.update_bests()
        try:
            if os.path.exists(SAVE_FILE):
                os.remove(SAVE_FILE)
        except Exception:
            pass

    def update_bests(self):
        self.best_scores = {1: 0, 2: 0, 3: 0, 4: 0}
        self.best_stars = {1: 0, 2: 0, 3: 0, 4: 0}
        for s in [1, 2, 3, 4]:
            sub = [r for r in self.records if r.get("stage") == s]
            if sub:
                self.best_scores[s] = max(r["score"] for r in sub)
                self.best_stars[s] = max(r.get("stars", 1) for r in sub)

    def ask_name(self, stg):
        self.pending_stage = stg
        self.player_name = ""
        self.state = "name_input"

    def setup_menu(self):
        configs = [
            (1, "Stage 1: Classic", WIDTH // 2 - 330, 275),
            (2, "Stage 2: Pyramid", WIDTH // 2 + 15, 275),
            (3, "Stage 3: Fortress", WIDTH // 2 - 330, 440),
            (4, "Stage 4: Matrix", WIDTH // 2 + 15, 440),
        ]
        self.stage_cards.clear()
        for stg, title, x, y in configs:
            self.stage_cards.append(StageCard(x, y, 315, 135, stg, title))

        self.btn_menu_trophy = IconBtn(WIDTH - 85, 20, 60, "trophy", (225, 150, 20))
        self.btn_name_ok = IconBtn(WIDTH // 2 - 75, HEIGHT // 2 + 55, 64, "check", (46, 185, 85))
        self.btn_name_cancel = IconBtn(WIDTH // 2 + 11, HEIGHT // 2 + 55, 64, "close", (215, 70, 65))
        self.btn_board_home = IconBtn(WIDTH - 110, 72, 56, "home", (215, 70, 65))
        self.btn_board_clear = IconBtn(85, 72, 56, "trash", (190, 65, 65))

        modes = [(0, "ALL"), (1, "STAGE 1"), (2, "STAGE 2"), (3, "STAGE 3"), (4, "STAGE 4")]
        self.filter_tabs.clear()
        start_x = (WIDTH - (5 * 106 + 4 * 12)) // 2
        for i, (m, label) in enumerate(modes):
            r = pygame.Rect(start_x + i * 118, 158, 106, 38)
            self.filter_tabs.append((r, m, label))

    def start_game(self, stg):
        self.stage = stg
        self.state = "playing"
        self.score = 0
        self.combo = 0
        self.lives = 3
        self.paddle_w = 135
        self.paddle_h = 18
        self.paddle_x = WIDTH // 2
        self.paddle_y = HEIGHT - 58

        self.fire_until = 0
        self.laser_until = 0
        self.wide_until = 0
        self.last_laser = 0

        self.balls = [Ball(self.paddle_x, self.paddle_y - 12, 5.2, -6.5, stuck=True)]
        self.bricks = []
        self.powerups = []
        self.lasers = []
        self.particles.clear()
        self.waves.clear()
        self.float_texts.clear()

        self.start_ticks = pygame.time.get_ticks()
        self.elapsed = 0
        self.won = False
        self.lost = False

        self.btn_restart = IconBtn(WIDTH - 140, 14, 50, "reload", (55, 145, 205))
        self.btn_menu = IconBtn(WIDTH - 78, 14, 50, "home", (215, 70, 65))

        self.btn_modal_again = IconBtn(WIDTH // 2 - 115, HEIGHT // 2 + 90, 64, "reload", (46, 180, 95))
        self.btn_modal_trophy = IconBtn(WIDTH // 2 - 32, HEIGHT // 2 + 90, 64, "trophy", (225, 150, 20))
        self.btn_modal_menu = IconBtn(WIDTH // 2 + 51, HEIGHT // 2 + 90, 64, "home", (215, 70, 65))

        self.build_bricks(stg)

    def build_bricks(self, stg):
        cols = 11
        rows = 7
        bw, bh = 68, 26
        gap = 6
        start_x = (WIDTH - (cols * bw + (cols - 1) * gap)) // 2
        start_y = 120

        for r in range(rows):
            for c in range(cols):
                x = start_x + c * (bw + gap)
                y = start_y + r * (bh + gap)
                col = BRICK_COLORS[r % len(BRICK_COLORS)]
                hp = 1
                is_bomb = False

                if stg == 1:
                    if r == 0:
                        hp = 2
                    if r == 3 and c in (3, 7):
                        is_bomb = True
                elif stg == 2:
                    if abs(c - cols // 2) > r + 1:
                        continue
                    if r == rows - 1:
                        hp = 2
                    if r == 3 and c == cols // 2:
                        is_bomb = True
                elif stg == 3:
                    if 2 <= r <= 4 and 3 <= c <= 7:
                        if r == 3 and c in (4, 6):
                            is_bomb = True
                        elif r == 3 and c == 5:
                            hp = 3
                        else:
                            continue
                    elif r in (0, 6) or c in (0, cols - 1):
                        hp = 2
                elif stg == 4:
                    if (r + c) % 2 == 1 and r not in (0, rows - 1):
                        hp = 2
                    if r in (2, 4) and c in (2, 5, 8):
                        is_bomb = True
                    elif r == 0:
                        hp = 3

                self.bricks.append(Brick(x, y, bw, bh, col, hp, is_bomb))

    def add_particles(self, x, y, color, count=18):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def explode_bomb(self, bomb):
        self.shake = 16
        bx, by = bomb.rect.center
        self.waves.append(Shockwave(bx, by, (255, 200, 60)))
        self.add_particles(bx, by, (255, 140, 30), 38)
        for b in self.bricks[:]:
            if b != bomb and math.hypot(b.rect.centerx - bx, b.rect.centery - by) < 115:
                self.score += 100
                self.add_particles(b.rect.centerx, b.rect.centery, b.color, 12)
                self.bricks.remove(b)

    def hit_brick(self, brick, is_fire=False):
        if brick not in self.bricks:
            return
        if is_fire or brick.is_bomb:
            brick.hp = 0
        else:
            brick.hp -= 1

        if brick.hp <= 0:
            self.bricks.remove(brick)
            self.combo += 1
            self.score += 50 * min(8, self.combo)
            cx, cy = brick.rect.center
            self.waves.append(Shockwave(cx, cy, brick.color))
            self.add_particles(cx, cy, brick.color, 20)

            if brick.is_bomb:
                self.explode_bomb(brick)

            if random.random() < 0.24:
                kind = random.choice(["multi", "fire", "laser", "wide", "life"])
                self.powerups.append(PowerUp(cx, cy, kind))
        else:
            self.add_particles(brick.rect.centerx, brick.rect.centery, (220, 230, 245), 7)

    def apply_powerup(self, kind):
        now = pygame.time.get_ticks()
        px, py = self.paddle_x, self.paddle_y - 28
        if kind == "multi":
            self.float_texts.append(FloatText(px, py, "MULTI-BALL!", (80, 220, 255)))
            active = [b for b in self.balls if not b.stuck]
            base = active[0] if active else self.balls[0]
            base.stuck = False
            if len(self.balls) < 9:
                self.balls.append(Ball(base.x, base.y, -5.5, -6.2, False))
                self.balls.append(Ball(base.x, base.y, 5.5, -6.2, False))
        elif kind == "fire":
            self.fire_until = now + 7000
            self.float_texts.append(FloatText(px, py, "FIREBALL!", (255, 130, 40)))
        elif kind == "laser":
            self.laser_until = now + 8000
            self.float_texts.append(FloatText(px, py, "LASER!", (215, 110, 255)))
        elif kind == "wide":
            self.wide_until = now + 10000
            self.float_texts.append(FloatText(px, py, "WIDE PADDLE!", (70, 245, 130)))
        elif kind == "life":
            self.lives = min(5, self.lives + 1)
            self.float_texts.append(FloatText(px, py, "+1 LIFE!", (255, 95, 135)))

    def handle_key(self, event):
        if self.state == "name_input":
            if event.key == pygame.K_RETURN:
                if not self.player_name.strip():
                    self.player_name = "Player"
                self.start_game(self.pending_stage)
            elif event.key == pygame.K_ESCAPE:
                self.state = "menu"
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            else:
                if len(self.player_name) < 14 and event.unicode.isprintable():
                    self.player_name += event.unicode
        elif self.state == "playing":
            if event.key == pygame.K_SPACE:
                for b in self.balls:
                    b.stuck = False
            elif event.key == pygame.K_r:
                self.ask_name(self.stage)
            elif event.key == pygame.K_m:
                self.state = "menu"

    def click(self, pos):
        if self.state == "name_input":
            if self.btn_name_ok.rect.collidepoint(pos):
                if not self.player_name.strip():
                    self.player_name = "Player"
                self.start_game(self.pending_stage)
            elif self.btn_name_cancel.rect.collidepoint(pos):
                self.state = "menu"
            return

        if self.state == "scoreboard":
            if self.btn_board_home.rect.collidepoint(pos):
                self.state = "menu"
                return
            if self.btn_board_clear.rect.collidepoint(pos):
                self.clear_records()
                return
            for rect, m, _ in self.filter_tabs:
                if rect.collidepoint(pos):
                    self.filter_mode = m
                    return
            return

        if self.state == "menu":
            if self.btn_menu_trophy.rect.collidepoint(pos):
                self.filter_mode = 0
                self.state = "scoreboard"
                return
            for sc in self.stage_cards:
                if sc.rect.collidepoint(pos):
                    self.ask_name(sc.stage_id)
                    break

        elif self.state == "playing":
            if self.won or self.lost:
                if self.btn_modal_again.rect.collidepoint(pos):
                    self.ask_name(self.stage)
                elif self.btn_modal_trophy.rect.collidepoint(pos):
                    self.filter_mode = self.stage
                    self.state = "scoreboard"
                elif self.btn_modal_menu.rect.collidepoint(pos):
                    self.state = "menu"
                return

            if self.btn_restart.rect.collidepoint(pos):
                self.ask_name(self.stage)
                return
            if self.btn_menu.rect.collidepoint(pos):
                self.state = "menu"
                return

            for b in self.balls:
                b.stuck = False

    def update(self):
        self.bg_fx.update()

        if self.shake > 0:
            self.shake -= 1

        if self.state != "playing" or self.won or self.lost:
            return

        now = pygame.time.get_ticks()
        self.elapsed = (now - self.start_ticks) // 1000

        target_w = 195 if now < self.wide_until else 135
        self.paddle_w += (target_w - self.paddle_w) * 0.2

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.paddle_x -= 9
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.paddle_x += 9
        else:
            mx, _ = pygame.mouse.get_pos()
            self.paddle_x += (mx - self.paddle_x) * 0.35

        half_w = int(self.paddle_w // 2)
        self.paddle_x = max(35 + half_w, min(WIDTH - 35 - half_w, int(self.paddle_x)))
        paddle_rect = pygame.Rect(int(self.paddle_x - half_w), self.paddle_y, int(self.paddle_w), self.paddle_h)

        if now < self.laser_until and now - self.last_laser > 280:
            self.last_laser = now
            self.lasers.append(Laser(paddle_rect.left + 10, paddle_rect.top))
            self.lasers.append(Laser(paddle_rect.right - 10, paddle_rect.top))

        for ls in self.lasers[:]:
            ls.update()
            if ls.rect.bottom < 85:
                self.lasers.remove(ls)
                continue
            for br in self.bricks[:]:
                if ls.rect.colliderect(br.rect):
                    self.hit_brick(br, False)
                    if ls in self.lasers:
                        self.lasers.remove(ls)
                    break

        is_fire = now < self.fire_until

        for b in self.balls[:]:
            b.update(self.paddle_x, self.paddle_y)
            if b.stuck:
                continue

            ball_rect = pygame.Rect(int(b.x - b.r), int(b.y - b.r), b.r * 2, b.r * 2)
            if b.vy > 0 and ball_rect.colliderect(paddle_rect):
                b.y = paddle_rect.top - b.r
                offset = (b.x - self.paddle_x) / max(1.0, half_w)
                speed = min(10.5, math.hypot(b.vx, b.vy) * 1.015)
                ang = offset * 1.15
                b.vx = speed * math.sin(ang)
                b.vy = -abs(speed * math.cos(ang))
                self.combo = 0

            for br in self.bricks[:]:
                if ball_rect.colliderect(br.rect):
                    if not is_fire:
                        ov_l = ball_rect.right - br.rect.left
                        ov_r = br.rect.right - ball_rect.left
                        ov_t = ball_rect.bottom - br.rect.top
                        ov_b = br.rect.bottom - ball_rect.top
                        m_ov = min(ov_l, ov_r, ov_t, ov_b)
                        if m_ov in (ov_l, ov_r):
                            b.vx = -b.vx
                        else:
                            b.vy = -b.vy
                    self.hit_brick(br, is_fire)
                    break

            if b.y - b.r > HEIGHT:
                self.balls.remove(b)

        if not self.balls:
            self.lives -= 1
            self.fire_until = 0
            self.laser_until = 0
            if self.lives <= 0:
                self.lost = True
            else:
                self.balls.append(Ball(self.paddle_x, self.paddle_y - 12, 5.2, -6.5, stuck=True))

        for pu in self.powerups[:]:
            pu.update()
            if pu.rect.colliderect(paddle_rect):
                self.apply_powerup(pu.kind)
                self.powerups.remove(pu)
            elif pu.rect.top > HEIGHT:
                self.powerups.remove(pu)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        for wv in self.waves[:]:
            wv.update()
            if wv.life <= 0:
                self.waves.remove(wv)

        for ft in self.float_texts[:]:
            ft.update()
            if ft.life <= 0:
                self.float_texts.remove(ft)

        if not self.bricks and not self.won:
            self.won = True
            stars = 3 if self.lives >= 3 else (2 if self.lives == 2 else 1)
            self.score += self.lives * 300
            self.save_record(self.score, max(1, self.elapsed), stars)

    def draw_paddle(self, surface, now):
        half_w = int(self.paddle_w // 2)
        px = int(self.paddle_x - half_w)
        py = self.paddle_y
        pw = int(self.paddle_w)
        ph = self.paddle_h

        flame_h = random.randint(8, 16)
        pygame.draw.polygon(surface, (255, 130, 30), [(px + 22, py + ph), (px + 36, py + ph), (px + 29, py + ph + flame_h)])
        pygame.draw.polygon(surface, (255, 130, 30), [(px + pw - 36, py + ph), (px + pw - 22, py + ph), (px + pw - 29, py + ph + flame_h)])

        p_rect = pygame.Rect(px, py, pw, ph)
        p_col = (195, 75, 255) if now < self.laser_until else (45, 185, 255)
        pygame.draw.rect(surface, p_col, p_rect, border_radius=10)
        pygame.draw.rect(surface, (180, 240, 255), (px + 10, py + 3, pw - 20, 5), border_radius=3)
        pygame.draw.rect(surface, (255, 255, 255), p_rect, 2, border_radius=10)

        if now < self.laser_until:
            pygame.draw.rect(surface, (255, 220, 70), (px + 6, py - 8, 8, 8), border_radius=2)
            pygame.draw.rect(surface, (255, 220, 70), (px + pw - 14, py - 8, 8, 8), border_radius=2)

    def draw_scoreboard(self, surface):
        self.bg_fx.draw(surface)
        board = pygame.Rect(60, 50, WIDTH - 120, HEIGHT - 100)
        pygame.draw.rect(surface, (18, 28, 58), board, border_radius=26)
        pygame.draw.rect(surface, (85, 185, 255), board, 4, border_radius=26)

        title = self.big_font.render("HALL OF FAME", True, (255, 225, 70))
        surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 78))

        self.btn_board_home.draw(surface)
        self.btn_board_clear.draw(surface)

        for rect, m, label in self.filter_tabs:
            active = self.filter_mode == m
            col = (55, 150, 235) if active else (32, 50, 90)
            pygame.draw.rect(surface, col, rect, border_radius=10)
            pygame.draw.rect(surface, (120, 200, 255), rect, 2, border_radius=10)
            txt = self.font.render(label, True, (255, 255, 255))
            surface.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        headers = [("RANK", 145), ("PLAYER", 300), ("STAGE", 470), ("SCORE", 605), ("TIME", 745)]
        for h_text, hx in headers:
            ht = self.font.render(h_text, True, (140, 205, 255))
            surface.blit(ht, (hx - ht.get_width() // 2, 218))
        pygame.draw.line(surface, (60, 110, 180), (100, 245), (WIDTH - 100, 245), 2)

        filtered = [r for r in self.records if self.filter_mode == 0 or r.get("stage") == self.filter_mode]
        filtered.sort(key=lambda r: (-r["score"], r["time"]))

        if not filtered:
            empty_txt = self.med_font.render("No records yet! Play a stage to claim 1st place!", True, (140, 180, 230))
            surface.blit(empty_txt, (WIDTH // 2 - empty_txt.get_width() // 2, HEIGHT // 2 + 20))
        else:
            for idx, rec in enumerate(filtered[:9]):
                ry = 258 + idx * 56
                row_rect = pygame.Rect(100, ry, WIDTH - 200, 46)
                r_bg = (55, 75, 125) if idx == 0 else (30, 46, 84)
                r_bd = (255, 215, 55) if idx == 0 else (70, 110, 175)

                pygame.draw.rect(surface, r_bg, row_rect, border_radius=10)
                pygame.draw.rect(surface, r_bd, row_rect, 2, border_radius=10)

                if idx < 3:
                    draw_medal(surface, 145, ry + 23, idx + 1)
                else:
                    rk = self.med_font.render(f"{idx + 1}", True, (180, 215, 255))
                    surface.blit(rk, (145 - rk.get_width() // 2, ry + 9))

                p_txt = self.med_font.render(str(rec["name"]), True, (255, 255, 255))
                m_txt = self.font.render(f"Stage {rec.get('stage', 1)}", True, (150, 210, 255))
                s_txt = self.med_font.render(str(rec["score"]), True, (70, 245, 140))
                t_txt = self.med_font.render(f"{rec['time']}s", True, (255, 195, 70))

                surface.blit(p_txt, (300 - p_txt.get_width() // 2, ry + 9))
                surface.blit(m_txt, (470 - m_txt.get_width() // 2, ry + 13))
                surface.blit(s_txt, (605 - s_txt.get_width() // 2, ry + 9))
                surface.blit(t_txt, (745 - t_txt.get_width() // 2, ry + 9))

    def draw(self, surface):
        if self.state == "scoreboard":
            self.draw_scoreboard(surface)
            return

        ox = random.randint(-5, 5) if self.shake > 0 else 0
        oy = random.randint(-5, 5) if self.shake > 0 else 0
        self.bg_fx.draw(surface, ox, oy)

        if self.state in ("menu", "name_input"):
            self.btn_menu_trophy.draw(surface)

            banner = pygame.Rect(WIDTH // 2 - 295, 62, 590, 118)
            pygame.draw.rect(surface, (8, 12, 28), (banner.x + 5, banner.y + 7, banner.w, banner.h), border_radius=26)
            pygame.draw.rect(surface, (25, 42, 85), banner, border_radius=26)
            pygame.draw.rect(surface, (95, 210, 255), banner, 4, border_radius=26)

            shd = self.big_font.render("BRICK BREAKER", True, (10, 18, 40))
            title = self.big_font.render("BRICK BREAKER", True, (255, 225, 65))
            surface.blit(shd, (WIDTH // 2 - title.get_width() // 2 + 3, 98))
            surface.blit(title, (WIDTH // 2 - title.get_width() // 2, 95))

            if self.records:
                top_c = self.records[0]
                c_rect = pygame.Rect(WIDTH // 2 - 225, 200, 450, 44)
                pygame.draw.rect(surface, (35, 55, 105), c_rect, border_radius=14)
                pygame.draw.rect(surface, (255, 215, 0), c_rect, 2, border_radius=14)
                draw_medal(surface, c_rect.x + 26, c_rect.centery, 1)
                c_txt = self.font.render(
                    f"1st Place: {top_c['name']}  ({top_c['score']} pts in {top_c['time']}s)",
                    True,
                    (255, 235, 130),
                )
                surface.blit(c_txt, (c_rect.x + 52, c_rect.centery - c_txt.get_height() // 2))

            for sc in self.stage_cards:
                stg = sc.stage_id
                sc.draw(surface, self.font, self.best_stars[stg], self.best_scores[stg])

            if self.state == "name_input":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 12, 25, 210))
                surface.blit(overlay, (0, 0))

                modal = pygame.Rect(WIDTH // 2 - 230, HEIGHT // 2 - 150, 460, 300)
                pygame.draw.rect(surface, (28, 44, 82), modal, border_radius=24)
                pygame.draw.rect(surface, (85, 195, 255), modal, 4, border_radius=24)

                pr = self.med_font.render(f"ENTER NAME  (STAGE {self.pending_stage})", True, (255, 225, 80))
                surface.blit(pr, (WIDTH // 2 - pr.get_width() // 2, modal.y + 30))

                box = pygame.Rect(WIDTH // 2 - 170, HEIGHT // 2 - 35, 340, 56)
                pygame.draw.rect(surface, (15, 24, 48), box, border_radius=12)
                pygame.draw.rect(surface, (100, 210, 255), box, 3, border_radius=12)

                cursor = "|" if (pygame.time.get_ticks() // 400) % 2 == 0 else ""
                ntxt = self.med_font.render(self.player_name + cursor, True, (255, 255, 255))
                surface.blit(ntxt, (box.centerx - ntxt.get_width() // 2, box.centery - ntxt.get_height() // 2))

                self.btn_name_ok.draw(surface)
                self.btn_name_cancel.draw(surface)

        elif self.state == "playing":
            arena = pygame.Rect(30, 80, WIDTH - 60, HEIGHT - 90)
            pygame.draw.rect(surface, (80, 185, 255), arena, 3, border_radius=14)

            hud = pygame.Rect(30, 12, 730, 54)
            pygame.draw.rect(surface, (22, 36, 70), hud, border_radius=14)
            pygame.draw.rect(surface, (80, 175, 250), hud, 2, border_radius=14)

            stat = self.med_font.render(
                f"{self.player_name}   |   Stage {self.stage}   |   Score: {self.score}   |   Time: {self.elapsed}s",
                True,
                (255, 255, 255),
            )
            surface.blit(stat, (48, hud.centery - stat.get_height() // 2))

            for i in range(self.lives):
                draw_heart(surface, 660 + i * 30, hud.centery, 10, (255, 65, 95))

            self.btn_restart.draw(surface)
            self.btn_menu.draw(surface)

            for br in self.bricks:
                br.draw(surface)

            for wv in self.waves:
                wv.draw(surface)

            for pu in self.powerups:
                pu.draw(surface)

            for ls in self.lasers:
                ls.draw(surface)

            now = pygame.time.get_ticks()
            self.draw_paddle(surface, now)

            is_fire = now < self.fire_until
            for b in self.balls:
                b.draw(surface, is_fire)

            for p in self.particles:
                p.draw(surface)

            for ft in self.float_texts:
                ft.draw(surface)

            if any(b.stuck for b in self.balls) and not self.won and not self.lost:
                tip = self.font.render("Click Mouse or Press SPACE to Launch Ball", True, (180, 225, 255))
                surface.blit(tip, (WIDTH // 2 - tip.get_width() // 2, HEIGHT - 108))

            if self.won or self.lost:
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((8, 12, 26, 210))
                surface.blit(overlay, (0, 0))

                modal = pygame.Rect(WIDTH // 2 - 225, HEIGHT // 2 - 180, 450, 360)
                pygame.draw.rect(surface, (28, 45, 86), modal, border_radius=24)
                pygame.draw.rect(surface, (95, 195, 255), modal, 4, border_radius=24)

                if self.won:
                    win = self.big_font.render("STAGE CLEAR!", True, (75, 245, 130))
                    surface.blit(win, (WIDTH // 2 - win.get_width() // 2, modal.y + 28))

                    stars = 3 if self.lives >= 3 else (2 if self.lives == 2 else 1)
                    for i in range(3):
                        scol = (255, 215, 0) if i < stars else (55, 75, 115)
                        draw_star(surface, WIDTH // 2 - 75 + i * 75, modal.y + 120, 26, scol)

                    s_txt = self.med_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
                    m_txt = self.font.render(f"Finished in: {self.elapsed}s   |   Lives: {self.lives}", True, (170, 215, 255))
                else:
                    lose = self.big_font.render("GAME OVER!", True, (255, 75, 85))
                    surface.blit(lose, (WIDTH // 2 - lose.get_width() // 2, modal.y + 35))

                    s_txt = self.med_font.render(f"Score: {self.score}", True, (255, 255, 255))
                    m_txt = self.font.render("All balls lost! Try again!", True, (255, 160, 160))

                surface.blit(s_txt, (WIDTH // 2 - s_txt.get_width() // 2, modal.y + 175))
                surface.blit(m_txt, (WIDTH // 2 - m_txt.get_width() // 2, modal.y + 220))

                self.btn_modal_again.draw(surface)
                self.btn_modal_trophy.draw(surface)
                self.btn_modal_menu.draw(surface)


def main():
    game = Game()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.click(event.pos)
            elif event.type == pygame.KEYDOWN:
                game.handle_key(event)

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()