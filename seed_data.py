"""Initial, curated vocabulary copied into SQLite on the first application run.

These constants are seed content, not live application storage. Once seeded,
questions, answers, and accepted Wordle guesses are read from the database.
The guess dictionary is a curated English vocabulary, not the NYT word list.
"""

SCRAMBLE_WORDS = tuple("""
apple beach bread brush chair clock cloud dance dream drink earth family
flower forest friend garden grape green happy heart honey house juice kitten
lemon light magic mango melon money moon mother mouse music night ocean orange
panda paper party peach pencil phone piano plant plate queen rabbit radio rain
river robot school sheep shirt shoes smile snake snow space spoon spring star
stone storm story sugar summer sunny table tiger today train tree truck turtle
uncle video voice water whale wheel white window winter woman world yellow zebra
animal basket bottle button camera candle carpet castle cheese cherry circle
coffee cookie cotton dragon finger island jacket kitchen ladder letter little
mirror monkey number orange pillow pocket potato purple rocket silver sister
soccer spider street teacher tomato travel turkey village violet wallet watch
""".split())

WORDLE_TARGETS = tuple("""
about above actor adult after again agree ahead alarm album alert alien alike
alive allow alone along alter among angel anger angle angry ankle apart apple
apply arena argue arise arrow aside avoid awake award aware awful badge baker
basic beach began begin below bench berry birth black blade blame bland blank
blast blend blind block blood bloom blown board boast bonus boost booth brain
brake brand brave bread break breed brick bride brief bring broad broke brown
brush build built bunch cabin cable camel canal candy carry catch cause chain
chair chalk charm chart chase cheap check cheek cheer chess chest chief child
chill choir claim class clean clear clerk click climb clock close cloth cloud
coach coast color comic coral couch could count court cover crack craft crane
crash crawl crazy cream creek crime crisp cross crowd crown cruel crush cycle
daily dairy dance death delay depth diary dirty doubt dough dozen draft drain
drama drank dream dress dried drink drive drove eagle early earth eaten eight
elder elect empty enemy enjoy enter entry equal error event every exact exist
extra faint fairy faith fancy fault feast fence fever field fifth fifty fight
final first flame flash fleet flesh float flock flood floor flour fluid flute
focus force found frame fresh front frost fruit funny giant given glass globe
glory glove going grace grade grain grand grant grape graph grasp grass grave
great green greet grind group grown guard guess guest guide guilt habit happy
harsh heart heavy hobby honey honor horse hotel house human humor hurry ideal
image imply index inner input issue ivory jelly jewel joint judge juice knife
knock known label labor large laser later laugh layer learn least leave legal
lemon level light limit linen liver local logic loose lover lower loyal lucky
lunch magic major maker mango maple march marry match maybe mayor medal media
melon mercy merit metal meter might minor mixed model money month moral motor
mount mouse mouth movie music nasty never newly night noble noise north novel
nurse occur ocean offer often olive onion opera orbit order organ other ought
outer owner paint panel panic paper party patch pause peace peach pearl pedal
penny phase phone photo piano piece pilot pitch place plain plane plant plate
point polar porch pound power press price pride prime print prize proof proud
prove pulse puppy queen quest quick quiet quite quote radio raise range rapid
ratio reach react ready rebel refer relax renew repay reply rider ridge right
rigid ripen risen river roast robot rocky rough round route royal ruler rural
salad sauce scale scare scarf scene scent score scrub sense serve seven shade
shake shall shame shape share shark sharp shave sheep sheer sheet shelf shell
shift shine shiny shirt shock shoot shore short shout shown sight since skill
skirt sleep slice slide slope small smart smile smoke snack snake solid solve
sorry sound south space spare speak speed spell spend spice spill spine split
spoke sport spray stack staff stage stair stake stand stare start state steam
steel steep steer stick still stock stone stood store storm story stove strip
stuck study stuff style sugar suite sunny super swear sweat sweep sweet swept
swift swing table taken taste teach teeth thank their theme there these thick
thief thing think third thorn those three throw thumb tiger tight timer tired
title toast today token tooth topic total touch tough tower track trade trail
train trait treat trend trial tribe trick tried troop truck truly trust truth
twice twist uncle under union unity until upper upset urban usage usual valid
value video virus visit vital vivid vocal voice waste watch water weave wedge
weigh weird whale wheat wheel where which while white whole whose wider woman
women world worry worse worst worth would wound write wrong wrote yacht yield
young youth zebra
""".split())

