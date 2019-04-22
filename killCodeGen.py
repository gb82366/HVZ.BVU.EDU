import random

adjective = ['correct','wrong','left','right','floppy','rigid','prickly',\
'beautiful','slow','fast','cold','warm','salty','calm','dark','light',\
'delightful','annoying','obscure','excited','polite','precious','old',\
'young','absurd','normal','scary','bitter','curious','crazy','tall','gangly',\
'spunky','speckled','terrifying','striped','miniature','fluffy','sleepy',\
'sporadic','wet','dry','stubby','lost','hairy','smooth','chewy','rough']

color = ['blue','pink','red','black','yellow','teal','green','grey','white',\
'purple','lemon','orange','brown','beige','maroon','cyan','magenta','vermillion',\
'periwinkle','navy','cerulean','khaki','peach','chocolate','crimson',\
'aqua','gold','silver','ivory','mango','midnight','turquoise','lime',\
'tan','lilac','creme','amber','almond','fuschia','azure','burgundy',\
'bronze','charcoal','copper','grape','honeydew','indigo','chrome',\
'plum','olive','carmine','denim','viridian','slate','muave','pewter']

animal = ['dog','cat','fish','bear','whale','bird','tiger','lion',\
'gazelle','frog','impala','toad','squirrel','monkey','beaver','panda',\
'zombie','human','orangutan','cow','alligator','cheetah','dolphin',\
'fox','kangaroo','octopus','scorpion','zebra','wolf','rabbit','goat',\
'rhino','hippo','dinosaur','giraffe','giant','seahorse','unicorn',\
'manticore','pegasus','otter','owl','aardvark','koala','dwarf','turtle',\
'sloth','coyote','bison','buffalo','deer','racoon','snake','lizard','puma',\
'pelican','duck']
listChoice = 0


def capWord(word):
    return word[0].upper() + word[1:]


def getCode():
    x = capWord(random.choice(adjective))
    x += capWord(random.choice(color))
    x += capWord(random.choice(animal))
    return x

