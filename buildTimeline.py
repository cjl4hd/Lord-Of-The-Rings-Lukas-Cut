#Running in resolve 18.5
#Sources for documentation:
#https://resolvedevdoc.readthedocs.io/en/latest/index.html
#https://diop.github.io/davinci-resolve-api/#/
#Fusion scripting:
#https://www.steakunderwater.com/wesuckless/viewtopic.php?t=4851
#https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf
#keyboard shortcuts:
#https://indiefilming.com/tutorials/keyboard-shortcuts-davinci-resolve
#x264 plugin: 
#BM Forum
#https://forum.blackmagicdesign.com/viewtopic.php?f=21&t=125570&hilit=Sergey+Mirontsev&start=100
#Github
#https://github.com/gdaswani/x264_encoder


#If running outside of resolve:
#from python_get_resolve import GetResolve
#resolve = GetResolve()

#Lets us simulate keypresses, this allows for transitions
import keyboard
import time

#Lets us notify when the script is finished
import winsound

#Experiment with resolve structure:
#print(dir(app))
#Go through itemsin resolve data structure:
#print(dir(resolve.GetProjectManager().GetCurrentProject().GetCurrentTimeline().GetCurrentVideoItem().GetDuration()))

#object setup
projectManager = resolve.GetProjectManager() #resolve is defined when you're running the script inside the program
current_db = projectManager.GetCurrentDatabase()
currentProject = projectManager.GetCurrentProject()
media_pool = currentProject.GetMediaPool()
root_folder = media_pool.GetRootFolder()

#TODO print info for GetName for the above objects to be Verbose

#CREATE TIMELINES
#Note: If a timeline with this name exists, it will be overwritten
#create source timeline if we want to merge audio. This may be common with a surround sound source and free Davinci resolve.
#You'll want to use ffmpeg or shutter encoder to re-encode the audio to an mp3 or codec of your choice. Merge them back together
#in your new source timeline.
#TODO detect existing timelines, if they exist, the generated timeline may fail
media_pool.CreateEmptyTimeline('Source Timeline')
source_timeline = currentProject.GetCurrentTimeline()
#TODO consider using media_pool.CreateTimelineFromClips("Source Timeline", clip_list)

media_pool.CreateEmptyTimeline('New Generated Timeline')
generated_timeline = currentProject.GetCurrentTimeline()

media_pool.CreateEmptyTimeline('Deleted Scenes Timeline')
deleted_scenes_timeline = currentProject.GetCurrentTimeline()

#by getting clip list after creating timelines, we get pointers to the timelines we created
clip_list = root_folder.GetClipList()

#At this point in the code, we expect the media pool to look like the following:
#media_pool[0] = input video, if there are 2 discs, we'll add a second in here, everything else increments
#media_pool[1] = input audio (optional)
#media_pool[2] = source timeline
#media_pool[3] = generated timeline
#media_pool[4] = deleted scenes timeline

#load file to media pool if not already there

#create switches for building timeline
#Movieselection = 0 for fellowship, 1 for two towers, 2 for return of the king
movieSelection = 0

#create deleted scenes for review
deleted_scenes = 0

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
audioRemux = 0

#Input media version
#0 = extended 1080p blu-ray, removed frames for intermission (single disk)
#1 = extended 1080p blu-ray, 2 disk version
inputMedia = 1

######################################################
# NO NEED TO EDIT BEYOND HERE FOR BASIC CUT GENERATION
######################################################

#Edit point status
#used for tracking the state of the edit point
#The edit point tells us whether a transition will be placed before, between, or after a cut
#this should aways be initialized to 0
editPointStatus = 0

#verbose mode prints more info and debug
#verbose = 1 gives general status
#verbose = 2 gived detailed functions
verbose = 2

#Audio transitions help the film transition more naturally but are more error prone,
#so we can turn them off if things aren't working or we're debugging
audioTransitions = 1