# Small built-in fallback. The separately licensed SCOWL SQL asset expands
# accepted guesses on first startup; targets remain this curated word bank.
EXTRA_ALLOWED_WORDS = ("adieu", "audio", "fibre", "slate", "soare", "tears", "rates", "arose")
ALLOWED_WORDS = frozenset((*WORDLE_TARGETS, *EXTRA_ALLOWED_WORDS))

FILL_IN_BLANK_QUESTIONS = (
    ("A week has seven ____.", "days"),
    ("Water freezes into ____ when it gets cold enough.", "ice"),
    ("We use our ears to ____ sounds.", "hear"),
    ("A person who teaches students is a ____.", "teacher"),
    ("The opposite of hot is ____.", "cold"),
    ("Bees make sweet ____.", "honey"),
    ("A young dog is called a ____.", "puppy"),
    ("The season after winter is ____.", "spring"),
    ("There are twelve months in a ____.", "year"),
    ("You wear shoes on your ____.", "feet"),
    ("A person who bakes bread is a ____.", "baker"),
    ("We use our eyes to ____.", "see"),
    ("A triangle has three ____.", "sides"),
    ("The opposite of empty is ____.", "full"),
    ("Birds build ____ to lay their eggs in.", "nests"),
    ("A person who writes books is an ____.", "author"),
    ("The past tense of go is ____.", "went"),
    ("The past tense of eat is ____.", "ate"),
    ("The plural of child is ____.", "children"),
    ("The plural of tooth is ____.", "teeth"),
    ("Yesterday, I ____ a letter to my friend. (past tense of write)", "wrote"),
    ("She has ____ her homework. (past participle of finish)", "finished"),
    ("If I study hard, I will ____ the test. (opposite of fail)", "pass"),
    ("My brother is taller ____ me.", "than"),
    ("This is the ____ interesting book I have ever read. (superlative)", "most"),
    ("Neither Anna ____ Ben likes olives.", "nor"),
    ("I have lived here ____ 2020. (since or for)", "since"),
    ("We have waited here ____ two hours. (since or for)", "for"),
    ("They ____ playing football when it started to rain. (was or were)", "were"),
    ("There ____ five apples in the bowl. (is or are)", "are"),
    ("She ____ not enjoy loud music. (do or does)", "does"),
    ("Please speak ____; the baby is sleeping. (adverb of quiet)", "quietly"),
    ("The runner moved ____ toward the finish line. (adverb of quick)", "quickly"),
    ("A word with the opposite meaning is an ____.", "antonym"),
    ("A word with a similar meaning is a ____.", "synonym"),
    ("We borrowed books from the ____.", "library"),
    ("A doctor works in a ____ to treat patients. (starts with h)", "hospital"),
    ("The sun rises in the ____.", "east"),
    ("The sun sets in the ____.", "west"),
    ("A caterpillar grows into a ____.", "butterfly"),
    ("The ____ of France is Paris. (main city)", "capital"),
    ("We should wash our hands ____ eating. (before or during)", "before"),
    ("A person who studies science is a ____.", "scientist"),
    ("The opposite of generous is ____.", "selfish"),
    ("The comparative form of good is ____.", "better"),
    ("The superlative form of bad is ____.", "worst"),
    ("The past tense of bring is ____.", "brought"),
    ("The plural of mouse is ____.", "mice"),
    ("I look forward to ____ you tomorrow. (correct form of meet)", "meeting"),
    ("She is interested ____ learning new languages. (preposition)", "in"),
)
