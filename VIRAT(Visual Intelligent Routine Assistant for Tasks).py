# V.I.R.A.T. (Visual Intelligent Routine Assistant for Tasks)
import pygame
import serial
import time
from datetime import datetime

pygame.mixer.init()
ser = serial.Serial('COM3', 115200)

# Schedule
schedule = [
    {"task": "Practise DSA", "deadline": "09:30"},
    {"task": "Study Python", "deadline": "13:30"},
    {"task": "Read OB Notes", "deadline": "18:30"}
]

def printSchedule():
    print("\nVIRAT: Today's Schedule")
    for idx, item in enumerate(schedule):
        print(f" {idx + 1}. {item['deadline']}: {item['task']}")

def play_audio():
    try:
        hour = datetime.now().hour
        if hour < 12:
            audio_file = "morning.mp3"
        elif 12 <= hour < 16:
            audio_file = "afternoon.mp3"
        else:
            audio_file = "evening.mp3"

        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("VIRAT: Audio error:", e)

def blink_lights():
    for _ in range(5):
        ser.write(b'BLINK\n')
        time.sleep(0.5)

def get_nearest_task():
    now = datetime.now()
    upcoming_tasks = []
    for item in schedule:
        deadline = datetime.strptime(item["deadline"], "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )
        if deadline > now:
            upcoming_tasks.append((deadline, item))

    if not upcoming_tasks:
        return None

    # Sort by time and pick the earliest
    nearest = min(upcoming_tasks, key=lambda x: x[0])
    return nearest[1], (nearest[0] - now).total_seconds()

lights_on = False
last_greet_time = 0
greet_cooldown = 10  # seconds
schedule_shown = False  # Flag to avoid repeated printing

print("VIRAT: Listening for motion and study button...")

while True:
    line = ser.readline().decode(errors="ignore").strip()
    print("ESP32 says:", line)

    now = time.time()

    # Motion-based light ON and greeting
    if "Motion detected" in line and "ON" in line:
        if now - last_greet_time > greet_cooldown:
            print("VIRAT: Motion detected — greeting user.")
            play_audio()
            last_greet_time = now
        else:
            print("VIRAT: Motion detected — greeting skipped (cooldown).")
        if not lights_on:
            lights_on = True  # Lights turned on by motion
            if not schedule_shown:
                printSchedule()
                schedule_shown = True

    if "Motion detected" in line and "OFF" in line:
        lights_on = False  # Reset flag when lights go off
        schedule_shown = False  # Reset schedule display for next ON event

    # Study mode can only activate if lights are already on
    if "Button pressed" in line:
        if lights_on:
            print("\nVIRAT: Study mode activated.")
            task_info = get_nearest_task()

            if not task_info:
                print("VIRAT: No upcoming tasks.")
                continue

            selected_task, time_remaining = task_info

            print(f"VIRAT: Starting task '{selected_task['task']}' until {selected_task['deadline']} "
                  f"({int(time_remaining // 60)} minutes left).")

            ser.write(b'LIGHT ON\n')
            time.sleep(time_remaining)
            blink_lights()
            lights_on = False
            schedule_shown = False
        else:
            print("VIRAT: Study button ignored — lights are OFF.")
