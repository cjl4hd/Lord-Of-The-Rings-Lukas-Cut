#Running in resolve 18.5
#Sources for documentation:
#https://resolvedevdoc.readthedocs.io/en/latest/index.html
#https://diop.github.io/davinci-resolve-api/#/


#If running outside of resolve:
#from python_get_resolve import GetResolve
#resolve = GetResolve()

#object setup
projectManager = resolve.GetProjectManager() #resolve is defined when you're running the script inside the program
current_db = projectManager.GetCurrentDatabase()
currentProject = projectManager.GetCurrentProject()
media_pool = currentProject.GetMediaPool()
root_folder = media_pool.GetRootFolder()

#CREATE TIMELINES
#Note: If a timeline with this name exists, it will be overwritten
#create source timeline if we want to merge audio. This may be common with a surround sound source and free Davinci resolve.
#You'll want to use ffmpeg or shutter encoder to re-encode the audio to an mp3 or codec of your choice. Merge them back together
#in your new source timeline.
media_pool.CreateEmptyTimeline('Source Timeline')
source_timeline = currentProject.GetCurrentTimeline()

media_pool.CreateEmptyTimeline('New Generated Timeline')
generated_timeline = currentProject.GetCurrentTimeline()

media_pool.CreateEmptyTimeline('Deleted Scenes Timeline')
deleted_scenes_timeline = currentProject.GetCurrentTimeline()

#by getting clip list after creating timelines, we get pointers to the timelines we created
clip_list = root_folder.GetClipList()

#At this time, we expect the media pool to look like the following:
#media_pool[0] = input video
#media_pool[1] = input audio (optional)
#media_pool[2] = source timeline
#media_pool[3] = generated timeline
#media_pool[4] = deleted scenes timeline

#load file to media pool if not already there

#create switches for building timeline
#Movieselection = 0 for fellowship, 1 for two towers, 2 for return of the king
movieSelection = 1

#Violence
#0 = no violence
#1 = weapons
#2 = fighting
#3 = blood
#4 = death
maxViolence = 0

#Scary
#0 = nothing scary
#4 = very scary
maxscary = 0

#Orcs
#0 = no orcs
#1 = orcs
#2 = orcs fighting, chasing
maxOrcs = 0

#Nasgul
#0 = no nasgul
#1 = nasgul
#2 = nasgul fighting, chasing
maxNasgul = 0

#Audio remux
#enable this if you want to add your own audio. Common if your version of LOTR is DTS. 
#Two ways to get audio are 1) convert to stereo or 2) convert to PWM surround using shutter encoder (ffmpeg)
#and bring the audio into your media pool. This option will pull the audio back into your cut
audioRemux = 1

#Input media version
#0 = extended 1080p blu-ray
inputMedia = 0

