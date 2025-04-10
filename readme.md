# Lord Of The Rings Lukas Cut
This script creates a cut of the Lord of the Rings trilogy of movies designed for use with Davinci Resolve. The first Lukas Cut release is set to cut frames based on the Blu Ray 1080p extended edition, but cuts may be tuned for the 4k, theatrical, DVD, or fan cuts in future releases.
### Status
* Lord of the Rings the Fellowship of the Ring - Rough cut, no transitions
* Lord of the Rings the Two Towers - First pass cut, not reviewed, no transitions
* Lord of the Rings the Return of the King - not started
## Instructions for use
* Install Davinci Resolve (This script is tested on 18)
* Copy the script into the following directory:
> C:\ProgramData\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Edit\buildTimeline.py 
* Make script rule changes appropriate for your audience (or just leave it alone)
* Ensure the script is set for your version of the film (future feature)
* Add your Lord of the Rings film to the media pool
* If you have a separate sound track, add to media pool second
* Go to the menu Workspace -> Scripts -> Edit -> buildTimeline
## Using your generated timeline
Once you've generated your timeline, you can do whatever you want with it. You can make your own edits, add or remove more scenes, update the movie's color grading. Then you'll want to export the generated cut to a file, choosing your desired quality. More details on this can be found at the Davinci website:
(https://www.blackmagicdesign.com/products/davinciresolve/training) and download "Delivering Content".

## Rules/Definitions for the cut and how to use them
Each category in the script has a definition to make the cut more objective on what is considered scary, violent, etc. Those definitions are as follows:
### Violence
* 0 - No violence, this cut is G rated. Swords can be seen, but not used
* 1 - There is fighting, either with swords, or bare hands
### Scary
* 0 - No scary action or creature that would bother a child. G rated
* 1 - Something that may cause children to be scared, but may be less mild than a violent scene
### Orcs
* 0 - Minimal or no orcs in the scene. Children are unlikely to be bothered
* 1 - Orcs in present in the scene and may scare children
### Nasgul
* 0 - Minimal or no Nasgul. Children are unlikely to be bothered
* 1 - Nasgul are present in the scene and may scare children
### How to use the rules
When making a cut for yourself, you can choose the max value used to generate your timeline based on the descriptions above. This creates a movie talored to your child's age and comfort level, and allows the Lukas Cut to grow with your child.

## FAQ
### I'm getting an error when I try to export or deliver my video in Davinci Resolve
I've had this problem when my media is a large file >20G over the network while running on a laptop. I'm not sure if the problem was SMB, bandwidth/latency, or laptop memory, but I used shutter encoder to encode a lower bit rate locally to my laptop and then use that as my source media with no problems. Please let me know if you find the source for this type of case.
