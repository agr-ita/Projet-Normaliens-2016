### Script by GUEVARA RUKOZ Adriana, modified from code by LIN Isabelle ### 

from __future__ import print_function
import pygame
from pygame.locals import *
import random, os, copy, time, sys

subj = sys.argv[1] #2nd argument given from console (first = "identification.exe")
#print(subj)

#work_path = "/home/adriana/Projects/PhD/subprojects/ahpa-ehpe/adriana/exp_materials/identification"
work_path = os.getcwd()
os.chdir(work_path)

print(work_path)
#work_path=""

sep="\\" #windows
#sep="/" #linux

############
# SETTINGS #
############
nblocks = 2
rep = 1 #item repetitions within the same block

speakers = ['sh', 'ac', 'am']
V = ['a','i', 'u','e','o']
C = ['h','k']
coarticulation = ['0a', '0i', '0u', '0e', '0o', "aa", "ii", "uu", "ee", "oo", "00"] #"0v"==coartV; "vv"==fullV; "00"==natural cluster]
#coarticulation = ['a', 'i', 'u', 'e', 'o', "A", "I", "U", "E", "O", "0"] #lower==coartV; upper==fullV; "0"==natural cluster] #only linux-compatible
tr = ['am00pa', 'anaapa', 'im00pi', 'iniipi', 'um00pu', 'unuupu', 'emeepe', 'en00pe', 'omoopo', 'on00po']

bg_col = [255, 255, 255]
audio_buffer_size = 256
text_size = 600
text_col1 = [48, 128, 20]
text_col2 = [220, 20, 60]
gray = [56, 56, 56]

###############
# LOAD IMAGES #
###############
os.chdir(work_path + sep + "textscreens")
textscreens = {} 

#load instructions
textscreens['instructions'] = pygame.image.load('instructions_id.png')
textscreens['start'] = pygame.image.load('start.png')
textscreens['thankyou'] = pygame.image.load('thankyou.png')
textscreens['answer'] = pygame.image.load('answerscreen.png')

#getting image size for text screens, every screen having the same size
w, h = textscreens['answer'].get_size()

#feedback text
pygame.init()
#font = pygame.font.Font(None, text_size) #linux
font = pygame.font.SysFont("Arial", text_size) #windows
correct = font.render('O', True, text_col1, gray)
wrong = font.render('X', True, text_col2, gray)

#############
# FUNCTIONS #
#############

def wait(dur): #define delaying function, exit keys and responses
    ticks0 = pygame.time.get_ticks()
    while True:
        if dur != None and pygame.time.get_ticks() > ticks0 + dur:
            return
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                raise Exception
            if ev.type == KEYDOWN:
                if ev.key == K_s:
                    return ['0', pygame.time.get_ticks() - ticks0]                
                if ev.key == K_d:
                    return ['a', pygame.time.get_ticks() - ticks0]                
                if ev.key == K_f:
                    return ['i', pygame.time.get_ticks() - ticks0]                
                if ev.key == K_j:
                    return ['u', pygame.time.get_ticks() - ticks0]                
                if ev.key == K_k:
                    return ['e', pygame.time.get_ticks() - ticks0]
                elif ev.key == K_l:
                    return ['o', pygame.time.get_ticks() - ticks0]

def show(x, dur=None):
    if isinstance(x, str)==True: 
        if x not in textscreens: #show answer screens
            window.blit(textscreens['answer'], [W/2 - w/2, H/2 - h/2])
            font = pygame.font.SysFont("Arial", 150) #windows
            #font = pygame.font.Font(None, 150) #linux
            text = font.render(x, True, [0,0,0])
            lg, ht = text.get_size() 
            window.blit(text, [W/2 + 0 - lg/2, H/2 - ht])
        else: #instructions
            window.fill(bg_col)
            window.blit(textscreens[x], [W/2 - w/2, H/2 - h/2]) 
        pygame.display.flip()
        resp, RT = wait(None)
        return [resp, RT]
    else: #fill screen with background color
        window.fill(x)
        pygame.display.flip()
    if dur != None:
        time.sleep(dur)

def feedback(stim, response):
    if response == stim[3].lower():
        img = correct
    else:
        img = wrong
    x, y = img.get_size()
    window.fill(gray)
    window.blit(img, [W/2 - x/2, H/2 - y/2])
    pygame.display.flip()
    time.sleep(0.75)

