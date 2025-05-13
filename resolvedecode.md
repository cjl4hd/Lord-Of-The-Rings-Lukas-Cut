# Davinci Resolve Decode Support
Davinci Resolve will occasionally have issues with h264 decoding. This covers an exploration of which encode settings are incompatible. 
## Setup
I am using Handbrake 1.9.2 (2025022300) and importing to DR 18.5 for this review. I chose 4 minutes of video (44:00 to 48:00 of Fellowship) to encode. I tuned the encoder level and profile. In DR I set "Stop playback when a dropped frame is detected." to TRUE.