#Create data structure from switches
#This is the key component to the build script. Each cut contains data for describing how child friendly it is.
#From that, you can choose how much you want to remove from the final cut.
#startFrame, endFrame, violence, scary, orcs, nasgul, [transition, position], notes
#[0,1000,0-4,0-4,0-2,0-2,[1,0],"string"]
fellowshipCuts = [
    #                  Violence
    #                  | Scary
    #                  | | Orcs
    #                  | | | Nasgul
    #                  v v v v
    [0,     2769      ,0,0,0,0,[0,0],"intro map"],#will always have [0,0]
    [2770,  3260      ,0,1,0,0,[0,0],"Sauron with ring"],
    [3261,  6780      ,1,1,0,0,[0,0],"Shire burning, battle with Sauron"],
    [6781,  7847      ,0,1,0,0,[0,0],"ring with elf"],
    [7848,  8132      ,0,0,0,0,[1,0],"ring being lost"],
    [8133,  9565      ,0,0,0,0,[0,0],"Gollum intro"],
    [9566,  10720     ,0,0,0,0,[0,0],"Bilbo with Gollum"],
    [10721, 46288     ,0,0,0,0,[0,0],"Shire, Frodo, Gandalf"],
    [46289, 47199     ,0,1,0,0,[0,0],"Minas Morgul"],
    [47200, 49399     ,0,0,0,0,[1,-1],"Gandalf goes to Minas Tirith"],
    [49400, 50151     ,0,1,0,0,[0,0],"black riders"],
    [50152, 57736     ,0,0,0,0,[1,0],"Hobbiton"],
    [57737, 58022     ,0,1,0,0,[0,0],"Gollum torture"],
    [58023, 58171     ,0,0,0,0,[1,-1],"Shire, Bilbo, but that would lead them here"],
    [58172, 58297     ,0,1,0,0,[0,0],"black rider with sword"],
    [58298, 62072     ,0,0,0,0,[1,0],"take it Gandalf, you must; Samwise trimming the verge"],
    [62073, 67234     ,0,0,0,0,[0,0],"Frodo Sam walking, ends with black horse"],
    [67235, 72517     ,0,0,0,0,[0,0],"Gandalf visits Saruman, ends with Saruman waving staff"],
    [72518, 73874     ,1,1,0,0,[0,0],"Gandolf Saruman fight"],
    [73875, 77510     ,0,0,0,0,[1,1],"Merry Pippin join, ends with hobbits under tree"],
    [77511, 82717     ,0,1,0,0,[0,0],"black rider above tree, ends at ferry"],
    [82718, 89247     ,0,0,0,0,[1,1],"hobbits at Bree, ends with Frodo puting on ring"],
    [89248, 89964     ,0,0,0,0,[0,0],"black riders, Frodo in wraith world"],
    [89965, 91022     ,0,0,0,0,[0,0],"Frodo takes off ring, questioned by Strider"],
    [91023, 91245     ,0,0,0,0,[0,0],"hobbits burst in, Strider shows sword"],
    [91246, 91383     ,0,0,0,0,[0,0],"hobbits talk to Strider"],
    [91384, 93150     ,1,1,0,0,[0,0],"black riders enter Bree"],
    [93151, 99105     ,0,0,0,0,[1,0],"hobbits wake up in Bree, heading towards Rivendell"],
    [99106, 99674     ,0,0,0,0,[0,0],"Sauron talks with Saruman"],
    [99675, 100091    ,0,1,1,0,[0,0],"Saruman introduces orcs"],
    [100092, 100758   ,0,0,0,0,[1,0],"Gandalf on top of tower"],
    [100759, 101194   ,0,1,1,0,[0,0],"more orcs cutting trees"],
    [101195, 103126   ,0,0,0,0,[1,1],"Gandalf on tower, ends with hobbits on Weathertop looking down"],
    [103127, 107512   ,1,1,0,0,[0,0],"weathertop fight scene"],
    [107513, 108259   ,0,0,0,0,[1,0],"Frodo in pain, Strider carrying him"],
    [108260, 108939   ,0,0,0,0,[0,0],"Isenguard fly through"],
    [108940, 109929   ,0,0,0,0,[0,0],"Moth flys to Gandalf"],
    [109930, 111885   ,0,0,1,0,[0,0],"Isenguard fly through, orc army"],
    [111886, 115943   ,0,0,0,0,[1,-1],"stone trolls, Frodo struggles"],
    [115944, 119952   ,0,1,0,0,[0,0],"Galadriel with black riders, ends with them swept away"],
    [119953, 122529   ,0,0,0,0,[1,-1],"Rivendell, ends with i was delayed"],
    [122530, 123051   ,1,1,0,0,[0,0],"Saruman and Gandalf fight again"],
    [123052, 123796   ,0,0,0,0,[1,-1],"Gandalf flys away"],
    [123797, 132201   ,0,0,0,0,[0,0],"Rivendell, ends with Elrond telling story"],
    [132202, 133432   ,0,0,0,0,[0,0],"Sauron finger cut, Isildur says no"],#Shows sword cutting finger, but not much is seen.
    [133433, 151968   ,0,0,0,0,[0,0],"Rivendell discussion about ring"],#possibly scary Bilbo at 155175, 151969 is end of disk 1
    [151969, 159637   ,0,0,0,0,[0,0],"Rivendell, fellowship trek"],#1st scene of 2nd disc
    [159638, 164472   ,0,0,0,0,[0,0],"fellowship eating, practicing swords, ravens, hiking into the mountains"],
    [164473, 169391   ,0,0,0,0,[0,0],"Isengaurd fly through, mountain ice fall"],
    [169392, 176211   ,0,0,0,0,[0,0],"walk towards Moria, ends with its a tomb"],
    [176212, 178283   ,0,1,0,0,[0,0],"skeletons, goblins, sea monster"],
    [178284, 192637   ,0,0,0,0,[1,-1],"door crumbles, ends with arrow towards Boromir"],
    [192638, 193692   ,0,0,0,0,[0,0],"surrounded in tomb"],#Arrow flies, swords drawn, maybe a bit scary?
    [193693, 200317   ,1,1,1,0,[0,0],"tomb fight, ending with troll dying"],
    [200318, 202613   ,0,0,0,0,[1,1],"checking on Frodo, ends in hall with orcs"],
    [202614, 203371   ,0,1,1,0,[0,0],"hall of orcs, ending with orcs running"],
    [203372, 206267   ,0,0,0,0,[1,-1],"hear balrog, running to stairs"],
    [206268, 209317   ,1,1,1,0,[0,0],"running from orcs to balrog battle"],
    [209318, 209749   ,0,1,0,0,[0,0],"running from balrog"],
    [209750, 210144   ,0,0,0,0,[1,-1],"crossing bridge"],
    [210145, 211694   ,1,1,0,0,[0,0],"Gandalf fights balrog"],
    [211695, 212240   ,0,0,0,0,[1,-1],"Gandalf looks down, falls to floor"],
    [212241, 212336   ,0,1,0,0,[0,0],"Gandalf falls from bridge"],
    [212337, 217107   ,0,0,0,0,[1,1],"Frodo says no, fellowship sad"],
    [217108, 217462   ,0,0,0,0,[0,0],"Elf arrows in the forest"],
    [217463, 233872   ,0,0,0,0,[0,0],"Caras Galadhon 1"],
    [233873, 234633   ,1,1,0,0,[0,0],"seeing well, fires in Hobbiton"],
    [234634, 238719   ,0,0,0,0,[1,0],"Caras Galadhon 2"],
    [238720, 241122   ,0,1,1,0,[0,0],"Isengaurd"],
    [241123, 249909   ,0,0,0,0,[1,1],"leaving Caras Galadhon"],
    [249910, 250859   ,0,1,1,0,[0,0],"Uruk-hai chasing"],
    [250860, 262462   ,0,0,0,0,[1,1],"fellowship boats, landing, Boromir and Frodo"],
    [262463, 262829   ,0,1,0,0,[0,0],"Frodo sees the eye"],
    [262830, 264970   ,0,0,0,0,[1,0],"Frodo Aragorn talk"],
    [264971, 279530   ,0,1,1,0,[0,0],"Uruk-hai fight, boromir dies"],
    [279531, 288595   ,0,0,0,0,[1,1],"Frodo leaves, movie ends"],
    [288596, 328271   ,0,0,0,0,[0,0],"Credits"],
    
]

