# BlindSpot

## The Problem

Over 2 billion people live with visual impairment. Current aids like white canes offer limited spatial awareness and no real-time object context.

## The Solution

BlindSpot is a wearable assistive system that uses a Raspberry Pi 4B with a camera module to detect nearby obstacles in real time. A YOLOv8 model, optimised for edge inference using NCNN, identifies objects such as people, furniture, stairs, walls, and elevation changes from the live camera feed.

Detected objects are classified by type and spatial position. Based on proximity and horizontal placement within the frame, the system triggers distinct vibration patterns through five haptic motors, communicating both what the obstacle is and which direction it is coming from — left, centre, or right.

A SvelteKit web app running on the same network connects to a FastAPI server on the Pi, allowing real-time configuration of detection parameters without restarting the system.

## Stack

Raspberry Pi 4B · YOLOv8 NCNN · Picamera2 · Python · lgpio · FastAPI · SvelteKit
