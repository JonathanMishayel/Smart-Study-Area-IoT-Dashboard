# Smart-Study-Area-IoT-Dashboard
A real-time IoT-based climate monitoring system that collects temperature and humidity data using an ESP32 + DHT22 sensor, transmits it via MQTT, and visualizes it through an interactive Dash + Plotly web dashboard.

This project demonstrates end-to-end integration of IoT hardware, real-time data streaming, and data visualization engineering

---
### 🚀 Project Overview

This system continuously monitors environmental conditions in a study area and provides live analytics through a professional dashboard.

#### Data Flow Architecture
```text

DHT22 Sensor 
      ↓
ESP32 Microcontroller 
      ↓ (WiFi)
MQTT Broker (test.mosquitto.org)
      ↓
Python Dash Dashboard
      ↓
Interactive Visual Analytics
````
### Key Features

#### 📡 IoT Layer

ESP32 microcontroller

DHT22 temperature & humidity sensor

WiFi connectivity

Real-time MQTT publishing

Auto-reconnection handling

#### 📊 Dashboard Layer (Dash + Plotly)

Live-updating gauges (Temperature & Humidity)

Real-time time-series line charts

Correlation heatmap analysis

Statistical summary (min, max, average)

Professional UI using Dash Bootstrap Components

MQTT connection status indicator

Automatic data buffering
----
### 🛠 Technologies Used
##### Hardware

ESP32

DHT22 Sensor

##### Communication

MQTT Protocol

test.mosquitto.org Public Broker

##### Software

- Python 3.x

- Dash

- Plotly

- Pandas

- Paho-MQTT

- Dash Bootstrap Components

----
📊 Dashboard Preview

<img width="1919" height="893" alt="Dashboard_UI_" src="https://github.com/user-attachments/assets/bcc4dc70-a13a-48e1-8d8f-04951aef989a" />



