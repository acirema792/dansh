# Verifier round 5: ccb9302 (parent b557550)

Scratch: /tmp/chk6 (clone in repo/, parent worktree parent/). No edits made in /home/claude/dansh.

## 1. Test suite (/home/claude/dansh, HEAD ccb9302)
```
222 passed in 8.40s
```

## 2. Cheating / gate check
- `git diff b557550 ccb9302 --stat -- tests eval_cases eval_results app/content.py deploy LICENSE .env*` touches only tests/data/adversarial.json.
- Corpus: 548 -> 775 entries. Multiset comparison of (expect, message, all fields): 0 removed or relabelled, 227 added. The large diff line count is reformatting only.
- No test .py file changed. Protected paths are unchanged.

## 3-4. Fresh held-out set (/tmp/chk6/heldout5.json, labels fixed in scripts/make_heldout5.py before any run)
166 messages: 99 bite, 35 crit, 20 ctl, 12 animal. 16 are marked arguable. Novelty: 0 exact-substring hits against repo tests/, eval_cases/, loop/ or the /tmp/chk5 round-4 set.
(results follow)

| label | n | HEAD ccb9302 | parent b557550 |
|---|---|---|---|
| bite FALSE_SAFE | 99 | 15 | 18 |
| crit FALSE_SAFE | 35 | 0 | 0 |
| crit UNDER | 35 | 30 | 31 |
| ctl FALSE_ALARM | 20 | 8 | 8 |
| animal ANIMAL_MISROUTE | 12 | 1 | 1 |

FALSE_SAFE total: HEAD 15 (9 non-arguable); parent 18 (13 non-arguable).
UNDER total: HEAD 30 / 35; parent 31

### Every FALSE_SAFE at HEAD (A = arguable)
- - [OFF_TOPIC] `sap katne se pair sujgaya hai` trace=['R3 no snake/bite recognised -> ask']
- - [OTHER] `while milking the cow i got bitten on the foot, the foot is swelling` trace=['R1 other animal (other) -> out of scope']
- - [OTHER] `cleaning the cow shed got bitten on the toe, toe is swollen and painful` trace=['R1 other animal (other) -> out of scope']
- - [OTHER] `tying the goat got bitten on the hand near the haystack` trace=['R1 other animal (other) -> out of scope']
- - [OTHER] `buffalo shed me kaata papa ko raat ko, pair sooj gaya` trace=['R1 other animal (other) -> out of scope']
- - [OTHER] `near the pig pen got bitten on the ankle this evening` trace=['R1 other animal (other) -> out of scope']
- - [OTHER] `kneeling by the ant hill got bit on the knee, it hurts a lot` trace=['R1 other animal (ant) -> out of scope']
- - [OTHER] `while chasing the goat he got bit on the ankle in the field, it is swelling` trace=['R1 other animal (other) -> out of scope']
- - [INFO] `saanp dikha aur use chhoo kar nikal gaya, kya karu` trace=['R2 prevention question -> prevention advice']
- A [OFF_TOPIC] `ajgar ne lapet liya bachhe ko, chhudaya, ab kya karein` trace=['R3 no snake/bite recognised -> ask']
- A [OFF_TOPIC] `python coiled around my son's leg at the zoo, what now` trace=['R3 no snake/bite recognised -> ask']
- A [INFO] `kids say the snake did not bite, all fine, but now chhotu keeps nodding off` trace=['R2 prevention question -> prevention advice']
- A [INFO] `saanp dikha, chacha ne pakadne ki koshish ki, kya karein` trace=['R2 prevention question -> prevention advice']
- A [INFO] `saanp ghar me ghusa aur chhotu uske paas khel raha tha, kya karein` trace=['R2 prevention question -> prevention advice']
- A [OTHER] `a rat bit my son at night while he slept on the floor, now his foot is swollen` trace=['R1 other animal (rat) -> out of scope']

