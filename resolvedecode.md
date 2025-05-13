# Davinci Resolve Decode Support
Davinci Resolve will occasionally have issues with h264 decoding. This covers an exploration of which encode settings are incompatible. 
## Setup
I am using Handbrake 1.9.2 (2025022300) and importing to DR 18.5 for this review. I chose 4 minutes of video (44:00 to 48:00 of Fellowship) to encode. I tuned the encoder level and profile. In DR I set "Stop playback when a dropped frame is detected." to TRUE. I made a series of short cuts, some being a few seconds, and others being less than a second, to test how DR handles the encoded frames.

| Encoder Profile | Encoder Level | Playback | Render |
| ---- | ---- | ---- | ---- |
| Main | 4 | PASS | PASS |
| Main | 4.1 | ---- | ---- |
| High | 4 | ---- | ---- |
| Main | 5 | ------- | ---- |
| Main | 5.1 | ------- | ---- |
| Main | 5.2 | ------- | ---- |
| Main | 6 | ------- | ---- |
| Main | 6.1 | ------- | ---- |
| Main | 6.2 | FAIL | PASS |

### Profile Conclusions
Using profiles without modified settings will consistently yield a working decode. Skipped frames in playback are likely due to my older laptop CPU. To determine the cause of my failed decode I'll have to dig deeper.

## Media Info and Encode Settings
I've reviewed two files that are the same video source, but with different encode settings. In reference to problematic settings, a Reddit source said: "reducing the bframes from 8 to 3, switching to closed gop. X264 keyint is also 250, I would have that as twice the keyint-min (46 or 48) as a test."
To evaluate this, I used Media Info to view the encode settings for both the problematic file and working one. Here is what I found:
- bframes: both sources use bframes=8, so I don't expect this to always be a problem
- open_gop: Both sources use open_gop=0, so while this may be a problem, there is another problem in my media

I then compared the rest of the settings and found these differences:
| Problematic file | Working file |
| ---------------- | ------------ |
| deblock=1:-3:-3 / me=tesa /me_range=48 / fast_pskip=0 / chroma_qp_offset=-4 / sliced_threads=0 / decimate=0 / keyint=250 / keyint_min=23 / rc=2pass / bitrate=12895 / ratetol=1.0 / cplxblur=20.0 / qblur=0.5 / vbv_maxrate=38000 / vbv_bufsize=30000 / aq=1:0.80 | deblock=1:0:0 / me=umh / me_range=24 / fast_pskip=1 / chroma_qp_offset=-2 / lookahead_threads=1 / sliced_threads=0 / decimate=1 / keyint=240 / keyint_min=24 / rc=crf / crf=20.0 / vbv_maxrate=25000 / vbv_bufsize=31250 / crf_max=0.0 / filler=0 / aq=1:1.00 |