twotowersCuts = [
    #                  Violence
    #                  | Scary
    #                  | | Orcs
    #                  | | | Nasgul
    #                  v v v v
    [0,      2545     ,0,0,0,0,[0,0],"Mountains pan"],
    [2546,   5492     ,1,1,0,0,[0,0],"Gandalf fights balrog"],
    [5493,   14138    ,0,0,0,0,[1,1],"Frodo wakes, walking with Sam"],
    [14139,  16060    ,0,1,0,0,[0,0],"Frodo Sam fight Gollum"],#not very scary
    [16061,  21216    ,0,0,0,0,[1,1],"Frodo Sam walk with Gollum"],
    [21217,  24612    ,0,0,1,0,[0,0],"Merry Pippin with orcs"],
    [24613,  27717    ,0,0,0,0,[1,-1],"Aragorn, Gimli, Legolas trailing orcs"],
    [27718,  28968    ,0,0,0,0,[0,0],"Isenguard fly through 2 towers"],
    [28969,  31717    ,0,1,0,0,[0,0],"Orcs cutting trees, builing army"],
    [31718,  32823    ,0,0,0,0,[1,0],"Rohan intro, preparnig for attack"],
    [32824,  33175    ,1,1,0,0,[0,0],"Orcs attack Rohan"],
    [33176,  33600    ,0,0,0,0,[1,-1],"Riders of Rohan see orcs"],#Not great audio transition
    [33601,  34275    ,0,1,0,0,[0,0],"Searching bodies"],
    [34276,  39056    ,0,0,0,0,[1,0],"Find Theodred alive, ends with banished"],
    [39057,  40354    ,0,0,0,0,[0,0],"Orcs with AGL chasing"],#orcs brief and far enough in distance to be 0
    [40355,  44637    ,0,1,1,0,[0,0],"Orcs with MP"],
    [44638,  45310    ,1,1,1,0,[0,0],"Riders find orcs and attack"],
    [45311,  51439    ,0,0,0,0,[1,1],"Riders talk with AGL"],
    [51440,  51907    ,0,1,1,0,[0,0],"AGL find orc pile"],
    [51908,  54332    ,0,0,0,0,[1,1],"Gimli finds sheath, Aragorn starts tracking"],
    [54333,  54361    ,0,1,1,0,[0,0],"orc grabs hobbit"],
    [54362,  54406    ,0,0,0,0,[1,0],"belt removed"],
    [54407,  54496    ,0,1,1,0,[0,0],"Orc drops belt"],
    [54497,  55086    ,0,0,0,0,[1,0],"Hobbits run into forest"],
    [55087,  55509    ,0,0,0,0,[0,0],"MP in fangorn"],
    [55510,  55852    ,0,0,1,0,[0,0],"Orc finds MP"],
    [55853,  56457    ,0,0,0,0,[1,-1],"MP continue running"],
    [56458,  56597    ,0,1,1,0,[0,0],"Orc Attacks Marry"],
    [56598,  56935    ,0,0,0,0,[1,0],"Pippin meets treebeard"],
    [56936,  57203    ,1,1,1,0,[0,0],"Treebeard smashing orc"],
    [57204,  60111    ,0,0,0,0,[1,0],"Treebeard holding, talking to MP"],
    [60112,  66923    ,0,0,0,0,[0,0],"FSG walking"],
    [66924,  67578    ,0,1,0,0,[0,0],"Frodo falls into water, sees spirits"],
    [67579,  70940    ,0,0,0,0,[1,1],"FSG walking, Frodo sees flashback"],
    [70941,  70987    ,1,1,0,1,[0,0],"Flashback to Nasgul stabbing Frodo in wraith world"],
    [70988,  72116    ,0,1,0,1,[0,0],"FSG see nasgul"],
    [72117,  73118    ,0,0,0,0,[1,-1],"FSG hide under bushes"],#Nasgul far away, not scary or recognizable
    [73119,  77578    ,0,0,0,0,[0,0],"AGL in fangorn, see white wizard"],
    [77579,  78109    ,1,1,0,0,[0,0],"Gandalf fighting balrog"],
    [78110,  83900    ,0,0,0,0,[1,-1],"Gandalf in time, returns until task is done, shadowfax"],
    [83901,  87275    ,0,0,0,0,[0,0],"MP with treebeard"],
    [87276,  90347    ,0,0,0,0,[0,0],"AGLG talking"],
    [90348,  97964    ,0,0,0,0,[0,0],"FSG at black gate"],
    [97965,  104575   ,0,0,0,0,[0,0],"MP in fangorn"],
    [104576, 113891   ,0,0,0,0,[0,0],"AGLG in Rohan"],
    [113892, 114288   ,1,0,0,0,[0,0],"AGLG fight with Rohan men and Wormtongue"],
    [114289, 125976   ,0,0,0,0,[1,1],"Gandalf frees King Theoden"],
    [125977, 133079   ,0,0,0,0,[0,0],"Rohan prep to leave for Helm's Deep"],
    [133080, 135245   ,0,0,0,0,[0,0],"Saruman and Wormtongue"],
    [135246, 138656   ,0,0,0,0,[0,0],"Leaving Rohan"],
    [138657, 139570   ,0,0,1,0,[0,0],"Saruman and Wormtongue plotting"],
    [139571, 150546   ,0,0,0,0,[1,1],"FSG walking see elephants"],
    [150547, 152969   ,1,1,0,0,[0,0],"Faramir's men attack elephants, catch FS"],
    [152970, 153305   ,0,0,0,0,[1,1],"Faramir takes FS"],
    [153306, 165931   ,0,0,0,0,[0,0],"AGL guide rohan to Helm's Deep"],
    [165932, 172230   ,1,1,1,0,[0,0],"Wargs attack rohan people, Aragorn falls"],
    [172231, 172396   ,0,0,0,0,[1,1],"Rohan people looking through the dead"],
    [172397, 172520   ,0,1,0,0,[0,0],"Pan through blood, dead horse"],
    [172521, 172695   ,0,0,0,0,[1,-1],"Gimli says Aragorn?"],
    [172696, 173582   ,0,1,1,0,[0,0],"Talk with orc"],
    [173583, 178954   ,0,0,0,0,[1,-1],"Look over cliff, Rohan people make it to Helm's Deep"],
    [178955, 181148   ,0,1,1,0,[0,0],"Saruman shows Wormtongue his army"],
    [181149, 190627   ,0,0,0,0,[1,1],"Treebeard walks, Aragorn survives, Rivendell"],
    [190628, 191054   ,0,1,1,0,[0,0],"Saruman, orcs march, Sauron watches"],
    [191055, 216364   ,0,0,0,0,[1,1],"FS taken to Faramir's hideout"],#awkward audio transition
    [216365, 224354   ,0,0,0,0,[0,0],"Aragorn sees army, Helm's Deep prepares"],
    [224355, 242030   ,0,0,0,0,[0,0],"Treebeard gathering, Helm's prep, elves join"],
    [242031, 248810   ,2,1,1,0,[0,0],"Battle of Helm's Deep"],
    [248811, 251137   ,0,0,0,0,[1,1],"Treebeard too slow"],
    [251138, 256055   ,2,1,0,0,[0,0],"Battle of Helm's"],
    [256056, 258576   ,0,0,0,0,[1,0],"Ents decided to do nothing"],#-3db would be nice
    [258577, 267267   ,2,1,0,0,[0,0],"Helm's Deep, falling back to keep"],
    [267268, 269307   ,0,0,0,0,[1,1],"Treebeard walking to western forest, changes direction"],
    [269308, 273725   ,0,0,0,0,[0,0],"FS taken out of hideout, Treebeard sees trees burnt"],
    [273726, 276686   ,0,0,0,0,[0,0],"FS in Osgiliath"],
    [276687, 277369   ,0,1,0,1,[0,0],"Nasgul in Osgiliath"],
    [277370, 277971   ,0,0,0,0,[1,0],"Helm's Deep fortress gate defense"],
    [277972, 278010   ,0,1,1,0,[0,0],"Orcs hit gate 1"],
    [278011, 278663   ,0,0,0,0,[1,0],"Aragorn pep talk"],
    [278664, 278735   ,0,1,1,0,[0,0],"Orcs hit gate 2"],
    [278736, 279044   ,0,0,0,0,[1,0],"Women and children make for the mountain pass"],
    [279045, 279073   ,0,1,1,0,[0,0],"orcs hit gate 3"],
    [279074, 280920   ,0,0,0,0,[1,0],"Ride out with me, for Rohan"],
    [280921, 284046   ,2,1,1,0,[0,0],"orcs hit gate, battle"],
    [284047, 284172   ,0,0,0,0,[1,1],"Ents attack Isenguard"],
    [284173, 284826   ,2,1,1,0,[0,0],"Orcs smashed by rocks"],
    [284827, 285221   ,0,0,0,0,[1,1],"Saruman sees destruction 1"],#possible violence, but small orcs at a distance
    [285222, 285386   ,1,1,1,0,[0,0],"Ent smashes orcs together"],
    [285387, 287555   ,0,0,0,0,[1,0],"Saruman sees destruction 2"],
    [287556, 289980   ,1,1,1,1,[0,0],"Frodo walks to Nasgul, fighting continues"],
    [289981, 291647   ,0,0,0,0,[1,1],"Sam monologue begins"],#some orcs but very short
    [291648, 294781   ,0,0,0,0,[0,0],"Sam narrarates while Isenguard falls"],
    [294782, 294899   ,0,0,1,0,[0,0],"Orcs retreat to Fangorn"],
    [294900, 295654   ,0,0,0,0,[1,0],"Aragorn watches orcs die in Fangorn"],
    [295655, 296627   ,0,1,1,0,[0,0],"Gimli, Legolas clear orc bodies"],
    [296628, 309063   ,0,0,0,0,[1,1],"MP take control of Isenguard"],
    [309064, 338660   ,0,0,0,0,[0,0],"Credits"],

]
returnofthekingCuts = [
    #                  Violence
    #                  | Scary
    #                  | | Orcs
    #                  | | | Nasgul
    #                  v v v v
    [0,      5320     ,0,0,0,0,[0,0],"Intro, Smeagol finds ring"],
    [5321,   6648     ,1,1,0,0,[0,0],"Smeagol kills friend"],
    [6649,   6757     ,0,1,0,0,[0,0],"Smeagol takes ring from dead friend's hand"],
    [6758,   7119     ,0,0,0,0,[1,0],"Smeagol puts on ring"],
    [7120,   9212     ,0,1,0,0,[0,0],"Smeagol cursed"],
    [9213,   13458    ,0,0,0,0,[1,-1],"FSG continue journey"],
    [13459,  21562    ,0,0,0,0,[0,0],"MP Isenguard met by ALGG"],
    [21563,  25220    ,1,1,0,0,[0,0],"Saruman sends fireball, dies"],
    [25221,  33205    ,0,0,0,0,[1,0],"Pippin takes stone, they go to Rohan"],
    [33206,  38919    ,0,0,0,0,[0,0],"Gollum monologue, FSG argue"],
    [38920,  44081    ,0,0,0,0,[0,0],"Rohan, ALGG MP, Pippin looks at stone"],
    [44082,  45254    ,0,1,0,0,[0,0],"Saruman sees Pippin"],
    [45255,  53379    ,0,0,0,0,[1,0],"Gandalf scoops up stone, he and Pippin leave"],
    [53380,  60484    ,0,0,0,0,[0,0],"Elves leave, Arowyn rides back"],
    [60485,  65327    ,0,0,0,0,[0,0],"GP ride to Minas Tirith"],
    [65328,  65529    ,1,1,0,0,[0,0],"Boromir flash back"],
    [65530,  72373    ,0,0,0,0,[1,1],"Pippin volunteers service, Galdolf and Pippin talk"],#not a great transition
    [72374,  75253    ,0,0,0,0,[0,0],"FSG walking, see head with crown of flowers"],
    [75254,  78993    ,0,0,0,0,[0,0],"GP talking about the war"],
    [78994,  85373    ,0,0,1,1,[0,0],"Nasgul prep for war, flash back to stabbing Frodo, Minas morgul"],
    [85374,  86880    ,0,0,0,0,[1,1],"FSG climbing away from Minas Morgul"],
    [86881,  88421    ,0,0,0,0,[0,0],"Pippin has a task, Faramir ready to fight"],
    [88422,  92767    ,1,1,1,0,[0,0],"Faramir defends city"],
    [92768,  101544   ,0,0,0,0,[1,1],"Pippin lights beacon"],
    [101545,  104738  ,1,1,1,1,[0,0],"Faramir battle 1"],
    [104739,  104985  ,0,0,0,0,[1,1],"GP ride towards battle"],
    [104986,  105345  ,1,1,1,1,[0,0],"Faramir battle 2"],
    [105346,  111294  ,0,0,0,0,[1,1],"Gandalf enables escape from Osgiliath"],
    [111295,  114167  ,0,0,0,0,[0,0],"FSG continue climb"],
    [114168,  114727  ,0,0,1,1,[0,0],"Nasgul,Orcs in Osgiliath"],
    [114728,  120572  ,0,0,0,0,[1,0],"GP in Minas Tirith"],
    [120573,  128218  ,0,0,0,0,[0,0],"Gogum sabatoges Sam"],
    [128219,  131546  ,0,0,0,0,[0,0],"Faramir goes back to fight"],
    [131547,  131802  ,0,0,1,0,[0,0],"Faramir fight resumes"],
    [131803,  134437  ,1,1,1,0,[0,0],"Pippin sings while soldiers die"],
    [134438,  134948  ,0,0,0,0,[1,1],"Gandalf sad"],
    [134949,  153863  ,0,0,0,0,[0,0],"Gondor counting men, Aragorn receives sword"],
    [153864,  157383  ,0,0,0,0,[0,0],"AGL go into the mountain"],
    [157384,  159410  ,0,0,0,0,[0,0],"Gondor rides light and swift"],
    [159411,  159918  ,0,0,0,0,[0,0],"Orcs prep to attack Minas Tirith"],
    [159919,  169273  ,0,1,0,0,[0,0],"AGL find the king to fulfil his oath"],#entire scene has skulls and ghosts, so its likely scary for children
    [169274,  170694  ,0,1,0,0,[0,0],"King fulfills oath"],
    [170695,  183539  ,0,1,0,0,[0,0],"Wounded Faramir returns, battle of Minas Tirith begins"],
    [183540,  184992  ,0,1,0,0,[0,0],"AGL take ships"],
    [184993,  188290  ,0,0,0,0,[1,1],"Frodo Gollum enter Shelob's Lair"],
    [188291,  188885  ,0,1,0,0,[0,0],"Frodo sees bones, dead bird"],
    [188886,  189965  ,0,0,0,0,[1,1],"Sam finds Lambas"],
    [189966,  193853  ,1,1,0,0,[0,0],"Frodo fights Shelob, escapes"],
    [193854,  196130  ,1,1,0,0,[0,0],"Frodo fights Gollum, Gollum falls"],
    [196131,  198143  ,0,0,0,0,[1,-1],"Frodo continues, help from Galadriel"],
    [198144,  200788  ,0,0,0,0,[0,0],"Gondor scouts Minas Tirith"],
    [200789,  201732  ,0,1,1,0,[0,0],"Battle of Minas Tirith gate defense"],
    [201733,  203905  ,0,0,0,0,[1,-1],"Steward tries to burn Faramir"],
    [203906,  205507  ,1,1,1,0,[0,0],"Minas Tirith Gate breaks"],
    [205508,  210877  ,0,1,0,0,[0,0],"Frodo stung, Sam fights Shelob"],
    [210878,  212657  ,0,0,0,0,[0,0],"Sam with Frodo paralyzed"],
    [212658,  214180  ,0,1,1,0,[0,0],"Orcs find Frodo"],
    [214181,  219368  ,1,1,1,1,[0,0],"Faramir alive,Pippin finds Gandalf, attacked by Nasgul"],
    [219369,  220474  ,0,0,0,0,[1,-1],"Gondor joins"],
    [220475,  220710  ,0,0,1,0,[0,0],"Orcs prep to fight 1"],
    [220711,  221683  ,0,0,0,0,[1,1],"Theoden pep talk"],
    [221684,  221750  ,0,0,1,0,[0,0],"Orcs prep to fight 2"],
    [221751,  223504  ,0,0,0,0,[1,0],"Merry ready to ride"],
    [223505,  223601  ,0,0,1,0,[0,0],"Orcs prep bows"],
    [223602,  223912  ,0,0,0,0,[1,0],"Gondor rides"],#not a great transition
    [223913,  225323  ,1,1,1,0,[0,0],"Gondor Fight begins"],
    [225324,  227962  ,0,0,0,0,[1,-1],"Denethor lights Faramir"],#not a great transition
    [227963,  228370  ,0,1,0,0,[0,0],"Denethor burns"],
    [228371,  237624  ,1,1,1,0,[0,0],"Battle continues with elephants"],
    [237625,  240118  ,1,1,1,1,[0,0],"Nasgul attacks King Theoden"],
    [240119,  241421  ,0,1,1,0,[0,0],"Aragorn arrives"],
    [241422,  246215  ,1,1,1,1,[0,0],"Eowyn kills Nasgul, fight continues"],
    [246216,  251891  ,0,1,0,0,[0,0],"Theoden dies, oath fulfilled"],
    [251892,  254023  ,0,0,0,0,[1,-1],"Eowyn recovers"],#not a great video transition
    [254024,  255271  ,0,0,0,0,[0,0],"Pippin finds Merry"],
    [255272,  258134  ,1,1,1,0,[0,0],"Frodo recovers, lost ring"],
    [258135,  261257  ,1,1,1,0,[0,0],"Sam saves Frodo"],
    [261258,  265243  ,0,0,0,0,[1,1],"Sam shows Frodo the ring"],
    [265244,  269833  ,0,0,0,0,[0,0],"AGLG head towards black gate"],
    [269834,  271035  ,0,0,0,0,[0,0],"Faramir and Eowyn hold hands"],
    [271036,  272216  ,0,0,0,0,[0,0],"Frodo Sam sneak into orc camp 1"],#candidate for detailed cut
    [272217,  273391  ,0,1,1,0,[0,0],"Orcs yell at FS"],
    [273392,  273667  ,0,0,0,0,[1,1],"AGLG ride"],#candidate for detailed cuts
    [273668,  275925  ,0,1,1,0,[0,0],"FS start fight with orcs"],
    [275926,  279360  ,0,0,0,0,[1,-1],"FS escape orcs"],#video transition cross dissolve example at 276295
    [279361,  284495  ,0,0,0,0,[0,0],"AGLG ride to gate, FS out of water, meet mouth of Sauron"],
    [284496,  286753  ,0,0,0,0,[0,0],"Talk to Mouth about Frodo"],#might be scary, but somewhat important plot?
    [286754,  287075  ,1,1,0,0,[0,0],"Mouth head cut off, concludes negotiations"],
    [287076,  290441  ,0,0,0,0,[1,1],"FS avoiding eye, AGLG prepare for battle"],
    [290442,  290497  ,0,1,1,0,[0,0],"AGLG surrounded"],
    [290498,  296773  ,0,0,0,0,[1,0],"FS climb mountain, fight about to begin"],
    [296774,  300497  ,1,1,1,1,[0,0],"Fight begins, FS climb to Mount Doom entrance"],
    [300498,  303460  ,0,0,0,0,[1,1],"Frodo enters Mt Doom, puts on ring"],
    [303461,  306619  ,1,1,1,1,[0,0],"Nasgul fly to Mt Doom, Frodo Gollum fight, battle continues"],
    [306620,  308794  ,0,0,0,0,[1,1],"Frodo Gollum fall, Gollum dies"],#A little scary with gollum in lava, but key plot point
    [308795,  309286  ,0,0,1,0,[0,0],"Orcs run"],
    [309287,  310780  ,0,0,0,0,[1,0],"Tower falls, explodes"],
    [310781,  311812  ,0,1,1,1,[0,0],"Orcs fall into the earth, volcano explodes, Nasgul fall"],
    [311813,  316821  ,0,0,0,0,[1,1],"FS run from lava, rescued"],
    [316822,  320264  ,0,0,0,0,[0,0],"Frodo wakes in bed"],
    [320265,  327932  ,0,0,0,0,[0,0],"Minas Tirith, Aragorn crowned, wedding"],
    [327933,  330642  ,0,0,0,0,[0,0],"Return to Hobbiton"],
    [330643,  345158  ,0,0,0,0,[0,0],"Sam wedding, journey to Gray Haven"],
    [345159,  347428  ,0,0,0,0,[0,0],"Sam and family, end"],
    [347429,  378596  ,0,0,0,0,[0,0],"Credits"],
]