### Every UNDER at HEAD
- - [URGENT] `snake bit my father, now he keeps nodding off` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, aankhen bhaari ho rahi hain` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप ने काटा, आंखें भारी हो रही हैं` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `cobra bite, her speech is thick and slow` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ke kaatne ke baad haath nahi utha pa raha` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप ने काटा, जुबान लड़खड़ा रही है` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kata, pet me marod ho rahi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, she puked twice` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, his pee looks like black tea` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, nazar dhundli ho gayi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kata papa ko, behos ho gaye` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, he is unconsious` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit my mom, brething problem` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, foam at the mouth` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `krait bit him, his tongue feels heavy` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saap ne kata, pet me bahut dard` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit her, stomach is paining badly` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit my son, he says tummy ache` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, body is jerking` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit grandpa, he doesn't respond when we call` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, lips are going blue` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, beta khada nahi ho pa raha` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `cobra bite, he cant open his eye` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bite, wound keeps oozing and won't clot` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `snake bit him, he can't keep his head straight, it flops` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ne kaata, gale se kuch nahi utar raha` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `saanp ke kaatne ke baad bachha bilkul nidhaal ho gaya` trace=['R5 snake named, no danger signs yet -> URGENT']
- A [URGENT] `saanp ne kaata, chakkar aa rahe aur aankhen jhapak rahi` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप के काटने के बाद पेशाब का रंग गहरा भूरा हो गया` trace=['R5 snake named, no danger signs yet -> URGENT']
- - [URGENT] `सांप के काटने के बाद दम फूल रहा है` trace=['R5 snake named, no danger signs yet -> URGENT']

### False alarms / misroutes at HEAD (tolerated)
- FALSE_ALARM [URGENT] `my boss is a snake, he bit my head off today`
- FALSE_ALARM [POSSIBLE] `this mango is so sour it bites`
- FALSE_ALARM [URGENT] `naag panchami kab hai is saal`
- FALSE_ALARM [CRITICAL] `rose ke kaante se ungli pe khoon aa gaya`
- FALSE_ALARM [POSSIBLE] `the frost bites in the morning`
- ANIMAL_MISROUTE [POSSIBLE] `शहद की मक्खी ने काट लिया`
- FALSE_ALARM [URGENT] `saanp ki kenchuli mili store room me, safe hai kya`
- FALSE_ALARM [URGENT] `a snake crossed the road ahead of my bike, nobody was hurt`
- FALSE_ALARM [URGENT] `saanp ka sapna aaya kal raat, iska matlab kya hai`

### Outcome changes parent -> HEAD
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) `kutte ne jagaya tab dekha munna ke pair pe kaata hua hai`
- ok(URGENT) -> FALSE_SAFE(INFO) `kids say the snake did not bite, all fine, but now chhotu keeps nodding off`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) `kal rat 1 baje bachhi ke pair me kaata, sujan aa gayi`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) `rat 11 baje papa ko pair pe kaat liya, bahut jalan`
- FALSE_SAFE(OTHER) -> ok(POSSIBLE) `aaj rat sote waqt bete ko haath pe kaata, haath laal ho gaya`
- UNDER(URGENT) -> ok(CRITICAL) `सांप ने काटा, हाथ नहीं उठा पा रहा`
- FALSE_ALARM(URGENT) -> ok(INFO) `saw a cobra in the zoo today, so big`
- ok(INFO) -> FALSE_ALARM(URGENT) `saanp ki kenchuli mili store room me, safe hai kya`

## 5. Regression hunt on the new rules (/tmp/chk6/grid5.json, 51 messages, labels fixed in scripts/make_grid5.py before running; full output in grid_head.txt and grid_parent.txt)

| Group | HEAD false safe | parent false safe | Notes |
|---|---|---|---|
| (a) `_explicit_animal_biter` | 7 of 16 (2 of them arguable) | 9 of 16 | Pattern 1 (`animal + 0-2 words + bite word`) reads "**cow** was bitten", "**buffalo** got bit", "horse **stable got bitten**", "**cat** bowl got bitten" as the animal biting. One false safe is a **crit** message: `near the pig pen got bitten on the ankle, now he is vomiting` -> OTHER, items ['other_bite'], no go_hospital (R1b sends "108 first" but not the hospital plan) |
| (b) BITE_DENIED + ALL_FINE | **3 new** (1 arguable) | 0 | `the snake didn't bite but it scratched him, he is fine` -> INFO; `saanp kaata nahi, khali ragad ke gaya, sab theek` -> INFO; (A) `the snake did not bite her, she is fine, just puked once` -> INFO. All were URGENT at the parent. denied_fine does not look at person pronouns, contact verbs (scratched, ragad) or unlisted symptoms |
| (c) SIGHTING + ASK | 4 (2 arguable) | 4 | `saanp dikha aur uske upar gir gaya, kya karein` and `saanp ghus gaya kambal me, chotu andar tha, kya karu` -> INFO at both. Not new, but the new SIGHTING+ASK route keeps them INFO now that bare "kya" was removed from INFO_WORDS (the stated fix) |
| (d) SELF_BITE_STRONG | 2 | 3 | `I bit my lip and then something stung my foot` -> OFF_TOPIC; `i bit into a guava in the orchard and then felt a sharp sting on my ankle` -> OFF_TOPIC. The strong path ignores doubt words ("something") and body parts, and UNKNOWN does not contain "something stung" |
| (e) rat / raat | 2 (both arguable) | 4 | Fixed: "rat 2 baje", "kal rat ... kaata", "rat sote waqt". Regression (A): `chuhe ne kaata raat me, haath bahut sooj gaya` was POSSIBLE, now OTHER ("chuhe" added to OTHER); swelling after a night-time "rat" bite is still not treated as a possible snakebite (round-4 item 1, second half, not done) |
| (f) INFO_WORDS additions | **2 new** (1 arguable) | 0 | `it was like a snake, it went across her lap while she sat in the yard` -> INFO ("like a snake" is now an INFO word); (A) `kai saanp dikhe khet me, ek bachhe ke upar se gaya` -> INFO ("kai" = "several" in Hindi). Both were URGENT at the parent |

