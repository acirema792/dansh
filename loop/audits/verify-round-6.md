# Verifier round 6: b002768 (and ccb9302), base b557550

Scratch: /tmp/chk7 (clone in repo/). No edits made in /home/claude/dansh.

## 1. Test suite (/home/claude/dansh)
```
222 passed in 9.51s
```

## 2. Cheating / gate check
- `git diff --stat b557550 b002768 -- tests eval_cases eval_results app/content.py deploy LICENSE` touches only tests/data/adversarial.json.
- Corpus: 548 (b557550) -> 775 (ccb9302) -> 992 (b002768). Full-record multiset comparison (json.dumps sort_keys): 0 removed, 444 added vs base; 0 removed, 217 added vs ccb9302. No message relabelled. Diff size is reformatting (indentation) only.
- No tests/*.py changed; no assertion loosened.
## 3-4. Fresh held-out set (/tmp/chk7/heldout6.json, sha256 d622001b..., labels fixed in scripts/make_heldout6.py before any run)

216 messages: 97 bite, 51 crit, 25 ctl, 15 animal, 28 plain (snake named, no danger sign; expect URGENT). Arguable: 18 ({'bite': 11, 'crit': 4, 'ctl': 1, 'plain': 2}). Novelty: 0 exact-substring hits against the repo (tests/, eval_cases/, loop/, corpus) or the /tmp/chk5, /tmp/chk6 sets (2 initial duplicates were replaced before any run).

The crit items were written after reading FLAG_WORDS / FLAG_RE / SYSTEMIC_RE and aimed at phrasings those lists do not cover (as the task asks), so the crit numbers measure gap coverage, not prevalence.

| label | outcome | b002768 (all / non-arguable) | ccb9302 | b557550 |
|---|---|---|---|---|
| bite (97) | FALSE_SAFE | 17 / 12 | 19 / 14 | 27 / 20 |
| crit (51) | FALSE_SAFE | 0 / 0 | 0 / 0 | 0 / 0 |
| crit (51) | UNDER | 48 / 44 | 48 / 44 | 48 / 44 |
| plain (28) | FALSE_SAFE | 0 / 0 | 0 / 0 | 0 / 0 |
| plain (28) | OVER | 21 / 19 | 5 / 3 | 4 / 2 |
| ctl (25) | FALSE_ALARM | 15 / 14 | 14 / 13 | 17 / 16 |
| animal (15) | ANIMAL_MISROUTE | 0 / 0 | 0 / 0 | 0 / 0 |

Round-5 held-out set (/tmp/chk6/heldout5.json, 166) re-run for reference: b002768 0 FALSE_SAFE, 0 UNDER, 9 FALSE_ALARM, 1 misroute (ccb9302: 15 FS / 30 UNDER). The commit fixes exactly the previous verifier's set.

### Every FALSE_SAFE (bite) at b002768: 17 (A = arguable)
- - [INFO] `i sat on a snake by mistake, is it dangerous?` trace=['R2 prevention question -> prevention advice']
- - [INFO] `I stepped on a snake barefoot, should I worry?` trace=['R2 prevention question -> prevention advice']
- - [INFO] `picked up a snake thinking it was a rope, is that ok?` trace=['R2 prevention question -> prevention advice']
- - [INFO] `snake was in my shoe and i put it on, what should i do?` trace=['R2 prevention question -> prevention advice']
- - [INFO] `a snake got inside my kurta, it is out now, what to do?` trace=['R2 prevention question -> prevention advice']
- - [INFO] `saanp mere kapdon me ghus gaya tha, nikal gaya, kya karu` trace=['R2 prevention question -> prevention advice']
- - [INFO] `found a krait in my sleeping bag this morning?` trace=['R2 prevention question -> prevention advice']
- - [OFF_TOPIC] `papa khet se aaye to pair me do chhed hai aur jal raha hai` trace=['R3 no snake/bite recognised -> ask']
- - [OFF_TOPIC] `felt a sharp jab on my toe while walking home in the dark` trace=['R3 no snake/bite recognised -> ask']
- - [OFF_TOPIC] `kuch ne pair pe maara khet me` trace=['R3 no snake/bite recognised -> ask']
- A [OTHER] `kutte ne bhonka tab dekha chhotu ko kaata` trace=['R1 other animal (dog) -> out of scope']
- A [OTHER] `kal rat bite hua beti ke pair pe, sujan hai` trace=['R1 other animal (rat) -> out of scope']
- A [INFO] `a snake came out from under the mat i was sitting on, what now?` trace=['R2 prevention question -> prevention advice']
- A [INFO] `krait found in our bedding at dawn, didn't bite anyone it seems, all fine` trace=['R2 prevention question -> prevention advice']
- - [INFO] `the snake was inside my helmet, i wore it to work, what should i do?` trace=['R2 prevention question -> prevention advice']
- - [INFO] `snake was in the bucket i reached into, what now?` trace=['R2 prevention question -> prevention advice']
- A [INFO] `snake popped out of the toilet when i sat down, what to do?` trace=['R2 prevention question -> prevention advice']

### Every FALSE_SAFE (crit) at b002768: 0 (A = arguable)

### Every UNDER (crit) at b002768: 48 (A = arguable)
- - [URGENT] `snake bit my dad, he talks funny now` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, his words are jumbled` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `cobra bite, his voice is hoarse` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he can't get words out` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, chest feels tight` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kata, shwaas lene me takleef` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `sap ne kata, bolne me dikkat` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, awaz nahi nikal rahi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, pishaab laal ho gaya` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ke kaatne ke baad peshaab ka rang laal hai` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, urine looks like coffee` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he passed reddish urine` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit my boy, his wee is red` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, bruises appearing all over her body` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, he blacked out` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he's out cold` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he keeled over` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, he's zoning out` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, he isn't making any sense` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he is talking gibberish` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit my dad, he's drifting off` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, she can't stay awake` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, hosh kho diya` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kata, aankhe ulat gayi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kata, papa gir pade` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, bachhe ko mirgi aayi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, legs gave way` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, uthne ki taakat nahi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, gardan nahi sambhal rahi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he can't sit up` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he is retching` trace=['R5 snake named, no danger signs yet -> URGENT']
- A [URGENT] `snake bit him, he has been sick twice` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, his gut hurts` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, belly is sore` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, do baar ulty hui` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, womiting` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप ने काटा, होश खो दिया` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप ने काटा, आवाज नहीं निकल रही` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप ने काटा, हाथ-पैर में जान नहीं` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप ने काटा, सिर नहीं संभल रहा` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he is bluish` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he wont respond` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kata, papa bahut neend me hai` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, baar baar so ja raha` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he wont wake up` trace=['R5 snake named, no danger signs yet -> URGENT']
- A [URGENT] `saanp ne kaata, ankhon ke aage andhera` trace=['R5 snake named, no danger signs yet -> URGENT']
- A [URGENT] `snake bite, her whole body is shaking` trace=['R5 snake named, no danger signs yet -> URGENT']
- A [URGENT] `snake bit my son, he is wobbling when he walks` trace=['R5 snake named, no danger signs yet -> URGENT']

### plain -> CRITICAL at b002768: 21 of 28 (ccb9302: 5, b557550: 4)
- - `saanp ne kaata, ambulance aa rahi hai` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `saanp ne pair pe kaata, ghav ho gaya` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `saanp ne kaata, mujhe lag raha hai cobra tha` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `snake bite on leg, he started screaming` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `snake bit my daughter, she keeps scratching the spot` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `krait bit papa on the toe, hospital is not answering the phone` trace=["R4 danger signs ['unconscious'] -> CRITICAL"]  (ccb9302: CRITICAL)
- - `saanp ne kaata, ambulance wale phone nahi utha rahe` trace=["R4 danger signs ['unconscious', 'weakness'] -> CRITICAL"]  (ccb9302: URGENT)
- - `snake bit my brother, we will head straight to the hospital` trace=["R4 danger signs ['weakness'] -> CRITICAL"]  (ccb9302: URGENT)
- - `snake bite on my hand, the pain is so bad i can't stand it` trace=["R4 danger signs ['weakness'] -> CRITICAL"]  (ccb9302: CRITICAL)
- - `snake bite, the network is weak here, please tell what to do` trace=["R4 danger signs ['weakness'] -> CRITICAL"]  (ccb9302: CRITICAL)
- - `saanp ne kaata, doctor aa gaye` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `snake bit him on the ankle, he got up and walked home` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `सांप ने काटा, एम्बुलेंस आ रही है` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `saanp ne kaata, andhera ho gaya tha, dikha nahi` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- - `cobra bit my father's hand, he turned around and killed it` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- A `saanp ne kata, pair neela pad gaya` trace=["R4 danger signs ['breathing'] -> CRITICAL"]  (ccb9302: CRITICAL)
- - `saanp ne kaata, nazar nahi aaya kaunsa saanp tha` trace=["R4 danger signs ['ptosis'] -> CRITICAL"]  (ccb9302: URGENT)
- - `snake bit my son, everything is confusing, what to do` trace=["R4 danger signs ['unconscious'] -> CRITICAL"]  (ccb9302: URGENT)
- - `sir raat ko uthe to dekha saanp ne pair pe kaata` trace=["R4 danger signs ['weakness'] -> CRITICAL"]  (ccb9302: URGENT)
- - `saanp ne kaata, gaadi aa rahi hai, tab tak kya kare` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL']  (ccb9302: URGENT)
- A `snake bite, the wound is bleeding a little` trace=["R4 danger signs ['bleeding'] -> CRITICAL"]  (ccb9302: CRITICAL)

### False alarms / misroutes at b002768 (tolerated): 15
- FALSE_ALARM [URGENT] `saanp dikha khet me, door se, kisi ko kuch nahi hua`
- FALSE_ALARM [URGENT] `a snake crossed the road in front of us, we stopped the car`
- FALSE_ALARM [URGENT] `snake skin found behind the cupboard`
- FALSE_ALARM [URGENT] `my sister is scared of snakes`
- FALSE_ALARM [POSSIBLE] `ouch, a rose thorn pricked my finger in the garden`
- FALSE_ALARM [URGENT] `snakes and ladders khelte hue bhai ne cheating ki`
- FALSE_ALARM [URGENT] `naag panchami pe doodh chadhaya`
- FALSE_ALARM [URGENT] `the snake charmer at the fair had a cobra`
- FALSE_ALARM [URGENT] `the cobra pose in yoga hurts my back`
- FALSE_ALARM [POSSIBLE] `biting cold in the morning, kids have cracked lips`
- FALSE_ALARM [POSSIBLE] `this chilli bites`
- FALSE_ALARM [URGENT] `we killed a snake in the yard yesterday, nobody got hurt`
- FALSE_ALARM [URGENT] `saw a cobra in the garden from the window`
- FALSE_ALARM [URGENT] `saanp ka khel dekhne gaye mele me`
- FALSE_ALARM [URGENT] `kids playing with a rubber snake`

### Outcome changes ccb9302 -> b002768
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `it was dark, my father says a rat bit him on the toe while he slept on the floor`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `lizard bit him at night on the floor`
- ok(INFO) -> FALSE_ALARM(URGENT) [ctl] `kids playing with a rubber snake`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, ambulance aa rahi hai`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne pair pe kaata, ghav ho gaya`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, mujhe lag raha hai cobra tha`
- ok(URGENT) -> OVER(CRITICAL) [plain] `snake bite on leg, he started screaming`
- ok(URGENT) -> OVER(CRITICAL) [plain] `snake bit my daughter, she keeps scratching the spot`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, ambulance wale phone nahi utha rahe`
- ok(URGENT) -> OVER(CRITICAL) [plain] `snake bit my brother, we will head straight to the hospital`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, doctor aa gaye`
- ok(URGENT) -> OVER(CRITICAL) [plain] `snake bit him on the ankle, he got up and walked home`
- ok(URGENT) -> OVER(CRITICAL) [plain] `सांप ने काटा, एम्बुलेंस आ रही है`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, andhera ho gaya tha, dikha nahi`
- ok(URGENT) -> OVER(CRITICAL) [plain] `cobra bit my father's hand, he turned around and killed it`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, nazar nahi aaya kaunsa saanp tha`
- ok(URGENT) -> OVER(CRITICAL) [plain] `snake bit my son, everything is confusing, what to do`
- ok(URGENT) -> OVER(CRITICAL) [plain] `sir raat ko uthe to dekha saanp ne pair pe kaata`
- ok(URGENT) -> OVER(CRITICAL) [plain] `saanp ne kaata, gaadi aa rahi hai, tab tak kya kare`

### Outcome changes b557550 -> b002768 (FALSE_SAFE-relevant only)
- FALSE_SAFE(INFO) -> ok(URGENT) [bite] `saanp joote me tha aur maine pehen liya, kya karu`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `she was bitten by the haystack next to the buffalo shed`
- ok(URGENT) -> FALSE_SAFE(INFO) [bite A] `krait found in our bedding at dawn, didn't bite anyone it seems, all fine`
- FALSE_SAFE(OFF_TOPIC) -> ok(POSSIBLE) [bite] `bachhe ke pair pe kaatne ka nishan hai, subah dekha`
- FALSE_SAFE(INFO) -> ok(URGENT) [bite] `a snake fell from the roof onto the bed where the kids were sleeping`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `got bit on the leg while chasing the dog out of the field`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `dog was barking at the bushes and dad got bitten on the shin`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite A] `kutte ke saath khel raha tha, pair me kaat liya`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite A] `billi ke paas so raha tha raat ko, haath pe kaata`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite A] `goat ko chara de raha tha to ungli pe kaat liya`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `it was dark, my father says a rat bit him on the toe while he slept on the floor`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) [bite] `lizard bit him at night on the floor`
## 5. Regression grid (/tmp/chk7/grid6.json, 86 messages, sha256 650ae524..., labels fixed in scripts/make_grid6.py before running; full results g_new/g_mid/g_base.json)

| group | n | b002768 non-ok | ccb9302 non-ok | b557550 non-ok |
|---|---|---|---|---|
| (a) _explicit_animal_biter | 22 | ANIMAL_MISROUTE 2, FALSE_ALARM 1 | FALSE_ALARM 1, FALSE_SAFE 1 | FALSE_ALARM 1, FALSE_SAFE 5 |
| (b) R1e / R1f | 8 | 0 | FALSE_SAFE 6 | FALSE_SAFE 6 |
| (c) BITE_DENIED + ALL_FINE + _later_change | 13 | FALSE_ALARM 4, FALSE_SAFE 2 | FALSE_ALARM 2, FALSE_SAFE 2 | FALSE_ALARM 5 |
| (d) SNAKE_CONTACT_RE | 8 | FALSE_ALARM 4, FALSE_SAFE 2 | FALSE_ALARM 4, FALSE_SAFE 2 | FALSE_ALARM 1, FALSE_SAFE 3 |
| (e) FLAG_RE false matches (plain bites) | 11 | OVER 5 | OVER 4 | OVER 4 |
| (f) SYSTEMIC_RE + LOCAL_STATE | 14 | OVER 5, UNDER 5 | UNDER 7 | UNDER 7 |
| (g) INFO_WORDS / SIGHTING+ASK | 10 | FALSE_ALARM 1 | FALSE_SAFE 2 | FALSE_ALARM 1, FALSE_SAFE 2 |

Every non-ok grid row at b002768:
- (a) - ANIMAL_MISROUTE [POSSIBLE] `kutte ke kaatne se pair me ghav` trace=['R6 unknown bite / suspected krait -> POSSIBLE (treated as snakebite)'] (ccb9302 ok/OTHER, base ok/OTHER)
- (a) - ANIMAL_MISROUTE [CRITICAL] `kutte ne kaata tha pichle hafte, ab bukhar` trace=["R1e danger signs ['breathing'] although 'dog' named -> snakebite protocol", 'R1c animal (dog) named but uncertain -> treat as possible snakebite'] (ccb9302 ok/OTHER, base ok/OTHER)
- (a) A FALSE_ALARM [URGENT] `cow was bitten by a snake, should we worry about the milk?` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 FALSE_ALARM/URGENT, base FALSE_ALARM/URGENT)
- (c) - FALSE_ALARM [URGENT] `saanp ne kaata nahi, sab theek hai` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 FALSE_ALARM/URGENT, base FALSE_ALARM/URGENT)
- (c) - FALSE_ALARM [URGENT] `snake didn't bite, all fine, but i want to know which snake it was` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 ok/INFO, base FALSE_ALARM/URGENT)
- (c) - FALSE_ALARM [URGENT] `the snake did not bite, everyone is fine now` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 ok/INFO, base FALSE_ALARM/URGENT)
- (c) - FALSE_ALARM [POSSIBLE] `kaata nahi lekin dar gaya, sab theek` trace=['R6 unknown bite / suspected krait -> POSSIBLE (treated as snakebite)'] (ccb9302 FALSE_ALARM/POSSIBLE, base FALSE_ALARM/POSSIBLE)
- (c) A FALSE_SAFE [INFO] `the snake did not bite, he is fine, he was asleep under it` trace=['R2 prevention question -> prevention advice'] (ccb9302 FALSE_SAFE/INFO, base ok/URGENT)
- (c) A FALSE_SAFE [INFO] `the snake did not bite. all fine. he seems pale` trace=['R2 prevention question -> prevention advice'] (ccb9302 FALSE_SAFE/INFO, base ok/URGENT)
- (d) - FALSE_ALARM [URGENT] `the snake crawled into a hole, nobody hurt` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 FALSE_ALARM/URGENT, base FALSE_ALARM/URGENT)
- (d) - FALSE_ALARM [URGENT] `snake fell from the tree into the pond, how to remove it?` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 FALSE_ALARM/URGENT, base ok/INFO)
- (d) - FALSE_ALARM [URGENT] `saanp upar chhat pe hai, kaise bhagayein` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 FALSE_ALARM/URGENT, base ok/INFO)
- (d) - FALSE_ALARM [URGENT] `snake slid under the door, kya karein` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 FALSE_ALARM/URGENT, base ok/INFO)
- (d) - FALSE_SAFE [INFO] `a snake bumped me while i was sleeping?` trace=['R2 prevention question -> prevention advice'] (ccb9302 FALSE_SAFE/INFO, base FALSE_SAFE/INFO)
- (d) - FALSE_SAFE [INFO] `a snake was in my pocket?` trace=['R2 prevention question -> prevention advice'] (ccb9302 FALSE_SAFE/INFO, base FALSE_SAFE/INFO)
- (e) - OVER [CRITICAL] `snake bit my son, he jerked his foot away` trace=["R4 danger signs ['unconscious'] -> CRITICAL"] (ccb9302 ok/URGENT, base ok/URGENT)
- (e) - OVER [CRITICAL] `snake bit him, he is breathing normally` trace=["R4 danger signs ['breathing'] -> CRITICAL"] (ccb9302 OVER/CRITICAL, base OVER/CRITICAL)
- (e) - OVER [CRITICAL] `snake bit him, he is not vomiting` trace=["R4 danger signs ['vomiting_abdominal'] -> CRITICAL"] (ccb9302 OVER/CRITICAL, base OVER/CRITICAL)
- (e) A OVER [CRITICAL] `snake bit him, he can't move his toe because of the pain` trace=["R4 danger signs ['weakness'] -> CRITICAL"] (ccb9302 OVER/CRITICAL, base OVER/CRITICAL)
- (e) - OVER [CRITICAL] `saanp ne kaata, network weak hai, jaldi batao` trace=["R4 danger signs ['weakness'] -> CRITICAL"] (ccb9302 OVER/CRITICAL, base OVER/CRITICAL)
- (f) - UNDER [URGENT] `snake bite, he's gone quiet` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 UNDER/URGENT, base UNDER/URGENT)
- (f) - UNDER [URGENT] `snake bit her, she is acting strange` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 UNDER/URGENT, base UNDER/URGENT)
- (f) - UNDER [URGENT] `saanp ne kaata, ajeeb harkat kar raha` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 UNDER/URGENT, base UNDER/URGENT)
- (f) A UNDER [URGENT] `snake bit my son, he isn't himself` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 UNDER/URGENT, base UNDER/URGENT)
- (f) A UNDER [URGENT] `snake bit him, his face has gone pale` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 UNDER/URGENT, base UNDER/URGENT)
- (f) - OVER [CRITICAL] `snake bit him, he started limping` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL'] (ccb9302 ok/URGENT, base ok/URGENT)
- (f) - OVER [CRITICAL] `snake bit my dad, he kept working in the field` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL'] (ccb9302 ok/URGENT, base ok/URGENT)
- (f) - OVER [CRITICAL] `saanp ne kaata, khet me kaam ho raha tha` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL'] (ccb9302 ok/URGENT, base ok/URGENT)
- (f) - OVER [CRITICAL] `snake bit him, he got into the car` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL'] (ccb9302 ok/URGENT, base ok/URGENT)
- (f) A OVER [CRITICAL] `saanp ne kaata, bukhar aa gaya` trace=['R4b a body-wide change after the bite (not a listed sign) -> CRITICAL'] (ccb9302 ok/URGENT, base ok/URGENT)
- (g) - FALSE_ALARM [URGENT] `the snake game on my phone` trace=['R5 snake named, no danger signs yet -> URGENT'] (ccb9302 ok/INFO, base ok/INFO)

Grid changes ccb9302 -> b002768:
- (a) FALSE_SAFE(OTHER) -> ok(POSSIBLE) `a rat bit my son while he slept on the floor`
- (a) ok(OTHER) -> ANIMAL_MISROUTE(POSSIBLE) `kutte ke kaatne se pair me ghav`
- (a) ok(OTHER) -> ANIMAL_MISROUTE(CRITICAL) `kutte ne kaata tha pichle hafte, ab bukhar`
- (b) FALSE_SAFE(OTHER) -> ok(CRITICAL) `dog bit him and now he is vomiting`
- (b) FALSE_SAFE(OTHER) -> ok(CRITICAL) `monkey bit him and now his eyes are heavy`
- (b) FALSE_SAFE(OTHER) -> ok(CRITICAL) `bee stings all over, now he can't breathe`
- (b) FALSE_SAFE(OTHER) -> ok(CRITICAL) `scorpion sting, he is sweating and vomiting`
- (b) FALSE_SAFE(OTHER) -> ok(CRITICAL) `dog bit him, he is pale and sleepy`
- (b) FALSE_SAFE(OTHER) -> ok(CRITICAL) `kutte ne kaata, ab vo behosh hai`
- (c) ok(INFO) -> FALSE_ALARM(URGENT) `snake didn't bite, all fine, but i want to know which snake it was`
- (c) ok(INFO) -> FALSE_ALARM(URGENT) `the snake did not bite, everyone is fine now`
- (e) ok(URGENT) -> OVER(CRITICAL) `snake bit my son, he jerked his foot away`
- (f) UNDER(URGENT) -> ok(CRITICAL) `snake bite, he became very quiet`
- (f) UNDER(URGENT) -> ok(CRITICAL) `snake bite, she is getting groggy`
- (f) ok(URGENT) -> OVER(CRITICAL) `snake bit him, he started limping`
- (f) ok(URGENT) -> OVER(CRITICAL) `snake bit my dad, he kept working in the field`
- (f) ok(URGENT) -> OVER(CRITICAL) `saanp ne kaata, khet me kaam ho raha tha`
- (f) ok(URGENT) -> OVER(CRITICAL) `snake bit him, he got into the car`
- (f) ok(URGENT) -> OVER(CRITICAL) `saanp ne kaata, bukhar aa gaya`
- (g) FALSE_SAFE(INFO) -> ok(URGENT) `saanp dekha, bachha uske paas tha, kya karein`
- (g) ok(INFO) -> FALSE_ALARM(URGENT) `the snake game on my phone`
- (g) FALSE_SAFE(OFF_TOPIC) -> ok(URGENT) `python wrapped around my brother at the zoo`

### Mechanism notes (b002768)
- **_explicit_animal_biter**: works on everything I tried. Passive context ("got bit while chasing the dog", "dog was barking ... dad got bitten", "bitten by the fence near the goat pen at night") now goes to POSSIBLE. Active biters ("the dog bit my son", "kutte ne kaata", "bandar ka kaata", "bitten by our pet dog") stay OTHER. A small regression: `kutte ke kaatne se pair me ghav` is now POSSIBLE because the new BITE word "kaatne" is not in the hi_adj alternation (tolerated misroute). The 5-word "ne" window still reads `kutte ne bhonka tab dekha chhotu ko kaata` as a dog bite (arguable, also at the parent).
- **R1e / R1f**: works. All 6 "animal + body-wide danger sign" messages were OTHER with no go_hospital at ccb9302 and are CRITICAL now. Night/floor rat and lizard bites are POSSIBLE. Side effect: `kutte ne kaata tha pichle hafte, ab bukhar` -> CRITICAL, because FLAG_RE breathing `\bhaa?n?f\w*` matches **"hafte"** (Hindi for "week"). Also `saanp ne kaata tha do hafte pehle ...` -> CRITICAL ['breathing'].
- **BITE_DENIED + ALL_FINE + _later_change**: fixes round 5's "scratched"/"ragad" false safes. But `_later_change` treats any "but"/"now"/"just" as a change, so "did not bite, everyone is fine now" is now URGENT (tolerated). Two arguable false safes from ccb9302 remain: `the snake did not bite, he is fine, he was asleep under it` and `the snake did not bite. all fine. he seems pale`. The second happens because denied_fine also turns off SYSTEMIC. One arguable held-out regression vs base: `krait found in our bedding at dawn, didn't bite anyone it seems, all fine` -> INFO ("bedding" does not match `\bbed\b`).
- **SNAKE_CONTACT_RE**: over-matches ordinary words. `on my` in "the snake game on my phone"; `fell`/`slid`/`crawl`/`upar` in "snake fell ... into the pond", "slid under the door", "saanp upar chhat pe hai". These are false alarms only. It still misses contact verbs such as "bumped" and "sat on", and holding places such as pocket, shoe, kurta, helmet, bucket and sleeping bag (held-out false safes above).
- **FLAG_RE**: false matches on common words in plain bite messages make them CRITICAL:
  - "hafte" (week) -> breathing;
  - "is not answering", "phone nahi utha rahe", "isn't responding" (about the phone or hospital), "jagah" (place) -> unconscious;
  - "head straight to the hospital", "network/battery is weak", "can't hold on", "can't move her, no vehicle", "sir ... uthe" -> weakness;
  - "nazar nahi aaya" (didn't see it), "blurry photo" -> ptosis;
  - "everything is confusing" -> unconscious;
  - "jerked his foot away" -> unconscious;
  - "should we let it bleed?" -> bleeding.

  'breakfast', 'happening' and 'hospital not open' did not false-match. Negation also fails in some cases: "he is breathing normally" and "he is not vomiting" -> CRITICAL (also at the base).
- **SYSTEMIC_RE + LOCAL_STATE**: this is the main over-triage source. The Hinglish branch `<word> ho/aa/lag/pad raha/gaya` and the Hindi branch fire on any word not in a stop-list. Examples:
  - "ambulance aa rahi", "एम्बुलेंस आ रही", "doctor aa gaye", "gaadi aa rahi";
  - "mujhe lag raha hai", "ghav ho gaya", "andhera ho gaya", "kaam ho raha tha".

  The English branch fires on any verb after keeps/started/got/turned/kept: "started screaming", "keeps scratching", "got up", "turned around", "started limping", "kept working", "got into". It also misses body-wide changes that do not fit its templates: "he's gone quiet", "she is acting strange", "ajeeb harkat kar raha", "his face has gone pale", "he isn't himself". It does catch "became very quiet" and "is getting groggy".
- **INFO_WORDS / SIGHTING+ASK**: "kai" and "like a snake" were removed from INFO_WORDS. "python" and "zoo" are still INFO words, but "python wrapped around my brother at the zoo" now reaches URGENT. The remaining INFO false safes come from the `"?" in raw` and SIGHTING+ASK info markers, combined with snake_mention_only when no body part or person word is present.

## 6. BENCHMARK-RESULTS.md "Audit-found inputs"
- "992 messages ... 969/992 as labelled, 0 false safes, 0 under-triage": **reproduced** (b002768: 969 ok, 18 FALSE_ALARM, 5 ANIMAL_MISROUTE, 0 FS, 0 UNDER). ccb9302 on the same 992: 35 FS, 30 UNDER.
- "All 23 differences are over-triage": **true** for the corpus.
- Round-5 numbers quoted (15 FS, 9 non-arguable, 30 UNDER): **match** verify-round-5.md.
- "adds spelling-tolerant patterns for each danger sign": partly true. On round 5's exact phrasings it gives 30 -> 0 UNDER. On 51 fresh danger-sign phrasings it gives **48 UNDER (44 non-arguable), the same count as ccb9302 and b557550**. The patterns still cover few phrasings beyond the reported ones: "blacked out", "keeled over", "out cold", "talks funny", "chest feels tight", "pishaab laal", "urine looks like coffee", "hosh kho diya", "mirgi", "retching", "womiting", "ulty", "wont wake up" and "आवाज नहीं निकल" are all missed.
- "a body-wide change ... that matches no listed sign is CRITICAL": true for the template phrasings. It also contributes to plain held-out bites going CRITICAL: 21 of 28 at b002768 (11 via R4b SYSTEMIC, 10 via FLAG_RE false matches), against 5 at ccb9302 and 4 at b557550. The document does not mention this over-triage.
- "another animal is out of scope only when the message says it is the biter": **now true on everything I tried** (round 5 found this claim false).
- "any bite word with a body part, a family member or an outdoor or night setting is a possible snakebite": true on my probes. The remaining off-topic false safes have **no bite word** ("do chhed ... jal raha", "sharp jab on my toe in the dark", "kuch ne pair pe maara").
- Line 51, "in every run, no bite message was ever left without a hospital referral": **false** on fresh input. There are 12 non-arguable held-out false safes plus 2 in the grid. The claim holds only for the corpus.

## Evidence summary
- Tests: 222 passed. Gate: protected paths unchanged. The corpus was only added to (548 -> 775 -> 992; 0 removed or relabelled, by full-record multiset comparison). No test file changed. No cheating found.
- The corpus claim reproduces (969/992, 0 FS, 0 UNDER). Round 5's held-out set now passes completely (0 FS, 0 UNDER).
- Fresh held-out set (216 messages), b002768 / ccb9302 / b557550:
  - bite FALSE_SAFE: **17 / 19 / 27**; non-arguable **12 / 14 / 20**. All 12 non-arguable false safes were already present at the base. They are not new regressions, but they remain:
    - 7 are snake-contact messages sent to INFO by the "?" / SIGHTING+ASK marker: sat on, stepped on, picked up, shoe, kurta, kapde, sleeping bag, helmet, bucket.
    - 3 are no-bite-word outdoor injuries sent to OFF_TOPIC: "do chhed", "sharp jab", "kuch ne maara".
  - crit FALSE_SAFE: 0 / 0 / 0. crit UNDER: **48 / 48 / 48** (44 non-arguable). This set was aimed at gaps, so the new FLAG_RE and SYSTEMIC rules generalise little beyond the phrasings they were written for.
  - plain -> CRITICAL: **21 / 5 / 4** of 28. This is a large new over-triage, from SYSTEMIC_RE (R4b) and FLAG_RE false matches ("hafte", "ambulance aa rahi", "phone nahi utha rahe", "head straight to the hospital").
  - ctl FALSE_ALARM 15 / 14 / 17. Animal misroute 0 / 0 / 0.
- Grid (86 messages): R1e/R1f and the passive-voice animal fix work (8 false safes fixed vs ccb9302). New in b002768: 0 false safes, 3 new false alarms, 2 new animal misroutes ("kaatne" and "hafte") and 6 new plain -> CRITICAL. Remaining grid false safes: 2 non-arguable (`a snake bumped me while i was sleeping?`, `a snake was in my pocket?`) and 2 arguable.
- Decision rule:
  - non-arguable bite FALSE_SAFE > 0 (12 held-out + 2 grid) -> REJECT;
  - non-arguable crit UNDER = 44 > 3 -> REJECT.

VERDICT: REJECT
