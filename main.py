"""Asset setup helpers for the Xiaomei running animation project."""

from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from typing import Any

import pygame
import requests


PROJECT_DIR = Path(__file__).resolve().parent
ASSETS_DIR = PROJECT_DIR / "assets"
COMMONS_API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "XiaomeiRunningAnimation/1.0 (educational project)"
ALLOWED_LICENSES = ("cc0", "public domain")
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
TRACK_CENTER_X = 400
TRACK_CENTER_Y = 330
TRACK_RADIUS_X = 260
TRACK_RADIUS_Y = 130


def _commons_candidates(search_term: str, mime_prefix: str) -> list[dict[str, Any]]:
    """Return Commons files with an explicit public-domain or CC0 license."""
    response = requests.get(
        COMMONS_API,
        params={
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": search_term,
            "gsrnamespace": 6,
            "gsrlimit": 10,
            "prop": "imageinfo",
            "iiprop": "url|mime|extmetadata",
        },
        headers={"User-Agent": USER_AGENT},
        timeout=12,
    )
    response.raise_for_status()
    pages = response.json().get("query", {}).get("pages", {}).values()
    candidates = []
    for page in pages:
        info_list = page.get("imageinfo", [])
        if not info_list:
            continue
        info = info_list[0]
        if not info.get("mime", "").startswith(mime_prefix):
            continue
        license_name = info.get("extmetadata", {}).get("LicenseShortName", {}).get("value", "")
        if license_name.lower() in ALLOWED_LICENSES:
            candidates.append(info)
    return candidates


def _draw_girl(destination: Path) -> None:
    image = pygame.Surface((120, 160), pygame.SRCALPHA)
    ink = (67, 48, 55)
    skin = (255, 211, 176)

    pygame.draw.line(image, skin, (48, 112), (38, 145), 9)
    pygame.draw.line(image, skin, (72, 112), (83, 145), 9)
    pygame.draw.line(image, (247, 115, 139), (38, 145), (29, 149), 8)
    pygame.draw.line(image, (247, 115, 139), (83, 145), (94, 149), 8)
    pygame.draw.ellipse(image, (99, 169, 214), (34, 78, 52, 51))
    pygame.draw.polygon(image, (247, 115, 139), [(37, 87), (83, 87), (60, 119)])
    pygame.draw.line(image, skin, (34, 88), (20, 108), 8)
    pygame.draw.line(image, skin, (86, 88), (100, 105), 8)
    pygame.draw.ellipse(image, skin, (18, 102, 8, 8))
    pygame.draw.ellipse(image, skin, (96, 100, 8, 8))
    pygame.draw.ellipse(image, (112, 68, 46), (31, 17, 59, 71))
    pygame.draw.ellipse(image, skin, (37, 27, 47, 55))
    pygame.draw.ellipse(image, (112, 68, 46), (32, 18, 58, 29))
    pygame.draw.ellipse(image, (112, 68, 46), (31, 33, 15, 49))
    pygame.draw.ellipse(image, (112, 68, 46), (74, 33, 15, 49))
    pygame.draw.circle(image, ink, (52, 52), 3)
    pygame.draw.circle(image, ink, (69, 52), 3)
    pygame.draw.ellipse(image, (249, 143, 151), (40, 59, 11, 6))
    pygame.draw.ellipse(image, (249, 143, 151), (69, 59, 11, 6))
    pygame.draw.arc(image, (183, 84, 92), (53, 56, 15, 12), math.pi, 2 * math.pi, 2)
    pygame.draw.circle(image, (255, 220, 105), (60, 27), 8)
    pygame.draw.circle(image, (255, 244, 190), (60, 27), 4)
    pygame.image.save(image, str(destination))


def _download_music(destination: Path) -> bool:
    try:
        for info in _commons_candidates("filetype:audio happy instrumental music mp3", "audio/mpeg"):
            response = requests.get(
                info["url"], headers={"User-Agent": USER_AGENT}, timeout=20
            )
            response.raise_for_status()
            if len(response.content) < 1024:
                continue
            destination.write_bytes(response.content)
            return True
    except (requests.RequestException, KeyError, OSError):
        pass
    return False