#Create data structure from switches
#This is the key component to the build script. Each cut contains data for describing how child friendly it is.
#From that, you can choose how much you want to remove from the final cut.
#startFrame, endFrame, violence, scary, orcs, nasgul, notes
#[0,1000,0-4,0-4,0-2,0-2,"string"]
fellowshipCuts = [
    #                Violence
    #                | Scary
    #                | | Orcs
    #                | | | Nasgul
    #                v v v v
    [0,     2769    ,0,0,0,0,"intro map"],
    [2770,  3260    ,0,1,0,0,"sauron with ring"],
    [3261,  6780    ,1,1,0,0,"shire burning, battle with sauron"],
    [6781,  7847    ,0,1,0,0,"ring with elf"],
    [7848,  8132    ,0,0,0,0,"ring being lost"],
    [8133,  9565    ,0,0,0,0,"golem intro"],
    [9566,  10720   ,0,0,0,0,"bilbo with golem"],
    [10721, 46288   ,0,0,0,0,"Shire, frodo, gandolf"],
    [46289, 47199   ,0,1,0,0,"Minas morgel"],
    [47200, 49399   ,0,0,0,0,"gandolf goes to minas tirith"],
    [49400, 50151   ,0,1,0,0,"black riders"],
    [50152, 57736   ,0,0,0,0,"hobbiton"],
    [57737, 58022   ,0,1,0,0,"golem torture"],
    [58023, 58171   ,0,0,0,0,"shire,bilbo, but that would lead them here"],
    [58172, 58297   ,0,1,0,0,"black rider with sword"],
    [58298, 62072   ,0,1,0,0,"take it gandolf, you must; samwise trimming the verge"],
    [62073, 67234   ,0,0,0,0,"frodo sam walking, ends with black horse"],
    [67235, 72517   ,0,0,0,0,"Gandolf visits Saurmon, ends with saurumon waving staff"],
    [72518, 73874   ,1,1,0,0,"fandolf sauromn fight"],
    [73875, 77510   ,0,0,0,0,"mary pipin join, ends with hobbits under tree"],
    [77511, 82717   ,0,1,0,0,"black rider above tree, ends at ferry"],
    [82718, 89247   ,0,0,0,0,"hobbits at bree, ends with frodo puting on ring"],
    [89248, 89964   ,0,0,0,0,"black riders, frodo in wraith world"],
    [89965, 91022   ,0,0,0,0,"frodo takes off ring, questioned by srtider"],
    [91023, 91245   ,0,0,0,0,"hobbits burst in, strider shows sword"],
    [91246, 91383   ,0,0,0,0,"hobbits talk to strider"],
    [91384, 93150   ,1,1,0,0,"black riders enter bree"],
    [93151, 99105   ,0,0,0,0,"hobbits wake up in bree, heading towards rivendel"],
    [99106, 100091   ,0,1,1,0,"Sauron introduces orcs"],
    [100092, 100758  ,0,0,0,0,"gandolf on top of tower"],
    [100759, 101194  ,0,1,1,0,"more orcs cutting trees"],
    [101195, 103126   ,0,0,0,0,"gandolf on tower, ends with hobbits on weathrtop looking down"],
    [103127, 107512   ,1,1,0,0,"weathertop fight scene"],
    [107513, 108259   ,0,0,0,0,"frodo in pain, strider carying him"],
    [108260, 108939   ,0,0,0,0,"Isenguard fly through"],
    [108940, 109929   ,0,0,0,0,"Moth flys to gandalf"],
    [109930, 111885   ,0,0,1,0,"Isenguard fly through, orc army"],
    [111886, 115943   ,0,0,0,0,"stone trolls, frodo struggles"],
    [115944, 119952   ,0,1,0,0,"Galadriel with black riders, ends with them swept away"],
    [119953, 122529   ,0,0,0,0,"Rivendel, ends iwth i was delayed"],
    [122530, 123051   ,1,1,0,0,"saurumon and gandolf fight again"],
    [123052, 123796   ,0,0,0,0,"gandolf flys away"],
    [123797, 132201   ,0,0,0,0,"rivendel, ends with elrond telling story"],
    [132202, 133432   ,0,0,0,0,"Sauron finger cut, isildor says no"],
    [133433, 159637   ,0,0,0,0,"rivendel, fellowship trek"],
    [159638, 164472   ,0,0,0,0,"fellowship eating, practicing swords, ravens, hiking into the mountains"],
    [164473, 169391   ,0,0,0,0,"Isengaurd fly through, mountain ice fall"],
    [169392, 176211   ,0,0,0,0,"walk towards moria, ends with its a tomb"],
    [176212, 178283   ,0,1,0,0,"skeletons, goblins, sea monster"],
    [178284, 192637   ,0,0,0,0,"door crumbles, ends with arrow towards borimir"],
    [192638, 200317   ,1,1,1,0,"tomb fight, ending with troll dying"],
    [200318, 202613   ,0,0,0,0,"checking on Frodo, ends in hall with orcs"],
    [202614, 203371   ,0,1,1,0,"hall of orcs, ending with orcs running"],
    [203372, 206267   ,0,0,0,0,"hear balrog, running to stairs"],
    [206268, 209317   ,1,1,1,0,"running from orcs to balrog battle"],
    [209318, 209749   ,0,1,0,0,"running from balrog"],
    [209750, 210144   ,0,0,0,0,"crossing bridge"],
    [210145, 211694   ,1,1,0,0,"gandolf fights balrog"],
    [211695, 212240   ,0,0,0,0,"gandolf looks down, falls to floor"],
    [212241, 212336   ,0,1,0,0,"gandolf falls from bridge"],
    [212337, 217107   ,0,0,0,0,"frodo says no, fellowship sad"],
    [217108, 217462   ,0,0,0,0,"Elf arrows in the forest"],
    [217463, 233872   ,0,0,0,0,"caras galathon"],
    [233873, 234633   ,1,1,0,0,"seeing well, fires in hobbiton"],
    [234634, 238719   ,0,0,0,0,"caras galathon"],
    [238720, 241122   ,0,1,1,0,"Isengaurd"],
    [241123, 249909   ,0,0,0,0,"leaving caras galathon"],
    [249910, 250859   ,0,1,1,0,"oracai chasing"],
    [250860, 262462   ,0,0,0,0,"fellowship boats, landing, borimir and frodo"],
    [262463, 262829   ,0,1,0,0,"frodo sees the eye"],
    [262830, 264970   ,0,0,0,0,"frodo aragorn talk"],
    [264971, 279530   ,0,1,1,0,"oracai fight, boromir dies"],
    [279531, 328271   ,0,0,0,0,"frodo leaves, movie ends"]
    
]

