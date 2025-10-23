import tkinter as tk
import random
import time
import threading
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import csv
import os

# --- Data Storage ---
temperature_data = []
humidity_data = []
timestamps = []
csv_file = "silkworm_data.csv"

# Simulation variables
simulated_temp = 25.0
simulated_hum = 77.0

# PID Controller variables
target_temp = 25.0
Kp, Ki, Kd = 0.5, 0.01, 0.1
integral, previous_error = 0, 0
dt = 2  # update interval in seconds

# --- Load historical data safely ---
if os.path.isfile(csv_file):
    with open(csv_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ts = row.get("Timestamp") or row.get("timestamp") or row.get("Time") or row.get("time")
            temp = row.get("Temperature (°C)") or row.get("Temp") or row.get("temperature")
            hum = row.get("Humidity (%)") or row.get("Hum") or row.get("humidity")
            if ts and temp and hum:
                timestamps.append(ts)
                temperature_data.append(float(temp))
                humidity_data.append(float(hum))
    if len(timestamps) > 30:
        timestamps = timestamps[-30:]
        temperature_data = temperature_data[-30:]
        humidity_data = humidity_data[-30:]

# --- Save Data to CSV ---
def save_data(temp, hum):
    file_exists = os.path.isfile(csv_file)
    with open(csv_file, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Temperature (°C)", "Humidity (%)"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"{temp:.2f}", f"{hum:.2f}"])

# --- Silkworm Health Calculation ---
def calculate_health(temp, hum):
    temp_score = max(0, 100 - abs(temp - 25)*10)
    hum_score = max(0, 100 - abs(hum - 77)*5)
    health_score = (temp_score + hum_score) / 2
    return int(health_score)

def feeding_behavior(health_score):
    if health_score > 80:
        return "Feeding Normally 🍽️"
    elif health_score > 50:
        return "Reduced Feeding ⚠️"
    else:
        return "Minimal Feeding ❌"

def cocoon_yield(health_score):
    if health_score > 80:
        return "High Yield 🟢"
    elif health_score > 50:
        return "Medium Yield 🟡"
    else:
        return "Low Yield 🔴"

# --- Manual Controls ---
def turn_on_heater():
    global simulated_temp
    simulated_temp += 1

def turn_on_fan():
    global simulated_temp
    simulated_temp -= 1

def turn_on_humidifier():
    global simulated_hum
    simulated_hum += 2

# --- Monitor Environment ---
def monitor_environment():
    global simulated_temp, simulated_hum, integral, previous_error
    while True:
        temp = simulated_temp + random.uniform(-0.5, 0.5)
        hum = simulated_hum + random.uniform(-1, 1)

        # PID Automatic Temperature Control
        error = target_temp - temp
        integral += error * dt
        derivative = (error - previous_error) / dt
        output = Kp*error + Ki*integral + Kd*derivative
        simulated_temp += output * 0.1
        previous_error = error

        timestamps.append(datetime.now().strftime("%H:%M:%S"))
        temperature_data.append(temp)
        humidity_data.append(hum)
        if len(timestamps) > 30:
            timestamps.pop(0)
            temperature_data.pop(0)
            humidity_data.pop(0)

        # Determine system status
        if temp > 28:
            status = "⚠️ Fan ON (Too Hot)"
            color = "red"
        elif temp < 23:
            status = "❄️ Heater ON (Too Cold)"
            color = "blue"
        elif hum < 70:
            status = "💧 Humidifier ON (Low Humidity)"
            color = "#0288d1"
        else:
            status = "✅ Stable Conditions"
            color = "green"

        # Silkworm health simulation
        health_score = calculate_health(temp, hum)
        label_health.config(text=f"Silkworm Health: {health_score}/100")
        label_feeding.config(text=f"Feeding Behavior: {feeding_behavior(health_score)}")
        label_yield.config(text=f"Cocoon Yield: {cocoon_yield(health_score)}")

        # Update UI
        label_temp_val.config(text=f"{temp:.2f} °C", fg=color)
        label_hum_val.config(text=f"{hum:.2f} %", fg=color)
        label_status.config(text=status, fg=color)
        label_time.config(text=f"Last Updated: {datetime.now().strftime('%H:%M:%S')}")

        # Update Graph
        update_graph()

        # Save data
        save_data(temp, hum)

        time.sleep(dt)

# --- Update Graph ---
def update_graph():
    ax.clear()
    ax.plot(timestamps, temperature_data, label="Temperature (°C)", color="red", linewidth=2)
    ax.plot(timestamps, humidity_data, label="Humidity (%)", color="blue", linewidth=2)
    ax.set_xlabel("Time")
    ax.set_ylabel("Value")
    ax.set_title("Real-Time Temperature & Humidity", fontsize=12, fontweight='bold')
    ax.legend(loc="upper right")
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    canvas.draw()

# --- GUI Setup ---
root = tk.Tk()
root.title("Climora - Silkworm Environment Monitoring System")
root.geometry("1100x600")
root.config(bg="#f5f5f5")

# Header
header_frame = tk.Frame(root, bg="#4caf50", height=60)
header_frame.pack(fill="x")
header_label = tk.Label(header_frame, text="🐛 Silkworm Environment Monitoring 🐛",
                        bg="#4caf50", fg="white", font=("Arial", 18, "bold"))
header_label.pack(pady=10)

# Main Frame
main_frame = tk.Frame(root, bg="#f5f5f5")
main_frame.pack(fill="both", expand=True, padx=20, pady=10)

# Left Panel - Live Readings & Controls
left_panel = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
left_panel.pack(side="left", fill="y", padx=10, pady=10, ipadx=20, ipady=20)

tk.Label(left_panel, text="Live Environment Readings", bg="white", fg="#2e7d32",
         font=("Arial", 14, "bold")).pack(pady=10)

tk.Label(left_panel, text="Temperature:", bg="white", font=("Arial", 12)).pack()
label_temp_val = tk.Label(left_panel, text="-- °C", bg="white", font=("Arial", 16, "bold"))
label_temp_val.pack(pady=5)

tk.Label(left_panel, text="Humidity:", bg="white", font=("Arial", 12)).pack()
label_hum_val = tk.Label(left_panel, text="-- %", bg="white", font=("Arial", 16, "bold"))
label_hum_val.pack(pady=5)

tk.Label(left_panel, text="System Status:", bg="white", font=("Arial", 12)).pack(pady=10)
label_status = tk.Label(left_panel, text="Waiting for Data...", bg="white",
                        font=("Arial", 12, "italic"), fg="gray")
label_status.pack()

label_time = tk.Label(left_panel, text="Last Updated: --:--:--", bg="white",
                      font=("Arial", 10), fg="gray")
label_time.pack(pady=10)

# Silkworm Health & Behavior
label_health = tk.Label(left_panel, text="Silkworm Health: --/100", bg="white", font=("Arial", 12))
label_health.pack(pady=5)
label_feeding = tk.Label(left_panel, text="Feeding Behavior: --", bg="white", font=("Arial", 12))
label_feeding.pack(pady=5)
label_yield = tk.Label(left_panel, text="Cocoon Yield: --", bg="white", font=("Arial", 12))
label_yield.pack(pady=5)

# Manual Controls - Styled
tk.Label(left_panel, text="Manual Controls", bg="white", font=("Arial", 12, "bold")).pack(pady=10)

btn_frame = tk.Frame(left_panel, bg="white")
btn_frame.pack(pady=5)

tk.Button(btn_frame, text="❄️ Heater ON", command=turn_on_heater,
          bg="#ff8a65", fg="white", font=("Arial", 12, "bold"), width=15).grid(row=0, column=0, padx=5, pady=5)
tk.Button(btn_frame, text="🌬️ Fan ON", command=turn_on_fan,
          bg="#4fc3f7", fg="white", font=("Arial", 12, "bold"), width=15).grid(row=0, column=1, padx=5, pady=5)
tk.Button(btn_frame, text="💧 Humidifier ON", command=turn_on_humidifier,
          bg="#81c784", fg="white", font=("Arial", 12, "bold"), width=15).grid(row=1, column=0, columnspan=2, pady=5)

# Right Panel - Graph
right_panel = tk.Frame(main_frame, bg="white", bd=2, relief="groove")
right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

fig, ax = plt.subplots(figsize=(8, 4))
canvas = FigureCanvasTkAgg(fig, master=right_panel)
canvas.get_tk_widget().pack(fill="both", expand=True, pady=10)

# Footer
footer_frame = tk.Frame(root, bg="#388e3c", height=30)
footer_frame.pack(fill="x")
tk.Label(footer_frame, text="© 2025 Central Silk Board | Prototype by Mohammed Kaif",
         bg="#388e3c", fg="white", font=("Arial", 10)).pack(pady=5)

# --- Start Monitoring Thread ---
t = threading.Thread(target=monitor_environment)
t.daemon = True
t.start()

root.mainloop()