def _synthesize_music(destination: Path) -> None:
    """Write a cheerful five-second melody as a standard PCM WAV file."""
    sample_rate = 22050
    duration = 5.0
    melody = (523.25, 659.25, 783.99, 659.25, 587.33, 698.46, 880.0, 698.46)
    samples = bytearray()
    for index in range(int(sample_rate * duration)):
        time = index / sample_rate
        note = melody[int(time / 0.625) % len(melody)]
        envelope = min(1.0, (time % 0.625) * 18, (0.625 - time % 0.625) * 12)
        tone = math.sin(2 * math.pi * note * time)
        harmony = math.sin(2 * math.pi * note * 1.5 * time) * 0.22
        value = int(9000 * envelope * (tone * 0.72 + harmony))
        samples.extend(struct.pack("<h", value))

    with wave.open(str(destination), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(samples)


def prepare_assets() -> dict[str, Path]:
    """Ensure character and music assets exist; return the paths to load."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    girl_path = ASSETS_DIR / "girl.png"
    if not girl_path.is_file() or girl_path.stat().st_size == 0:
        _draw_girl(girl_path)

    mp3_path = ASSETS_DIR / "music.mp3"
    wav_path = ASSETS_DIR / "music.wav"
    if mp3_path.is_file() and mp3_path.stat().st_size > 0:
        music_path = mp3_path
    elif wav_path.is_file() and wav_path.stat().st_size > 0:
        music_path = wav_path
    elif _download_music(mp3_path):
        music_path = mp3_path
    else:
        _synthesize_music(wav_path)
        music_path = wav_path

    return {"girl": girl_path, "music": music_path}


def draw_playground(surface: pygame.Surface) -> None:
    """Draw the grass field and red oval running track."""
    surface.fill((89, 166, 91))
    for y in range(0, SCREEN_HEIGHT, 36):
        pygame.draw.line(surface, (94, 171, 96), (0, y), (SCREEN_WIDTH, y), 18)

    outer_track = pygame.Rect(100, 165, 600, 330)
    inner_track = pygame.Rect(180, 235, 440, 190)
    pygame.draw.ellipse(surface, (191, 76, 69), outer_track)
    for inset in (12, 30, 48, 66):
        lane = outer_track.inflate(-inset * 2, -inset)
        pygame.draw.ellipse(surface, (237, 192, 157), lane, 2)
    pygame.draw.ellipse(surface, (73, 151, 83), inner_track)

    field_center_y = TRACK_CENTER_Y
    pygame.draw.line(surface, (192, 218, 174), (400, 246), (400, 414), 2)
    pygame.draw.ellipse(surface, (192, 218, 174), (365, field_center_y - 35, 70, 70), 2)
    pygame.draw.circle(surface, (239, 225, 172), (400, field_center_y), 4)


def draw_runner(
    surface: pygame.Surface, img: pygame.Surface, angle: float
) -> tuple[float, float, float]:
    """Draw the runner on the oval and return its x, y, and scale."""
    x = TRACK_CENTER_X + TRACK_RADIUS_X * math.cos(angle)
    y = TRACK_CENTER_Y + TRACK_RADIUS_Y * math.sin(angle)
    far_y = TRACK_CENTER_Y - TRACK_RADIUS_Y
    near_y = TRACK_CENTER_Y + TRACK_RADIUS_Y
    depth = max(0.0, min(1.0, (y - far_y) / (near_y - far_y)))
    scale = 0.6 + 0.4 * depth

    width = max(1, round(img.get_width() * scale))
    height = max(1, round(img.get_height() * scale))
    runner = pygame.transform.smoothscale(img, (width, height))
    runner_rect = runner.get_rect(center=(round(x), round(y)))
    surface.blit(runner, runner_rect)
    return x, y, scale


def load_chinese_font(size: int = 28) -> pygame.font.Font:
    """Load a common Chinese font, falling back to Pygame's default font."""
    if not pygame.font.get_init():
        pygame.font.init()

    font_paths = (
        Path("C:/Windows/Fonts/msjh.ttc"),
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simsun.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("/System/Library/Fonts/PingFang.ttc"),
        Path("/System/Library/Fonts/STHeiti Medium.ttc"),
        Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
        Path("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"),
    )
    for font_path in font_paths:
        if font_path.is_file():
            try:
                return pygame.font.Font(str(font_path), size)
            except pygame.error:
                continue

    for font_name in ("Microsoft JhengHei", "Microsoft YaHei", "SimHei", "Noto Sans CJK TC"):
        matched_path = pygame.font.match_font(font_name)
        if matched_path:
            return pygame.font.Font(matched_path, size)
    return pygame.font.Font(None, size)


def run() -> None:
    """Run the endless Xiaomei animation until the user exits."""
    pygame.init()
    assets = prepare_assets()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("小美在跑步")
    clock = pygame.time.Clock()
    title_font = load_chinese_font(30)
    prompt_font = load_chinese_font(20)
    runner_image = pygame.image.load(str(assets["girl"])).convert_alpha()

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(assets["music"]))
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    angle = 0.0
    running = True
    try:
        while running:
            delta_time = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                running = False

            if not running:
                break

            angle += delta_time * 1.0
            draw_playground(screen)
            draw_runner(screen, runner_image, angle)

            title = title_font.render("小美在跑步", True, (255, 255, 245))
            title_rect = title.get_rect(topright=(SCREEN_WIDTH - 28, 24))
            screen.blit(title, title_rect.move(1, 2))
            screen.blit(title, title_rect)

            prompt = prompt_font.render(
                "按 ESC 鍵停止並關閉畫面", True, (255, 255, 245)
            )
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24))
            screen.blit(prompt, prompt_rect.move(1, 2))
            screen.blit(prompt, prompt_rect)

            pygame.display.flip()
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        pygame.quit()