twotowersCuts = [
    #                  Violence
    #                  | Scary
    #                  | | Orcs
    #                  | | | Nasgul
    #                  v v v v
    [0,      2545     ,0,0,0,0,"Mountains pan"],
    [2546,   5492     ,1,1,0,0,"Gandolf fights balrog"],
    [5493,   14138    ,0,0,0,0,"Frodo wakes, walking with sam"],
    [14139,  16060    ,0,1,0,0,"Frodo sam fight golem"],
    [16061,  21216    ,0,0,0,0,"Frodo sam walk with golem"],
    [21217,  24612    ,0,0,1,0,"mary pipin with orcs"],
    [24613,  27717    ,0,0,0,0,"aragorn, gimli, legolas trailing orcs"],
    [27718,  28968    ,0,0,0,0,"Isenguard fly through 2 towers"],
    [28969,  31717    ,0,1,0,0,"Orcs cutting trees, builing army"],
    [31718,  32823    ,0,0,0,0,"Rohan intro, preparnig for attack"],
    [32824,  33175    ,1,1,0,0,"Orcs attack Rohan"],
    [33176,  39056    ,0,0,0,0,"Riders of R see orcs, find wounded men, ends with banished"],
    [39057,  40354    ,0,0,1,0,"Orcs with AGL chasing"],
    [40355,  44637    ,0,1,1,0,"Orcs with MP"],
    [44638,  45310    ,1,1,1,0,"Riders find orcs and attack"],
    [45311,  51439    ,0,0,0,0,"Riders talk with AGL"],
    [51440,  55086    ,0,1,1,0,"AGL find orc pile"],
    [55087,  60111    ,0,0,1,0,"MP in fangorn, meet treebeard"],
    [60112,  66923    ,0,0,0,0,"FSG walking"],
    [66924,  67578    ,0,1,0,0,"Frodo falls into water, sees spirits"],
    [67579,  73118    ,0,0,0,1,"FSG walking, see nasgul"],
    [73119,  77578    ,0,0,0,0,"AGL in fangorn, see white wizard"],
    [77579,  78109    ,1,1,0,0,"Wizard fighting balrog"],
    [78110,  83900    ,0,0,0,0,"Gandalf in time, returns until task is done, shadowfax"],
    [83901,  87275    ,0,0,0,0,"MP with treebeard"],
    [87276,  90347    ,0,0,0,0,"AGLG talking"],
    [90348,  97964    ,0,0,0,0,"FSG at black gate"],
    [97965,  104575    ,0,0,0,0,"MP in fangorn"],
    [104576, 113891    ,0,0,0,0,"AGLG in Rohan"],
    [113892, 114288    ,1,0,0,0,"AGLG fight with Rohan men and wormtongue"],
    [114289, 125976    ,0,0,0,0,"Gandalf frees King Theoden"],
    [125977, 133079    ,0,0,0,0,"Rohan prep to leave for helms deep"],
    [133080, 135245    ,0,0,0,0,"Saurumon and wormtongue"],
    [135246, 138656    ,0,0,0,0,"Leaving Rohan"],
    [138657, 139570    ,0,0,1,0,"Saurumon and wormtongue plotting"],
    [139571, 150546    ,0,0,0,0,"FSG walking see elephants"],
    [150547, 152969    ,1,1,0,0,"Faramir's men attack elephants, catch FS"],
    [152970, 153305    ,0,0,0,0,"Faramir takes FS"],
    [153306, 165931    ,0,0,0,0,"AGL guide rohan to helms deep"],
    [165932, 172230    ,1,1,1,0,"Wargs attack rohan people, aragorn falls"],
    [172231, 178954    ,0,0,0,0,"Rohan people make it to helms deep"],
    [178955, 181148    ,0,1,1,0,"Saurumon shows wormtongue his army"],
    [181149, 190627    ,0,0,0,0,"Treebeard walks, aragorn survives, Rivendel"],
    [190628, 191054    ,0,1,0,0,"Saurumon,orcs march, sauron watches"],
    [191055, 216364    ,0,0,0,0,"FS taken to Faramir's hideout"],
    [216365, 224354    ,0,0,0,0,"Aragorn sees army, helms deep prepares"],
    [224355, 242030    ,0,0,0,0,"Treebeard gathering, helms prep, elves join"],
    [242031, 248810    ,1,1,0,0,"Battle of Helm's Deep"],
    [248811, 251137    ,0,0,0,0,"Treebeard too slow"],
    [251138, 256055    ,1,1,0,0,"Battle of helms"],
    [256056, 258576    ,0,0,0,0,"Ents decided to do nothing"],
    [258577, 267267    ,1,1,0,0,"Helms deep"],
    [267268, 269307    ,0,0,0,0,"Grabeard walking to western forest, changes direction"],
    [269308, 273725    ,0,0,0,0,"FS taken out of hideout, Treebeard sees trees burnt"],
    [273726, 276686    ,0,0,0,0,"FS in los giliad"],
    [276687, 277369    ,0,1,0,1,"Nasgul in los giliad"],
    [277370, 277971    ,0,0,0,0,"Helms deep fortress gate defense"],
    [277972, 278010    ,0,1,1,0,"Orcs hit gate 1"],
    [278011, 278663    ,0,0,0,0,"Aragorn pep talk"],
    [278664, 278735    ,0,1,1,0,"Orcs hit gate 2"],
    [278736, 279044    ,0,0,0,0,"Women and children make for the mountain pass"],
    [279045, 279073    ,0,1,1,0,"orcs hit gate 3"],
    [279074, 280920    ,0,0,0,0,"Ride out with me, for Rohan"],
    [280921, 284046    ,0,1,1,0,"orcs hit gate, battle"],
    [284047, 287555    ,0,0,0,0,"Ents attack Isenguard"],
    [287556, 291647    ,1,1,1,1,"Frodo walks to Nasgul, fighting continues"],
    [291648, 294781    ,0,0,0,0,"Sam narrarates while isenguard falls"],
    [294782, 294899    ,0,0,1,0,"Orcs retreat to fangorn"],
    [294900, 295654    ,0,0,0,0,"Aragorn watches orcs die in fangorn"],
    [295655, 296627    ,0,1,1,0,"Gimli, Legolas clear orc bodies"],
    [296628, 338660    ,0,0,0,0,"MP take control of Isenguard"],


]
returnofthekingCuts = []