Grid regressions new in ccb9302 (parent ok -> HEAD FALSE_SAFE): 6 (3 non-arguable). Grid fixes (parent FALSE_SAFE -> HEAD ok): 8.

## 6. BENCHMARK-RESULTS.md "Audit-found inputs"
- "775 messages ... 767/775 as labelled, 0 false safes, 0 under-triage": **reproduced** (HEAD: 767 ok, 7 false alarms, 1 animal misroute).
- "corpus with its messages added stood at 78 false safes and 32 under-triaged" (before the fix): **reproduced** at b557550 (78 FS, 32 UNDER).
- "another animal is out of scope only when the message says it is the biter": **false.** `cleaning the cow shed got bitten on the toe, toe is swollen and painful`, `while milking the cow i got bitten on the foot, the foot is swelling` and `tying the goat got bitten on the hand near the haystack` all go to OTHER.
- "any bite word with a body part, a family member or an outdoor or night setting is a possible snakebite": **false** whenever the animal-biter regex fires (above), and for `I bit my lip and then something stung my foot`.
- "'kya kare' / 'what to do' alone no longer makes a message a general question": true for INFO_WORDS. But SIGHTING + ASK_WORDS brings the same effect back for any sighting verb: `saanp dikha aur use chhoo kar nikal gaya, kya karu` -> INFO.
- Line 50, "in every run, no bite message was ever left without a hospital referral": **false** on fresh input (9 non-arguable false safes in my held-out set).
- The section correctly says the corpus is a regression test, not a held-out score. The held-out number is the one below.

## Evidence summary
- Tests: 222 passed. Gate: protected paths unchanged; corpus was only added to (548 -> 775, 0 removed or relabelled); no test file changed. No cheating found.
- Fresh held-out set (166 messages), HEAD ccb9302 vs parent b557550:
  - **FALSE_SAFE: 15 vs 18.** Non-arguable: **9 vs 13.**
  - **UNDER: 30/35 vs 31/35.**
  - FALSE_ALARM: 8 vs 8. ANIMAL_MISROUTE: 1 vs 1.
- The 9 non-arguable false safes at HEAD:
  - 7 are animal-as-context bites sent to OTHER. `_explicit_animal_biter` pattern 1 treats "<animal> [0-2 words] got/was bitten" as the animal being the biter.
  - 1 is a sighting+touch sent to INFO.
  - 1 is a typo-only message sent to OFF_TOPIC.
- Danger-sign coverage is still a list of exact phrases. The commit added round 4's exact phrasings, and 30 of 35 fresh phrasings still stop at URGENT (puked, unconsious, brething, foam at the mouth, behos, nidhaal, dhundli, "pet me bahut dard", "दम फूल", "आंखें भारी"...). Round-4 required item 5 (suffix and SMS robustness) was not done.
- Regression grid: 3 non-arguable false safes are new in this commit. They come from the new BITE_DENIED+ALL_FINE rule (scratch, "ragad") and from the new "like a snake" INFO word. There is also 1 crit-labelled false safe: a pig-pen bite with vomiting goes to OTHER with no go_hospital item.
- BENCHMARK-RESULTS.md corpus numbers reproduce. Its routing claims ("out of scope only when the message says it is the biter"; "no bite message was ever left without a hospital referral") are contradicted by fresh input.

VERDICT: REJECT