#select film
if inputMedia == 0:
    print(" ---- Generating 1080p Extended Edition WITHOUT 2 disc intermission ----")
elif inputMedia == 1:
    print(" ---- Generating 1080p Extended Edition WITH 2 disc intermission ----")

#select cuts from file switches
if movieSelection == 0:
    selectedCuts = fellowshipCuts
    print(" ---- Generating Fellowship cut ----")
elif movieSelection == 1:
    selectedCuts = twotowersCuts
    print(" ---- Generating Two Towers cut ----")
else:
    selectedCuts = returnofthekingCuts
    print(" ---- Generating Return of the King cut ----")
print(" ---- Warning: Console must be closed while script runs ----")

################################
#Functions used in this script
################################

#Move the edit point to the desired orientation
def setEditPoint(newPoint):
    global editPointStatus
    verbose = 0
    if verbose:
        print(f"start point: {editPointStatus}, end point: {newPoint}")
    loopCount = 0
    while ((editPointStatus != newPoint) and loopCount<3):
        loopCount = loopCount + 1
        print(f"{editPointStatus != newPoint}")
        if loopCount == 3:
            print("Error: setEditPoint failure")
            print(editPointStatus)
            print(newPoint)
        keyboard.send("u")
        time.sleep(0.5)
        if editPointStatus == 0:
            editPointStatus = 1
            if verbose:
                print(f"editPointStatus: {editPointStatus}, newPoint: {newPoint}, loopCount: {loopCount}")
            #break
        elif editPointStatus == 1:
            editPointStatus = -1
            if verbose:
                print(f"editPointStatus: {editPointStatus}, newPoint: {newPoint}, loopCount: {loopCount}")
            #break
        elif editPointStatus == -1:
            editPointStatus = 0
            if verbose:
                print(f"editPointStatus: {editPointStatus}, newPoint: {newPoint}, loopCount: {loopCount}")
            #break

    if verbose:
        print("Done with setEditPoint()")