#select cuts from file switches
if movieSelection == 0:
    selectedCuts = fellowshipCuts
elif movieSelection == 1:
    selectedCuts = twotowersCuts
else:
    selectedCuts = returnofthekingCuts

#Verify data structure
    #each item goes from frame A to at least frame A+1
    #ensure no frames missing, frames in order
prev_item = next_item = None
l = len(selectedCuts)
for index,cuts in enumerate(selectedCuts):
    #set up prev and next
    if index > 0:
        prev_item = selectedCuts[index - 1]
    else:
        prev_item = None
    if index < (l - 1):
        next_item = selectedCuts[index + 1]
    else:
        next_item = None
    #ensure that cuts[0] < cuts[1]
    if cuts[0] >= cuts[1]:
        print("Error! Cut \""+cuts[6]+"\" startFrame is greater than endFrame")
    #ensure that cuts[1] = cuts+1[0] - 1
    if next_item != None:
        if cuts[1] != (next_item[0] - 1):
            print("Error! Cut \""+cuts[6]+"\" endFrame is not nextCut.startFrame - 1")

#loop through data structure, adding clips
    #“mediaPoolItem”
    #“startFrame” (int)
    #“endFrame” (int)
    #(optional) “mediaType” (int; 1 - Video only, 2 - Audio only)
    #media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[0], "startFrame": 0, "endFrame": 10, "mediaType": 2}])

    
#Populate source timeline
#add video
currentProject.SetCurrentTimeline(source_timeline)
media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[0], "recordFrame": 86400}])
#if necessary, add audio
if audioRemux == 1:
    #for some reason the timeline starts at hr=1, so appending to the beginning means frame 86400
    #in our case, we've set both the video and audio to recordFrame=0, that way the timeline frame numbers match the media pool frame numbers
    media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[1], "recordFrame": 86400}])
    #audiotrack = source_timeline.GetItemListInTrack("audio", 1)
    #clip = audiotrack[0]
    #clip.SetProperty("start", 0)

for cuts in selectedCuts:
    if cuts[2] <= maxViolence and cuts[3] <= maxscary and cuts[4] <= maxOrcs and cuts[5] <= maxNasgul:
        currentProject.SetCurrentTimeline(generated_timeline)
        media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[2], "startFrame": cuts[0], "endFrame": cuts[1]}])
    else:
        currentProject.SetCurrentTimeline(deleted_scenes_timeline)
        media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[2], "startFrame": cuts[0], "endFrame": cuts[1]}])
        print("cut \""+cuts[6]+"\" removed at frame "+str(cuts[0]))
#appends the first clip from root folder, frames 0 to 10, only audio.

print("Successfully generated timeline.")