def run_three_laps() -> None:
    """Run until Xiaomei completes three laps, then wait for the user to exit."""
    pygame.init()
    assets = prepare_assets()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("小美跑三圈")
    clock = pygame.time.Clock()
    title_font = load_chinese_font(30)
    count_font = load_chinese_font(18)
    prompt_font = load_chinese_font(20)
    runner_image = pygame.image.load(str(assets["girl"])).convert_alpha()

    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(str(assets["music"]))
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

    total_angle = 3 * math.tau
    progress_angle = 0.0
    lap_count = 0
    finished = False
    running = True
    try:
        while running:
            delta_time = clock.tick(60) / 1000.0
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                running = False

            if not running:
                break

            if not finished:
                progress_angle = min(progress_angle + delta_time, total_angle)
                lap_count = min(3, int(progress_angle / math.tau + 1e-9))
                if progress_angle >= total_angle:
                    finished = True
                    if pygame.mixer.get_init():
                        pygame.mixer.music.stop()

            draw_playground(screen)
            draw_runner(screen, runner_image, progress_angle % math.tau)

            title_text = title_font.render("小美跑了三圈", True, (255, 255, 245))
            title_rect = title_text.get_rect(topright=(SCREEN_WIDTH - 28, 24))
            screen.blit(title_text, title_rect.move(1, 2))
            screen.blit(title_text, title_rect)

            count_text = count_font.render(f"第{lap_count}圈", True, (255, 255, 245))
            count_rect = count_text.get_rect(bottomleft=(24, SCREEN_HEIGHT - 24))
            screen.blit(count_text, count_rect.move(1, 2))
            screen.blit(count_text, count_rect)

            prompt = prompt_font.render(
                "按 ESC 關閉畫面", True, (255, 255, 245)
            )
            prompt_rect = prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24))
            screen.blit(prompt, prompt_rect.move(1, 2))
            screen.blit(prompt, prompt_rect)

            pygame.display.flip()
    finally:
        if pygame.mixer.get_init():
            pygame.mixer.music.stop()
        pygame.quit()

# 原本只能跑 run.py，改成可以選擇跑 run() 或 run_three_laps()
def main() -> None:
    while True:
        choice = input(
            "請選擇動畫模式：\n"
            "1. 無限跑步 (run)\n"
            "2. 跑三圈 (run_three_laps)\n"
            "3. 離開\n"
            "請輸入 1、2 或 3（直接按 Enter 預設 1）："
        ).strip()
        if choice in ("", "1"):
            run()
        elif choice == "2":
            run_three_laps()
        elif choice == "3":
            print("程式已結束。")
            return
        else:
            print("輸入無效，請輸入 1、2 或 3。")


if __name__ == "__main__":
    main()