def addAudioTransition():
    global generated_timeline
    timecode = generated_timeline.GetCurrentTimecode()
    if verbose:
        print(f"start timecode: {timecode}")
    #we can use SetCurrentTimecode() if we can convert a frame to timecode,
    #otherwise we set playhead to end and do our insertion from there
    #sleep time gives davinci resolve time to do the action before beginning the next
    #0.1 seems to work well. May need to be higher on low end pc
    #TODO: make keypress and sleep into a single function
    sleep_time = 0.2
    #so lets go back one cut
    time.sleep(sleep_time)
    keyboard.send('ctrl+4')#focus on timeline
    time.sleep(sleep_time)
    keyboard.send('end')
    time.sleep(sleep_time)
    #if verbose:
    #    print(f"end timecode: {timecode}")
    keyboard.send('up')
    time.sleep(sleep_time)
    #if verbose:
    #    print(f"UP timecode: {timecode}")
    #select nearest edit point
    keyboard.send('v')
    time.sleep(sleep_time)
    #if verbose:
    #    print(f"start timecode: {timecode}")
    setEditPoint(cuts[6][1])
    time.sleep(sleep_time)
    keyboard.send("shift+t")
    #Stop selection?
    keyboard.send('end')
    time.sleep(sleep_time)

#lengthen a scene's frameCount, thus increasing each consecutive frame's count as well
def lengthenScene(sceneIndex, stretchFrameCount):
    global selectedCuts
    for index,cuts in enumerate(selectedCuts):
        if index == sceneIndex:
            cuts[1] = cuts[1] + stretchFrameCount
            if verbose:
                print(f"scene lengthed: {sceneIndex}: {cuts[7]}")
        elif index > sceneIndex:
            cuts[0] = cuts[0] + stretchFrameCount
            cuts[1] = cuts[1] + stretchFrameCount