def trial(x, training=False):
    x['sound'].play()
    show(bg_col, pygame.mixer.Sound.get_length(x['sound']))
    v, c = x['stim'][0:2]
    coart = x['stim'][2:4]
    pygame.event.get()      # clear any previous events (like key presses)
    resp, rt = show(x['screen'])
    if training==True:
        feedback(x['stim'], resp)
    show(bg_col)
    print(subj, x['block'], x['spk'], v, c, coart, resp, rt, file = out, sep = ',')


########
# MAIN #
########

#getting subject name
#subj = raw_input('subject: ') #when launching from console

try:
    #create data file
    out = open(work_path + sep + 'rawdata' + sep + subj + '.dat', 'at')
    print('SUBJ', 'BLOCK', 'SPK', 'V1', 'C', 'COART', 'RESP', 'RT', file = out, sep = ',')

    ################################
    # AUDIO AND SCREEN PREPARATION #
    ################################

    #audio
    pygame.mixer.pre_init(buffer = audio_buffer_size)
    pygame.init()
    
    #screen
    window = pygame.display.set_mode([0, 0], FULLSCREEN | DOUBLEBUF | HWSURFACE)
    W, H = window.get_size()
    pygame.mouse.set_visible(False)
    show(bg_col) 

    #################
    # RANDOMISATION #
    ################# 
    
    #creating 10 families (1 family = 1 C x V combination; e.g., ah_pa)
    stim_family=[]

    for spk in speakers:
        cspk = [] #buffer for current speaker's stimuli
        for i in range(len(C)):
            for j in range(len(V)):
                c = C[i]
                v = V[j]
                combos = []
                for coart in coarticulation:
                    combos.append({'spk': spk, 'stim': v+c+coart+'p'+v})
                combos = combos * rep #each participant hears each stim /rep/ times
                cspk.append(combos)
        stim_family.append(cspk)


    n_trials = len(speakers) * len(C) * len(V) * len(coarticulation) * rep

    #build a list of stims, excluding neighbours from a same family in the 2 closest positions bwd & fwd
    test_stims = [] 
    for block in range(nblocks):
        valid = True
        while valid:
            stim=[]
            valid = False
            stims_to_use = copy.deepcopy(stim_family)
            last_family = -1
            next_to_last_family = -1
            next_family = 0
            random.shuffle(speakers)
            try:
                for i in range(n_trials/len(speakers)):
                    for s in range(len(speakers)):
                        valid_families = []
                        spk = speakers[s]
                        for j in range(len(C) * len(V)):
                            if stims_to_use[s][j] != [] and j != last_family and j != next_to_last_family: 
                                valid_families.append(j)
                        #randomly choose stimulus for this trial
                        next_family = random.choice(valid_families)
                        next_stim = random.randint(0,len(stims_to_use[s][next_family])-1)
                        stim.append(stims_to_use[s][next_family].pop(next_stim))
                        #update settings for next trial
                        next_to_last_family = last_family
                        last_family = next_family
                for s in stim:
                    s['block'] = block + 1
                test_stims.append(stim)
            except:
                #print(i, len(stim), block)
                valid = True

    #########################
    # LOAD AUDITORY STIMULI #
    #########################
    coart_pos = 2
    coart_code = 2 #1 for caps-compatible version [obsolete]
    
    #load training stimuli
    os.chdir(work_path + sep + 'stimuli' + sep + 'training')
    tr_stim = [] 
    for t in tr:
        tr_stim.append({'stim': t, 
                        'block': "tr",
                        'spk': "ag",
                        'sound': pygame.mixer.Sound(t + '.wav'),
                        'screen': t[:coart_pos] + '?' + t[coart_pos+coart_code:]})
    
    random.shuffle(tr_stim)

    #load test stimuli
    os.chdir(work_path + sep + 'stimuli')
    for b in range(nblocks):
        for s in test_stims[b]:
            s['sound'] = pygame.mixer.Sound(s['spk'] + sep + s['stim'] +'.wav')
            s['screen'] = s['stim'][:coart_pos] + '?' + s['stim'][coart_pos+coart_code:]

    
    #####################
    # EXPERIMENT BEGINS #
    #####################

    #training
    show('instructions', 1)
    for s in tr_stim:
        trial(s, training=True)

    #test
    show('start')
    for b in range(nblocks):
        for s in test_stims[b]: 
            trial(s)
    show('thankyou')

finally:
    pygame.quit()
    out.close()




