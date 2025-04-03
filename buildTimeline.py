#Running in resolve 18.5

#If running outside of resolve:
#from python_get_resolve import GetResolve
#resolve = GetResolve()

#if running inside of resolve
#resolve = app()

#object setup
projectManager = resolve.GetProjectManager()
current_db = projectManager.GetCurrentDatabase()
currentProject = projectManager.GetCurrentProject()
media_pool = currentProject.GetMediaPool()
root_folder = media_pool.GetRootFolder()
clip_list = root_folder.GetClipList()       #starting with only single item, the main video

#create timeline
#If a timeline with this name exists, it will be overwritten
media_pool.CreateEmptyTimeline('New Generated Timeline')

#load file to media pool if not already there

#create switches for building timeline
#Movieselection = 0 for fellowship, 1 for two towers, 2 for return of the king
movieSelection = 0

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
maxscary = 4

#Orcs
#0 = no orcs
#1 = orcs
#2 = orcs fighting, chasing
maxOrcs = 2

#Nasgul
#0 = no nasgul
#1 = nasgul
#2 = nasgul fighting, chasing
maxNasgul = 2

#Create data structure from switches
#This is the key component to the build script. Each cut contains data for describing how child friendly it is.
#From that, you can choose how much you want to remove from the final cut.
#startFrame, endFrame, violence, scary, orcs, nasgul, notes
#[0,1000,0-4,0-4,0-2,0-2,"string"]
fellowshipCuts = [
    [0,     2769    ,0,0,0,0,"intro map"],
    [2770,  3260    ,0,1,0,0,"sauron with ring"]
    [3261,  6780    ,1,1,0,0,"shire burning, battle with sauron"]
    [6781,  7847    ,0,1,0,0,"ring with elf"]
    [7848,  8132    ,0,0,0,0,"ring being lost"]
    [8133,  9565    ,0,0,0,0,"golem intro"]
    [2770,  10720   ,0,0,0,0,"bilbo with golem"]
    [10720, 46288   ,0,0,0,0,"Shire, frodo, gandolf"]
    [46288, 47199   ,0,1,0,0,"Minas morgel"]
    [47200, 49399   ,0,0,0,0,"gandolf goes to minas tirith"]
    [49400, 50151   ,0,1,0,0,"black riders"]
    [50152, 57736   ,0,0,0,0,"hobbiton"]
    [57737, 58022   ,0,1,0,0,"golem torture"]
    [58023, 58171   ,0,0,0,0,"shire,bilbo, but that would lead them here"]
    [58171, 58297   ,0,1,0,0,"black rider with sword"]
    [58298, 62072   ,0,1,0,0,"take it gandolf, you must; samwise trimming the verge"]
    [62073, 67234   ,0,0,0,0,"frodo sam walking, ends with black horse"]
    [67235, 72517   ,0,0,0,0,"Gandolf visits Saurmon, ends with saurumon waving staff"]
    [72518, 73874   ,1,1,0,0,"fandolf sauromn fight"]
    [73875, 77510   ,0,0,0,0,"mary pipin join, ends with hobbits under tree"]
    [77511, 82717   ,0,1,0,0,"black rider above tree, ends at ferry"]
    [82718, 89247   ,0,0,0,0,"hobbits at bree, ends with frodo puting on ring"]
    [89248, 89964   ,0,0,0,0,"black riders, frodo in wraith world"]
    [89965, 91022   ,0,0,0,0,"frodo takes off ring, questioned by srtider"]
    [91023, 91245   ,1,0,0,0,"hobbits burst in, strider shows sword"]
    [91246, 91383   ,0,0,0,0,"hobbits talk to strider"]
    [91384, 93150   ,1,1,0,0,"black riders enter bree"]
    [93151, 99105   ,0,0,0,0,"hobbits wake up in bree, heading towards rivendel"]
    [99106, 100091   ,0,1,1,0,"Sauron introduces orcs"]
    [100092, 100758  ,0,0,0,0,"gandolf on top of tower"]
    [100759, 101194  ,0,1,1,0,"more orcs cutting trees"]
    [101195, 103126   ,0,0,0,0,"gandolf on tower, ends with hobbits on weathrtop looking down"]
    [103127, 107512   ,1,1,0,0,"weathertop fight scene"]
    [107513, 108259   ,0,0,0,0,"frodo in pain, strider carying him"]
    [108260, 108939   ,0,0,0,0,"Isenguard fly through"]
    [108940, 109929   ,0,0,0,0,"Moth flys to gandalf"]
    [109930, 111885   ,0,0,1,0,"Isenguard fly through, orc army"]
    [111886, 115943   ,0,0,0,0,"stone trolls, frodo struggles"]
    [115944, 119952   ,0,1,0,0,"Galadriel with black riders, ends with them swept away"]
    [119953, 122529   ,0,0,0,0,"Rivendel, ends iwth i was delayed"]
    [122530, 123051   ,1,1,0,0,"saurumon and gandolf fight again"]
    [123052, 123796   ,0,0,0,0,"gandolf flys away"]

]

twotowersCuts = []
returnofthekingCuts = []


#TODO verify data structure
    #each item goes from frame A to at least frame A+1
    #ensure no frames missing, frames in order

#loop through data structure, adding clips
    #“mediaPoolItem”
    #“startFrame” (int)
    #“endFrame” (int)
    #(optional) “mediaType” (int; 1 - Video only, 2 - Audio only)
    #media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[0], "startFrame": 0, "endFrame": 10, "mediaType": 2}])
if movieSelection == 0:
    selectedCuts = fellowshipCuts
elif movieSelection == 1:
    selectedCuts = twotowersCuts
else:
    selectedCuts = returnofthekingCuts
    
for cuts in selectedCuts:
    if cuts[2] <= maxViolence and cuts[3] <= maxscary and cuts[4] <= maxOrcs and cuts[5] <= maxNasgul:
        media_pool.AppendToTimeline([{"mediaPoolItem":clip_list[0], "startFrame": cuts[0], "endFrame": cuts[1]}])
    else:
        print("cut \""+cuts[6]+"\" removed at frame "+str(cuts[0]))
#appends the first clip from root folder, frames 0 to 10, only audio.

print("Successfully generated timeline.")