def timecodeToFrames(timecode, frame_rate):
    """Converts a timecode string to frame count.

    Args:
        timecode: Timecode string in the format "HH:MM:SS:FF".
        frame_rate: Frame rate of the timeline.

    Returns:
        The frame count as an integer.
    """
    hours, minutes, seconds, frames = map(int, timecode.split(':'))
    total_seconds = (hours * 3600) + (minutes * 60) + seconds
    frame_count = (total_seconds * frame_rate) + frames
    return int(frame_count)

##################################
#End functions used in this script
##################################

#TODO: make main statement, not sure how much it matters
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
        print("Error! Cut \""+cuts[7]+"\" startFrame is greater than endFrame")
    #ensure that cuts[1] = cuts+1[0] - 1
    if next_item != None:
        if cuts[1] != (next_item[0] - 1):
            print("Error! Cut \""+cuts[7]+"\" endFrame is not nextCut.startFrame - 1")

#define media indices TODO: This can probably be cleaner, maybe by name
clipListCount = 1
clipListCount = clipListCount + audioRemux #add one for audio clip
clipListCount = clipListCount + (inputMedia == 1) #add one for 2 disk

#Update data structure for a desired version of the film
if inputMedia == 1:
    lengthenScene(45,167)
    
#Populate source timeline
#add video

