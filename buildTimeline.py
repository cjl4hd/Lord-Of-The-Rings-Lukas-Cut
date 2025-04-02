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

#create data structure from switches
#startFrame, endFrame, violence, scary, orcs, nasgul, notes
#[0,1000,0-4,0-4,0-2,0-2,"string"]
fellowshipCuts = [
    [0,2769,0,0,0,0,"intro map"],
    [2770,3260,0,1,0,0,"sauron with ring"]

]

twotowersCuts = []
returnofthekingCuts = []


#TODO verify data structure
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
