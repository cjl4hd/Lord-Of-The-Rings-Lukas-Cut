# Lord Of The Rings Lukas Cut
This script creates a cut of the Lord of the Rings trilogy of movies designed for use with Davinci Resolve. The goal of this cut is to reduce violence and scary scenes to make it suitable for younger audiences. The script removes these scenes without moving or adding to the original cut to preserve the original feel of the movies as much as possible. The current Lukas Cut release is set to cut frames based on the Blu Ray 1080p extended edition, but cuts may be tuned for the 4k, theatrical, DVD, or fan cuts in future releases.
### Status
* Lord of the Rings the Fellowship of the Ring - Rough cut, no transitions
* Lord of the Rings the Two Towers - Rough cut, no transitions
* Lord of the Rings the Return of the King - Rough cut, no transitions
## High Level Instructions for use
* Install Davinci Resolve (This script is tested on 18)
* Copy the script into the following directory:
> C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Edit\buildTimeline.py 
* Make script rule changes appropriate for your audience (or just leave it alone)
* Ensure the script is set for your version of the film (future feature)
* Add your Lord of the Rings film to the media pool
* If you have a separate sound track, add to media pool second
* Go to the menu Workspace -> Scripts -> Edit -> buildTimeline
## Detailed Workflow
Depending on where you get your digital copy of Lord of the Rings, it will have different encode settings and different codecs. Davinci Resolve can be picky about H264 inputs, so you may have to re-encode using better settings for import. If you're looking for a high quality output, Handbrake settings RF20 veryslow with all filters off has worked pretty well making a more compatible file without visible quality loss. When using Davinci Resolve Delivery for export, the ideal case is to add a x264 plugin to render the RF setting you want directly, as the x264 codec is more efficient than the H264 encoder in resolve. The challenge is that the x264 plugin is only given as source code, and if you're not familiar with Visual Studio, compiling may be challenging. Luckily there is a [Github repo](https://github.com/gdaswani/x264_encoder) that smooths this out. If using the resolve encoder, you likely want to export Best, as the others have visible quality loss. From there you can re-encode with Handbrake to RF 21 or 22 without much loss. This setup of many steps of re-encoding to get around Davinci Resolve limitations is not ideal, so getting a high quality input with compatible encoding and installing the plugin will both improve the efficiency and quality of your workflow.
### Detailed encode settings
Davinci Resolve's decoder doesn't like specific settings on H264 files. I'm currently looking into this, but there are a few things I've learned. If I'm in Handbrake 1.8.2 and use the default settings while changing RF and speed only, Davinci Resolve takes the output well. Possible problematic encoding settings are:
| Problematic Setting    | Description |
| -------- | ------- |
| bframes  | Specifies how many B-frames (bi-directionally predicted frames) can be used between I-frames and P-frames. 3 is a common value, and setting it higher than this may cause Resolve to struggle    |
| closed gop | When enabled, forces each GOP (Group of Pictures) to be self-contained, meaning no B-frames reference frames from the previous GOP. Disabling this may cause issues with Resolve     |
| keyint    | Sets the maximum interval between I-frames (in number of frames). A typical value is 250. Setting this to twice keyint-min may improve stability.   |
| keyint-min    | Sets the minimum interval between I-frames. A typical value is 25.    |

There are also helpful settings to tune for your use case that shouldn't impact Davinci Resolve's ability to decode, but are helpful to know, also for encoding later:
| Setting    | Description |
| -------- | ------- |
| preset | Controls speed vs. compression efficiency trade-off. Use the slowest setting you have the patience for, as it will produce better results  |
| tune | Tune allows you to optimize the encoder for specific content, for example for film, preserving grain, simpler decode, or zero latency for streaming |
| crf | Constant Rate Factor manages the quality of your result. Lower is higher efficiency but takes longer. For 1080p, Handbrake recommends 20-24 |
## Using your generated timeline
Once you've generated your timeline, you can do whatever you want with it. You can make your own edits, add or remove more scenes, update the movie's color grading. Then you'll want to export the generated cut to a file, choosing your desired quality. More details on this can be found at the Davinci website:
(https://www.blackmagicdesign.com/products/davinciresolve/training) and download "Delivering Content".

## Rules/Definitions for the cut and how to use them
Each category in the script has a definition to make the cut more objective on what is considered scary, violent, etc. Those definitions are as follows:
### Violence
* Level 0 (None to Mild): Scenes with little to no violence, such as peaceful dialogues or non-threatening environments. Swords can be seen, but not used
* Level 1 (Moderate): Scenes with some action or peril, including minor battles or threats.
* Level 2 (Intense): Scenes with graphic violence, intense battles, or significant peril.
### Scary
* 0 - No scary action or creature that would bother a child. G rated
* 1 - Something that may cause children to be scared, but may be less mild than a violent scene
### Orcs
* 0 - Minimal or no orcs in the scene. Orcs in the scene are only shown briefly, or at a distance. Children are unlikely to be bothered
* 1 - Orcs in present in the scene and may scare children
### Nasgul
* 0 - Minimal or no Nasgul. Children are unlikely to be bothered
* 1 - Nasgul are present in the scene and may scare children
### How to use the rules
When making a cut for yourself, you can choose the max value used to generate your timeline based on the descriptions above. This creates a movie talored to your child's age and comfort level, and allows the Lukas Cut to grow with your child.

## FAQ
### I'm getting an error when I try to export or deliver my video in Davinci Resolve
I've had this problem when my media is a large file >20G over the network while running on a laptop. I'm not sure if the problem was SMB, bandwidth/latency, or laptop memory, but I used shutter encoder to encode a lower bit rate locally to my laptop and then use that as my source media with no problems. Please let me know if you find the source for this type of case.