currentProject.SetCurrentTimeline(source_timeline)
sourceTimelineAudioLength = 0
sourceTimelineVideoLength = 0
for i in range(clipListCount):
    if verbose == 2:
        print(f"clip list item {i}:")
        print(clip_list[i].GetClipProperty(propertyName=None))
    #check if item is audio or video
    clipType = clip_list[i].GetClipProperty('Type')
    # - int(clip_list[i].GetClipProperty('Start'))
    #track length of audio and video separately to track position to append
    if clipType == "Audio":
        print("adding audio")
        #get item length in frames
        cliplength = timecodeToFrames(clip_list[i].GetClipProperty('End TC'), 24)
        media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[i], "recordFrame": 86400+sourceTimelineAudioLength}])
        sourceTimelineAudioLength = sourceTimelineAudioLength + cliplength
    elif clipType == "Video":
        print("adding video")
        #get item length in frames
        cliplength = int(clip_list[i].GetClipProperty('End'))
        media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[i], "recordFrame": 86400+sourceTimelineVideoLength}])
        sourceTimelineVideoLength = sourceTimelineVideoLength + cliplength
    elif clipType == "Video + Audio":
        print("adding video audio combo")
        #get item length in frames
        cliplength = int(clip_list[i].GetClipProperty('End'))
        media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[i], "recordFrame": 86400+sourceTimelineVideoLength}])
        sourceTimelineAudioLength = sourceTimelineAudioLength + cliplength
        sourceTimelineVideoLength = sourceTimelineVideoLength + cliplength
    
#media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[0], "recordFrame": 86400}])
#media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[0]}])
#if necessary, add audio
#if audioRemux == 1:
#    #for some reason the timeline starts at hr=1, so appending to the beginning means frame 86400
#    #in our case, we've set both the video and audio to recordFrame=0, that way the timeline frame numbers match the media pool frame numbers
#    #media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[1], "recordFrame": 86400}])
#    media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[1]}])
#    #audiotrack = source_timeline.GetItemListInTrack("audio", 1)
#    #clip = audiotrack[0]
#    #clip.SetProperty("start", 0)
#if inputMedia == 1:
#    media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[2]}])

for cuts in selectedCuts:
    if cuts[2] <= maxViolence and cuts[3] <= maxscary and cuts[4] <= maxOrcs and cuts[5] <= maxNasgul:
        currentProject.SetCurrentTimeline(generated_timeline)
        newclip = media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[2], "startFrame": cuts[0], "endFrame": cuts[1]}])
        if (cuts[6][0] == 1) and (audioTransitions == 1):
            timecode = generated_timeline.GetCurrentTimecode()
            if verbose:
                print(f"start timecode: {timecode}")
            #TODO: fix problem where audio transition is not placing in the right spot
            #This is likely due to the playhead not staying at the end of the clip while
            #we switch timelines. For some reason END is not sending the playhead to the end
            addAudioTransition()
        #Order goes center, right, left, repeats
        #When DR is loaded, it starts on center
        #we'll need to make a state machine to track state
    elif deleted_scenes:
        currentProject.SetCurrentTimeline(deleted_scenes_timeline)
        newclip = media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[2], "startFrame": cuts[0], "endFrame": cuts[1]}])
        #print(newclip[0].GetProperty())
        if verbose:
            print("cut \""+cuts[7]+"\" removed at frame "+str(cuts[0]))
#appends the first clip from root folder, frames 0 to 10, only audio.

#TODO: print length of each timeline, total, and whether they match
#reset edit point in case we run the script again later
setEditPoint(0)
print(" ---- Successfully generated timeline ----")
winsound.MessageBeep()
#Exploring adding transitions to timeline
#Shift-T on keyboard will add an audio only transition to the selected clip
#We can create keystrokes, however this requires selecting clips. Not sure how easy this will be to do
#Shift+V selects clip at playhead, Shift+T adds the default transition
#If we look at the clip inspector, we can see the transition has been added. Looking for an equivalent in Python
#keyboard.press_and_release('shift+t')
#Notes about transition data structure:
#transitions are always done relative to the beginning of a clip
#Data structure is [a,b] where a is True,false, and b is -1=end of prev clip,0=mid,1=beginning of current clip
        #experiment with adding transitions
        #keyboard.send('up')
        #keyboard.send('v') #V selects nearest edit point, this creates a transition that spans the clips
        #keyboard.send('u') #edit point type. Toggles side or aligned center
        #keyboard.send('shift+v') #select clip
        #keyboard.send("shift+t")
        #keyboard.send('esc')
        #time.sleep(sleep_time)

#Exploring auto-render
#From https://documents.blackmagicdesign.com/UserManuals/Fusion8_Scripting_Guide.pdf
# Adds the current composition as new job
# and print all RenderJobs in Queue.
#qm = fusion.RenderManager
#qm.AddJob(comp.GetAttrs()[“COMPS_FileName”])
#joblist = qm.GetJobList().values()
#for job in joblist:
#print(job.GetAttrs()[“RJOBS_Name”])
