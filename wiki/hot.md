---
type: meta
title: "Hot Cache"
updated: 2026-07-05T00:00:00
tags:
  - meta
  - hot-cache
status: evergreen
related:
  - "[[index]]"
  - "[[log]]"
  - "[[Wiki Map]]"
  - "[[getting-started]]"
  - "[[DragonScale Memory]]"
---

# Recent Context

## Last Updated

2026-07-03 (session 21): **Quant-finance sweep — 8 papers ingested (2 batches × 4 parallel agents), 23 new pages.** Purpose: literature base for Scott's sector-ETF (XLK etc.) time-series alpha project. THE BUILD IS NEXT — baseline momentum backtest repo, not more reading.

**Sources**: [[kurth2026-trend-following-demise]] (CFM/Bouchaud: fast trend dead post-2009 on small-tick contracts; slow trend + large-tick survive), [[pollok2026-end-to-end-portfolio-policies]] (transformer's low turnover wins net; ties equal-weight), [[miao-polak-online-ensemble-sector-rotation]] (top-5 sector Sharpe 0.657, survives 5-15bps, COVID-robust), [[karatas2021-two-stage-sector-rotation]] (8 iShares sector ETFs; ESN wins), [[tan2023-spatio-temporal-momentum]] (single-layer net beats deep; turnover regularization), [[poh2020-learning-to-rank-cross-sectional]] (LambdaMART 3x Sharpe vs sorts, gross), [[sanderink2026-when-alpha-breaks]] (regime-trust gate is the dominant value driver; inverse-uncertainty sizing backfires; VIX gate ≈ coin flip), [[bailey-lopez-de-prado-2014-deflated-sharpe]] (expected max Sharpe under zero skill ~3.2 at N=1000 trials)

**New concepts**: [[Trend-Following]], [[Cross-Sectional-Momentum]], [[Sector-Rotation]], [[Tick-Size-Microstructure]], [[End-to-End-Portfolio-Optimization]], [[Learning-to-Rank]], [[Online-Ensemble-Learning]], [[Echo-State-Networks]], [[Turnover-Regularization]], [[Regime-Trust-Gating]], [[Deflated-Sharpe-Ratio]], [[Backtest-Overfitting]]. **New entities**: [[Jean-Philippe Bouchaud]], [[Capital Fund Management]], [[Marcos Lopez de Prado]]

**KEY cross-paper thesis** (now on [[quantitative-finance]] domain page): turnover, not gross accuracy, decides net survival — confirmed independently by Zhang, Pollok, Tan, Miao-Polak. Strategy design rules for the build: (1) simple architecture + low turnover + cost-awareness from day one; (2) rank cross-sectionally, don't forecast levels; (3) regime gate on top; (4) deflate the Sharpe by trials attempted; (5) beat 12-1 momentum rotation and SPY buy-and-hold or it isn't alpha.

**Infra notes**: `flock` missing on Windows Git Bash → wiki-lock.sh and allocate-address.sh both broken; fix running in separate session (task_ae6acc01); addresses c-000003..c-000025 allocated manually this session. C: drive hit 100% full mid-session; ~1.4GB freed by purging npm/pip caches; root cause of the 475GB usage still unidentified.

---

## Previous Session (20b)

2026-07-02: **Latin phrase backfill — 17 new concept pages** from the CW13 ingest (standing rule: every Latin term gets a full concept page going forward).

**New Latin phrase pages**: [[Azoth]], [[prima-materia]], [[anima-mundi]], [[principium-individuationis]], [[cognitio-matutina-vespertina]], [[Tabula-Smaragdina]], [[servus-fugitivus]], [[anima-rationalis]], [[humidum-radicale]], [[spiritus-vegetativus]], [[filius-philosophorum]], [[stella-matutina]], [[ignis-fatuus]], [[deus-absconditus]], [[ex-tenebris-lux]], [[homo-maximus]], [[coincidentia-oppositorum]]

**Standing rule now active in CLAUDE.md**: every Latin phrase in future ingests gets a full concept page — same depth as any other concept (frontmatter, domain, definition, Jung's context, related pages).

---

## Previous Session (20)

**New page**: [[Philosophical-Tree]] — Essay V in full: 32 spontaneous patient tree-pictures (world-tree, fire/water tree, tree-nymph, quaternity of light, danger of inflation); tetrasomia (four sons of Horus, Ezekiel's cherubim, Daniel's beasts); aqua permanens as image of wholeness; Dorn's metallic tree and the realism/nominalism dispute; rose-coloured blood and the Rosicrucian rose; Sophia-Achamoth suffering myth; tree as Self (women) vs. anima/animus (men); the eagle dream (symbol vs. reduction).

**Pages updated**: [[Mercurius]] (§10 Summary — six-point recap, Mercurius as Christ's *compensatory counterpart*, cognitio matutina/vespertina), [[jung-cw13-alchemical-studies]] (marked COMPLETE, full Essay IV+V sections), [[Dream-Analysis-and-Interpretation]] (new: the eagle dream), [[Fourfold-Quaternio]] + [[Aqua-Permanens]] (cross-links)

**KEY material**:
- Par. 289: the lapis is "at most a counterpart or analogy of Christ" — never Christ renamed
- Par. 295 KEY: Mercurius "stands in a **compensatory relation to Christ**" — bridges the abyss the purity of Christian dogma created
- Par. 299 KEY: "**Christ = archetype of consciousness; Mercurius = archetype of the unconscious**"
- Par. 304 KEY: the tree = "the self depicted as a **process of growth**"
- Par. 333: "The goal is neither height nor depth, but **the centre**"
- Par. 397 KEY: "**Symbols mean very much more than can be known at first glance**" — anti-reductionist stance vs. Freud's incest-reduction and literalist alchemists
- Par. 469 KEY: "**When our dream says 'eagle' it means an eagle**" — devaluation, not disguise, explains most apparent dream-camouflage (par. 479)
- Par. 482 (closing): alchemy lost its vital substance splitting into *oratorium* (mysticism) vs. *laboratorium* (chemistry) — "no one asks about the fate of the psyche"

## Previous Session (19l)

2026-06-30: CW 13 Essay IV pars. 272-281 — §6 continuation (uroboros, three-and-four), §7 Astrology/Archons/Saturn, §8 Mercurius and Hermes. New pages: [[Nigredo]], [[Ialdabaoth]], [[Filius-Macrocosmi]]. (Superseded/completed by session 20 above — Essay IV now fully closed out through par. 303.)

## Session Before That (19k)

**New source pages**: [[jung-cw11-psychology-religion]], [[jung-cw14-mysterium-coniunctionis]], [[edinger-ego-and-archetype]] (+ 10 chapter subpages in `wiki/sources/edinger-ego-archetype/`), [[jung-on-active-imagination]], [[hannah-active-imagination]], [[vonfranz-alchemical-active-imagination]]

**New concept pages**: [[Religious Function of the Psyche]] (CW 11 core claim — psyche has innate drive toward God-image; religion is psychological phenomenon), [[Coniunctio]] (CW 14 central symbol — *coniunctio oppositorum*, Sol/Luna union, the goal of the opus)

**New entity**: [[Barbara-Hannah]] (English-Swiss analyst 1891-1986; 30+ years with Jung; *Active Imagination* 1981)

**Key updates**: [[Active Imagination]] (major: 4-stage model in Jung's words, Hannah's practical additions, von Franz's alchemical two-stage framing solutio→coagulatio = albedo→rubedo), [[Unus Mundus]] (promoted to mature; Dorn's three degrees of union: *unio mentalis*, body, unus mundus; par. 769 psychophysical background; par. 786/788 psychoid factor)

**Edinger chapter structure** (10 subpages at `wiki/sources/edinger-ego-archetype/`):
- Part I: 01-the-inflated-ego, 02-the-alienated-ego, 03-encounter-with-the-self
- Part II: 04-the-search-for-meaning, 05-christ-as-paradigm, 06-being-an-individual, 07-trinity-archetype
- Part III: 08-metaphysics-and-unconscious, 09-the-blood-of-christ, 10-the-philosophers-stone

**Key synthesis**: Von Franz makes explicit what Jung only implied — active imagination follows the same two-stage structure as the alchemical *opus*: first *solutio* (loosening, albedo — the image dissolves and speaks), then *coagulatio* (crystallization, rubedo — the insight solidifies into life change). The two-stage model explains why active imagination without follow-through produces nothing.

---

## Previous Session (19k)

**Pages updated**: [[Mercurius]] (major additions: §4 Spirit and Soul, §5 Dual Nature/hermaphroditism, §6 Unity and Trinity/Azoth), [[jung-cw13-alchemical-studies]] (par. 258 + §§4-6)

**KEY material (pars. 258-271)**:
- Par. 258: Mercurius rejoices in fire "like the salamander" — unlike literal quicksilver, which vaporizes; hell-fire as "rearrangement of the heavenly, spiritual powers in the lower, chthonic world of matter"
- Par. 259: The philosophic Mercurius (*servus/cervus fugitivus*) is "**obviously a projection of the unconscious**... when the inquiring mind lacks the necessary self-criticism in investigating an unknown quantity"
- Par. 263: **Two sources of illumination** — *anima rationalis* (God-given, distinguishes man from animal) vs. mercurial life-soul (*inflatio*/*inspiratio* of Holy Spirit)
- Par. 266 KEY: "**The psychologem 'Mercurius' must therefore possess an essentially antinomian dual nature**" — water/fire only valid as one thing if that thing unites both
- Par. 267: Aurelia occulta self-portrait — "I am known and yet do not exist at all"; poison dragon, both sexes, heaven and earth, dark and light
- Par. 268: Hermaphroditism — Abraham le Juif forgery names Mercurius **Adam Kadmon**; "coincides with the psychological concept of the self"
- Par. 270-271: Unity-in-trinity predates Christian dogma; Mercurius = **Azoth** — "the A and O that is everywhere present," alpha/omega of Latin, Greek, Hebrew alphabets combined

---

## Previous Session (19j)

2026-06-29 (session 19j): **CW 13 Essay IV pars. 247-257 — Five Levels, Freeing Mercurius, Alchemy as Gnostic doctrine, Mercurius as water and fire.** 0 new pages, 2 updated.

**KEY**: Par. 249 five levels of consciousness; par. 252 alchemy as Gnostic Anthropos doctrine; par. 256 *coincidentia oppositorum* needs completion by absolute opposition.

---

## Previous Session (19i)

2026-06-29 (session 19i): **CW 13 pars. 234-246 — Essay III finale + Epilogue + Essay IV opens.** 1 new concept page, 1 source page updated.

**Pages created**: [[Mercurius]] (new — Essay IV §1; the Spirit in the Bottle, pars. 239-246)

**Pages updated**: [[jung-cw13-alchemical-studies]] (pars. 234-238 + Essay IV §1 added; Essay III now fully closed)

**KEY material from pars. 234-246**:

*Essay III conclusion (pars. 234-236)*:
- Par. 234: Venus's characters = sapphire, cheyri, ladanum, muscus, ambra; Venus Magistra = the Sophia of the *lumen naturae*; *Venus armata*; the *Chymical Wedding* Venus episode = key to understanding Paracelsus's Venus
- Par. 235: Year Aniadin = Rev. 20:4 = thousand-year reign; "life without end"
- Par. 236: "Man had been entrusted with the task of bringing to perfection the divine will implanted in nature, and this was a truly sacramental work." Lazarello: "I am a Christian, O King, and it is no disgrace to be that and an Hermetic at the same time."

*Epilogue (pars. 237-238)*:
- Par. 237: "Alchemy is... the forerunner of our modern psychology of the unconscious. Thus Paracelsus appears as a pioneer not only of chemical medicine but of empirical psychology and psychotherapy."
- Par. 238: **"As a man he had one father, but as a spirit he had two mothers."** *Ex tenebris lux*. "What was divided on a lower level will reappear, united, on a higher one."

*Essay IV: The Spirit Mercurius (pars. 239-246)*:
- **The Spirit in the Bottle** (Grimm): Spirit announces "I am the great and mighty spirit Mercurius!" in the roots of a giant oak
- Par. 241: The oak = "prototype of the **self**, a symbol of the source and goal of the individuation process"
- **Par. 243 KEY**: The spirit = ***principium individuationis*** = *spiritus vegetativus* of the tree; the lapis = "outward and visible sign of the realization of the self"; "the self has its roots in the body, indeed in the body's chemical elements"
- Par. 244: The Master who imprisoned Mercurius = God; "the alchemist competes with the Creator"
- Par. 245: Glass bottle = *vas Hermeticum* = *anima mundi*; glass = solidified water/air
- Par. 246: Mercurius = Wotan/pagan god forced underground by Christianity; soul of metals, *homunculus*, *serpens mercurialis*, night raven — all "synonyms for the devil"

**ESSAY III NOW FULLY CLOSED (pars. 145-238). ESSAY IV IN PROGRESS: pars. 239+**

---

## Previous Session

Navigation: [[index]] | [[log]] | [[overview]]

## Last Updated

2026-06-29 (session 19h): **CW 13 Essay III COMPLETE — pars. 215-233 (§§4A-4D).** 0 new pages, 3 updated.

**Pages updated**: [[Melusina]] (§§4A-4B major additions — the Raymond legend, veil of Maya, Shakti, hierosgamos, Adech = "my brothers"), [[jung-cw13-alchemical-studies]] (§§4A-4D added + key quotes), [[Lumen-Naturae]] (§4C Spirit and Nature).

**KEY material (pars. 215-233)**:
- Par. 216: Melusina appears at the catastrophic collapse of one's life structure — "an abysmal void that is now suddenly filled with an alluring vision"; she is both psychic vision and objective entity, "like a dream which temporarily becomes reality"
- **Par. 220 KEY**: "There is no doubt that the goal of the philosophical alchemist was higher self-development, or the production of what Paracelsus calls the *homo maior*, or what I would call **individuation**"
- **Par. 221 KEY**: "A wholeness, of which he is a part, wants to be transformed from a latent state of unconsciousness into an approximate consciousness of itself"
- Par. 222: The "acts of Melusina" = veil of Maya; *liquor Sophiae* extracted by distillation; "**Stupidity is the mother of the wise, but cleverness never**"; fixation = consolidation of feeling
- Par. 223: Melusina = deceptive Shakti who must return to the watery realm and become "a part of his wholeness" — conceived in the mind
- **Par. 226 KEY**: "**Adech is not MY self, he is also that of my brothers**" — the Self is simultaneously individual and collective; the coniunctio includes the transpersonal dimension
- Par. 229: The unconscious = "largely autonomous psychic system" compensating conscious biases AND anticipating future conscious processes = "**supra-consciousness**"
- Par. 233: Paracelsus "leaves to the theoreticians to discuss" whether the ecclesiastical sacrament or the alchemical opus is the true path — presumably both were true for him

**ESSAY III NOW COMPLETE (pars. 145-233). Essay IV: The Spirit Mercurius is next.**

---

## Previous Session

2026-06-29 (session 19g): **CW 13 Essay III (Paracelsus) — pars. 201-214 extracted (§§3B-4).** 1 new page, 4 updated. Total: ~201 pages | 27 sources.

**Pages created**: [[Scaiolae]] (concept, developing) — the four spiritual powers of the mind = four psychological functions; wheels of Elijah's chariot; "nothing of mortality" in them; Adech as their ruler.

**Pages updated**: [[Anthropos]] (upper triad + difficult Adech + labor Sophiae + thousand names added), [[Melusina]] (Dorn's key gloss: Melusina = *apparentem in mente visionem* — the vision in the mind), [[jung-cw13-alchemical-studies]] (§§3B-4 added), index.

**Key material (pars. 201-214)**:
- Par. 201: *Anima iliastri* moved to centre → "resounds as Aniadus, Adech, Edochinum" → birth of the Aquaster (born supernaturally)
- Par. 203: Three names = one deathless Original Man; the lapis had "a thousand names" — all ultimately names for the Anthropos in its material aspect
- Par. 205: Union with homo maximus → *vita cosmographica*; *corpus Jesahach* = *corpus glorificationis* = *corpus astrale* (resurrected body)
- Par. 206-207: The Scaiolae — four spiritual powers: *phantasia, imaginatio, speculatio, agnata fides* = Ruland maps to four functions; the *homo maximus* = "basis and cause of all division into four"
- Par. 209: *Labor Sophiae* = "process of coming to terms with the unconscious"; prima materia = "saturnine," "cast on the dunghill" = the shadow content awaiting encounter
- **Par. 210**: "that difficult Adech who crosses [the ego's] purpose at every misguided step, who gives fate an unexpected twist, and sets it as a task the very thing it feared" — proto-description of the Self's compensatory function
- **Par. 214 — KEY**: Dorn's gloss: **Melusina = "the vision appearing in the mind"** (*apparentem in mente visionem*) — the anima demythologized as imagination-function; the Cyphanta (vessel) holds the speculations until they crystallize into understanding
- Part 4 (The Commentary of Gerard Dorn) begins at par. 213 — the most modern psychological insights hidden in Paracelsus's final obscure chapter

**CW 13 status**: Essays I-II done. Essay III now complete through par. 214 (entire Essay III = pars. 145-212 done; Part 4 Dorn Commentary beginning). Essays IV-V pending.

---

## Previous Session

2026-06-29 (session 19f): **CW 13 Essay III (Paracelsus) — pars. 191-200 extracted (§§6, 3, 3A, 3B).** 0 new pages, 3 updated. Total: ~200 pages | 27 sources.

**Pages updated**: [[Melusina]] (Sloane 5025/*coniunetio animae cum corpore* + Komarios dialogue), [[Lumen-Naturae]] (§A "Light of the Darkness" — major addition), [[jung-cw13-alchemical-studies]] (§§6, 3, 3A, 3B added).

**Key material (pars. 191-200)**: *Coniunetio animae cum corpore* illustration (Ripley Scrowle, 1588); filius regis + mystagogue Hermes on mountain (Lambspringk); Cleopatra/Komarios dialogue — waters awakening dead in Hades — spring blossoming; Aniada = Christian Sacraments + powers that promote longevity; **par. 196**: Paracelsus on track of "psychic transformation incomparably more important than the red tincture"; **par. 197**: *lumen naturae* = light of the darkness itself, not from above — "turns blackness into brightness"; **par. 198**: "Not separation but union of natures was the goal of alchemy"; Democritus: "Nature rejoices in nature"; Great Magic Papyrus of Paris quoted; **par. 199**: symbol as tertium — "that in logic does not exist, but which in reality is the living truth"; par. 200: man's two life forces (natural + aerial).

**CW 13 status**: Essays I-II done. Essay III through par. 200 (§§1-3B). Essays IV-V pending.

---

## Previous Session

2026-06-29 (session 19e): **CW 13 Essay III (Paracelsus) — pars. 182-190+ extracted (§§3-5).** 1 new page created, 2 updated. Total: ~200 pages | 27 sources.

**Pages created**: [[Melusina]] (concept, developing).

**Pages updated**: [[Iliaster]] (centre/distillatio/Self section + Melissa/Iloch/Aniadus coniunctio section added), [[jung-cw13-alchemical-studies]] (Essay III §§3-5 added).

**Key material from Essay III §§3-5 (pars. 182-190+)**:
- Melusina = the aqua permanens who opens the filius's side with the lance of Longinus (woodcut from Reusner's *Pandora*, Basel 1588); her longing for a soul = the kingly substance hidden in the sea
- *Filius regius* / Rex marinus: "He lives and calls from the depths: Who shall deliver me from the waters?" The alchemical sea = *mare nostrum* = the unconscious (par. 183)
- Alchemical optimism vs. Church pessimism: "the dark background of the soul contains not only evil but a king in need of, and capable of, redemption"
- **Par. 189 — KEY**: "the *retorta distillatio ex medio centri* results in the activation and development of a psychic centre, a concept that coincides psychologically with that of the self"
- The centre: Dorn: "Nothing is more like God than the centre." The *sidereal balsam* / *corpus astrale* dwells in the heart like the sun; the distillation from the centre = Self-development
- Melissa/Iloch/Aniadus: purging Saturnine melancholy → supracelestial coniunctio → Enochdianus; Aniadus = springtime efficacy = "the true May"
- Illustrations: hermaphrodite/*filius* (Rosarium 1550); Rebis (1420); Melusina as aqua permanens (Pandora, 1588)

**CW 13 status**: Essays I-II fully extracted. Essay III in progress (§§1-5 done, pars. 145-190+). Essays IV-V pending.

---

## Previous Session

2026-06-29 (session 19d): **CW 13 Essay III (Paracelsus) — pars. 145-171+ extracted.** 4 new pages created. Total: ~199 pages | 27 sources.

**Pages created**: [[Paracelsus]] (entity, mature), [[Lumen-Naturae]] (concept, mature), [[Iliaster]] (concept, developing), [[Anthropos]] (concept, developing).

**Pages updated**: [[jung-cw13-alchemical-studies]] (Essay III §§1-2 added).

**Key material from Essay III §§1-2 (pars. 145-171+)**:
- Paracelsus's two mothers: Mater Ecclesia (Church, stayed faithful) + Mater Natura (nature, accessed via *lumen naturae*). His "Pagoyum" = pagan knowledge from the light of nature.
- *Lumen naturae*: second independent source of knowledge alongside revelation. From the Astrum: "Nothing can be in man unless it has been given to him by the Light of Nature, and what is in the Light of Nature has been brought by the stars." Precursor to the collective unconscious.
- Paracelsus's unconscious split: "He consisted of two persons who never really confronted one another." The conflict between "I under God" and "God under me" = the drive that led to Goethe's Faust → Nietzsche → "create a god from your seven devils."
- Khunrath on *filius philosophorum* = both Christ (from Microcosm) and Son of Macrocosm: "From the stone you shall know in natural wise Christ, and from Christ the stone."
- Primordial Man / *homo maximus* / Adech: "The true man is the star in us." "For heaven is man and man is heaven." Adam Kadmon = *filius philosophorum* = ἄνθρωπος φωτεινός. Cross-cultural: Purusha, Gayomart, Metatron, Gnostic Anthropos.
- Iliaster (ὕλη + ἀστήρ): stellar life-substance; Life = "a certain embalsamed Mumia"; Balsam = *spiritus mercurii* = pharmacological aspect of Iliaster. Three forms: sanctitus/paratetus/magnus.

**CW 13 status**: Essays I-II fully extracted. Essay III in progress (pars. 145-171+). Essays IV-V pending.

---

## Previous Session

2026-06-29 (session 19c): **CW 13 Essay II (Visions of Zosimos) — pars. 118-144 extracted (Essay II now complete).** 1 new page created, 3 pages updated. Total: ~195 pages | 27 sources.

**Pages created**: [[Lapis-Philosophorum]] (concept, mature).

**Pages updated**: [[Aqua-Permanens]] (deus absconditus section: par. 138), [[jung-cw13-alchemical-studies]] (Essay II extended to pars. 118-144, §§3-6 added), [[index]] (Lapis-Philosophorum entry added).

**Key material from Essay II §§3-6 (pars. 118-144)**:
- Lapis = *ἄνθρωπος πνευματικός* (spiritual man) = *natura abscondita* (par. 126); Pandora/Eve = anima who seduced the spirit into matter
- Lapis-Christ: the lapis *complements*, not signifies, Christ. "Far from *signifying* Christ, the lapis *complements* the common conception." (par. 127)
- *Filius macrocosmi* (Khunrath) vs *filius microcosmi* (Christ): the stone from cosmic matter vs the son from a human mother
- Assumption of Mary → 4th feminine principle → real quaternary vs Trinity's "mere postulate" of totality (par. 127)
- Stone-birth mythology: Mithras, Australian *churinga*, Navaho Estsánatlehi (turquoise goddess = anima + Self simultaneously), Iroquois flint-twin
- *Deus absconditus* (par. 138): "the divine water or its symbol, the uroboros, means nothing other than the *deus absconditus*, the god hidden in matter, the divine Nous that came down to Physis and was lost in her embrace"
- **The key statement of CW 13** (par. 140): "The mystical side of alchemy... is essentially a psychological problem. To all appearances, it is a concretization, in projected and symbolic form, of the process of individuation."
- Kékulé / Zosimos contrast (par. 143): Kékulé dreamed the benzol ring; Zosimos had the same quality of dream but projected it into chemistry. "Chemistry has nothing to learn from Zosimos. It is a mine of discovery for modern psychology."

**CW 13 status**: Essays I-II fully extracted (pars. 1-144). Essays III (Paracelsus), IV (Spirit Mercurius), V (Philosophical Tree) remain.

---

## Previous Session

2026-06-28 (session 19b): **CW 13 Essay II (Visions of Zosimos) — pars. 85-117 extracted.** 2 new pages created, 3 pages updated. Total: ~194 pages | 27 sources.

**Pages created**: [[Zosimos-of-Panopolis]] (entity, mature), [[Aqua-Permanens]] (concept, mature).

**Pages updated**: [[Uroboros]] (CW 13 section: Ion=uroboros=sacrificer, massa confusa, four elements), [[Vessel-Symbol]] (CW 13 krater section: pars. 96-117), [[jung-cw13-alchemical-studies]] (Essay II now extracted).

**Key material from Essay II (pars. 85-117)**:
- Vision series: bowl altar, priest Ion self-dismembering, Agathodaimon as "leaden man," Meridian of the Sun beheaded at step four
- Sacrificer = sacrificed (par. 91): Ion = uroboros = sacrificer — three aspects of one principle
- Aqua permanens (pars. 89-105): *humidum radicale* = *anima aquina* = imprisoned anima mundi; Osiris=Nile=lead=sealed tomb; water=fire=spirit; "nature applied to nature transforms nature"
- Krater (pars. 96-97): bowl altar = krater of Poimandres filled with Nous; Dorn: vessel = "squaring of the circle" = psychic readiness for the Self

---

## Previous Session

2026-06-28 (session 19): **Man and His Symbols (Jung + Henderson + von Franz + Jaffé + Jacobi, 1964) — full ingest.** 4 new pages, 6 updated. Total: 192 pages | 27 sources.

**Pages created**: [[jung-man-and-his-symbols]] (source), [[Joseph-L-Henderson]] (entity), [[Aniela-Jaffe]] (entity), [[Jolande-Jacobi]] (entity).

**Pages updated**: [[Anima and Animus]], [[Active Imagination]], [[Individuation]], [[Mandala Symbolism]], [[C.G. Jung]], [[Marie-Louise von Franz]].

**Key material extracted**:

Part 1 (Jung): sign vs symbol; dreams as autonomous compensatory productions; 8-year-old girl's cosmogonic dreams; the collective unconscious as museum of organs.

Part 2 (Henderson): Trickster as archetype of pre-moral tribal shadow (Winnebago cycles); initiation vs hero achievement as the critical diagnostic distinction; sacred marriage after initiation.

Part 3 (von Franz): Self as sphere — ego = bright field at center, Self = nucleus AND whole sphere; **Naskapi Mista'peo** ("Great Man" = the inner companion in dreams; individuation before religion); **Chuang-Tzu's oak tree** (the useless tree fulfills its nature and outlives the useful trees); four stages of anima (Eve/Helen/Mary/Sapientia) and animus (Tarzan/Shelley-Hemingway/Lloyd George/Gandhi) with all specific examples; anima as "radio tuned to the Self"; Self as deer in active imagination ("I am the connecting animal... I am your fate or the objective I"); dark side of Self (Bath Badgerd — approach the center wrongly and it petrifies you); Black Elk / Eskimo eagle festival as social dimension of individuation.

Part 4 (Jaffé): Cities as projected mandalas — **Rome as urbs quadrata** (Romulus's *mundus* pit + plow circle + two arteries = full mandala), medieval cities, Washington D.C., Angkor Wat; circle in modern painting = psychic dissociation (Delaunay, Matisse, Kandinsky, Klee, Mondrian — circle separated from square); UFOs as "visionary rumor" projecting the wholeness archetype onto the sky; modern art arc from de Chirico's dread through Marini's dying rider to Soulages's light behind darkness.

Part 5 (Jacobi): **Henry case** — 25-year-old engineer, 35 sessions, 50 dreams. Initial dream (dead men in blue suits = sterile intellect); saint/prostitute dream (enantiodromia); oracle dream → I Ching hexagram MENG (synchronistic confirmation); 50th dream = four-part mandala (masculine totality); "**The unlived life is an illness of which one can die**." Henry married nine months after analysis started = first half of individuation complete.

Conclusion (von Franz): Darwin/Wallace simultaneous discovery = synchronistic event; Pauli's "primary possibilities" = archetypes; natural numbers as archetypes; unus mundus; Heisenberg encounters himself in nature; Bohr's complementarity = conscious/unconscious structure.

**Pending**: CW 13 Essays II-V (Zosimos, Paracelsus, Mercurius, Philosophical Tree) still unread.

---

## Previous Session

2026-06-28 (session 17c): **Aion Lectures Lects 8-13 — symbol extraction pass.** 4 new concept pages from user screenshots (book pp. 62-96). Total: 183 pages | 25 sources. Pages: [[Teleiosis]] (mature), [[Book-of-Tobit]] (mature), [[Lower-Triad]] (mature), [[Leviathan]] (mature). Updated: [[Pisces-Aeon]] (planetary conjunctions section).

**Key new material**: Teleiosis (telos/teleios/teleiosis; Matt 5:48 should read "whole and complete" not "perfect"; Basilides' *principium individuationis*; *phulokrinesis* of the amorphous third sonship; repressed/exteriorized individuation as the failure mode). Book of Tobit (the analytic fish template: capture/extract/transform; Tobit = blind ego, Sarah = possessed anima, Tobias = hero, Raphael = Self as guide; fish = threatening libido become healing; Edinger's own initial dream variant). Lower Triad (Dante's three-faced Satan; three-legged horse; typological mechanism: three differentiated functions + three unconscious counterparts = two opposing triads; inferior function held by the dark mother; Antichrist = lower triad structurally). Leviathan (*pharmakon athanasias*; messianic banquet; parallel to Eucharist; destruction of God-image = annulment of human personality par. 170). Pisces-Aeon updated: planetary conjunctions table — Judaism=Jupiter+Saturn, Islam=Jupiter+Venus, Christianity=Jupiter+Mercury, Antichrist=Jupiter+Moon.

---

2026-06-28 (session 12): **Batch ingest — 13 new sources, 21 new concept pages, 4 new entities.** The core Jungian corpus is now substantially complete. Sources: CW 7, CW 6, CW 12, MDR, *Answer to Job*, *Synchronicity*, *Modern Man*, *Fairy Tales* (von Franz), Neumann *Origins*, James *Varieties*, Frankl *Man's Search*, Nietzsche *Beyond Good and Evil*, PACE ML paper. Key additions: [[Persona]]/[[Shadow]] compensation model, [[Mana Personality]], [[Confrontation with the Unconscious]], [[Active Imagination]], [[God-Image (Imago Dei)]] (+ contradiction callout vs Summum Bonum), [[Synchronicity]], [[Unus Mundus]], [[Uroboros]], [[Numinous Experience]], [[Logotherapy]], [[PACE Optimizer]]. Total: 179 pages | 25 sources.

---

2026-06-28 (session 17b): **Aion Lectures second half read (pp. 101-193, Lectures 14-25).** 3 new concept pages + 1 symbol updated. Total pages: 141. [[Fourfold-Quaternio]] (mature), [[Vessel-Symbol]] (mature), [[Reciprocality-Principle]] (mature). Updated: [[Lapis-Philosophorum]]. Full Aion Lectures ingest now complete — all 148 pages read directly.

**Key material (second half)**: Fourfold Quaternio (four stacked quaternios connecting Anthropos/Man/Serpent/Lapis/Rotundum into a circle; four realms spiritual/animal/vegetable/mineral; historical correspondence to 500-year periods of the Pisces Aeon); Formula of the Self (para 410; abstract fourfold quaternio = the four psychological functions in *circulatio*); Space-Time Quaternio (Kant's a priori forms = Self's organizing schema; "sine qua non for any apprehension of the physical world"); Philosophical Pelican (mandala with source A at center, B-C-D-E flowing out and returning); Vessel (projected into church/relationship/group; must return to individual); Reciprocality Principle (ego's weak quality = unconscious amplified reciprocal; product = 1 = the Self's wholeness; Heisenberg uncertainty between ego and Self); Chirographum (planetary handwriting imprinted on soul's descent); Clementine God-image (contained opposites before privatio boni split them); Monoimos the Arab (twoness; the Other inside; the little point).

## Previous Session

2026-06-28 (session 17): **Edinger's Aion Lectures ingested** (Inner City Books, 1996, 148 pp.). 25-lecture guide to Jung's *Aion* by Edward Edinger, from lectures at the C.G. Jung Institute of Los Angeles (1988–89). 8 new pages, 5 pages updated. Total pages: 137.

**New pages**: [[edinger-aion-lectures]] (source), [[Edward-F-Edinger]] (entity), [[Ego-Self-Axis]] (mature concept), [[Aion-the-concept]] (mature concept), [[Pisces-Aeon]] (mature concept), [[Inflation-Jungian]] (mature concept). Updated: [[Shadow]], [[Anima and Animus]], [[Self (archetype)]], [[C.G. Jung]].

**Key material extracted (pages 1–100 read directly)**:
- **Aion** as psychic organism: cluster of chronos/kairos/aion; inner water, life span, eternity, destiny; Mithraic god Aion = Boundless Time
- **Ego-Self Axis**: Edinger's core concept. Four stages of ego-Self development. Stage 3 = individuation begins. The Psychic Life Cycle (inflation → wounding → metanoia → reconnection)
- **Inflation**: entirely unconscious; universal default condition; symptom = growing disinclination to attend to environmental feedback; two failure modes (ego eaten by Self / Self eaten by ego)
- **Pisces Aeon**: 2,000-year Christian era as archetypal framework. Two fishes = Christ (vertical) and Antichrist (horizontal). Nodal points: 500 AD (St. Benedict), 1000 AD (Joachim of Flora / Cathars), 1500 AD (Reformation), 2000 AD (Aquarius transition)
- **Joachim of Flora**: Trinity as historical sequence (Father/Son/Holy Ghost = law → grace → spirit = original oneness → conflict → individuation); *ecclesia spiritualis*; the heretical sects as premature Holy Ghost inflation
- **Shadow work threshold**: ego must be strong enough first; Egyptian negative confession as preparatory ego-building; reflux flask as image for shadow analysis
- **Four states of anima/animus**: infantile → projected → possessed → conscious (functions filtering unconscious)
- **Three outcomes of coniunctio**: concrete marriage, concrete separatio (Ariadne/Dionysus), progressive conscious love
- **Fish symbolism**: Book of Tobit as the analytic fish story (catch → extract → apply); Leviathan = primordial infantile psyche; eucharistic food at the messianic banquet; destruction of God-image = annulment of human personality
- **Christ as Self-symbol**: *imago dei*; "Christ exemplifies the archetype of the self"; historical Jesus hidden behind Self-projection; *privatio boni* as the symbol's flaw; *descensus ad inferos* = descent into collective unconscious

**Why this matters for Scott's individuation**: The Aion Lectures frame the entire Jungian project in its historical context. The collapse of the collective religious container is not a tragedy to reverse — it is the precondition for finding the Self as a direct psychological reality. The Ego-Self Axis is the personal version of what the aeon transition demands collectively.

## Previous Session

2026-06-27 (session 16): **Dream filed** — [[2026-06-27 The Gun and the Mountain]]. First dream log entry. Gun as mid-transformation libido (not yet a symbol); Drew as persona-carrier (the photo industry life not lived), not a classical shadow figure; metal detectors as the persona's gatekeeping mechanism. Malnourishment = libido actively withdrawn from the wrong climb. Victory = reclaimed but not yet integrated energy. Next step: [[Active Imagination]] dialogue with the gun image. Active imagination source texts already in `.raw/` — ingest when ready. Total pages: 130.

## Previous Session

2026-06-27 (session 15): **AgentX paper ingested** (arXiv 2606.26859, Kuaishou, Jun 2026). Production multi-agent system for autonomous recommender system iteration. 2 new pages: [[SGPO]] (mature), [[agentx-kuaishou-2026]] (source). Total pages: 129.

**Key results**: 3-week deployment, 3 AgentX workers, 374 ideas → 10 launchable results. Per-worker: 8× concurrency, 13.8× LR productivity, 3.7× business value vs human engineer. Main Feed: +0.561% user app-time. Life Service: >RMB 100M annualized revenue. Self-evolution tripled idea pass rate (15%→45%) and quadrupled throughput in 3 weeks.

**Critical diagnostic finding**: 91.4% of failures are operational/infrastructure, not agent reasoning (64.7% from A/B platform resource conflicts; under 5% genuine agent mistakes). Implication: the highest-leverage improvement is an upstream conflict checker that queries AB-platform state *before brainstorming*, not a smarter generation model.

**SGPO**: the novel technique — turns execution trajectories into natural-language "semantic gradients" that revise individual subagent prompts offline, validated through paired replay. Applicable to any loop that records trajectories and can distinguish strategy failures from harness failures.

## Previous Session

2026-06-27 (session 14): **Loop Engineering paper ingested.** Source: `.raw/loop_engineering_paper.pdf` — 6-page practitioner research note applying the "loop engineering" concept (spring 2026, Boris Cherny/Peter Steinberger/Addy Osmani/Karpathy convergence) to autonomous quantitative trading. 3 new pages: [[Loop-Engineering]] (mature), [[Maker-Checker-Pattern]] (mature), [[loop-engineering-hedge-funds-2026]] (source). Updated [[quantitative-finance]] domain with new sub-area. Total pages: 127.

**Key claims from the paper**: Break-even capital for a profitable loop: $100K-$250K deployed ($40-90/day token cost). Healthy checker rejection rate: 40-60% of signals killed. 7 concurrent agents is the comfortable ceiling for one operator. Latency: 4-12 seconds (intraday-adequate, not HFT). The critical failure mode is *verification debt* — verifier tuned once, never recalibrated against STATE.md outcomes log. Risk monitor MUST run in an isolated worktree with no shared context with the maker, or the kill switch never fires when the maker drifts.

## Previous Session

2026-06-27 (session 13): **CW 12 alchemical symbol extraction complete.** Read PDF pages 50-310 (¶19-415 across Parts I, II, III). Created 6 new symbol pages + updated Ouroboros: [[Mercurius]] (mature — the most important alchemical symbol, standing at beginning and end of the opus), [[Prima-Materia]] (mature — the shadow as gold; rust as *vera prima materia*), [[Lapis-Philosophorum]] (mature — the goal; the Self realized; completeness not perfection), [[Coniunctio]] (mature — Maria Prophetissa axiom; Sol-Luna marriage; eye on the centre), [[Anima-Mundi]] (developing — world soul imprisoned in elements), [[Sol-and-Luna]] (developing — consciousness/unconscious, father/mother pair). The alchemical process map and symbol table now in [[jung/symbols/_index]]. Total pages: 124 (CW 12 alchemical layer is now the wiki's most developed symbolic resource after CW 5).

**Key insight this session**: Mercurius is CW 12's central symbol because he *is* the transformation process itself — not just an ingredient but the agent. "He stands at the beginning and end of the work: he is the prima materia, the caput corvi, the nigredo; as dragon he devours himself and as dragon he dies, to rise again as the lapis." The opus is circular (circulare/rota) because Mercurius both begins and completes it.

## Previous Session

2026-06-27 (session 12): **Vault infrastructure: domain conventions + Dataview dashboard.** No sources ingested. Key additions: [[dashboard]] (Dataview domain balance check — open when focus is unclear), [[business]] (AI consulting domain scaffold with service areas and next actions for the Hilo market), `_templates/strategy-note.md` (trading research template). `domain:` is now a universal required frontmatter field. `CLAUDE.md` updated with Domain Conventions. Domain split at this session: Depth Psychology ~90% of wiki, Quantitative Finance ~5%, Business 0%. The dashboard makes this visible every session.

## Previous Session

2026-06-26 (session 11): **Jung CW 8 *Structure and Dynamics of the Psyche* theory-extracted.** The theoretical backbone for the dream-symbol project. 1 source page ([[jung-cw8-structure-dynamics-psyche]]) + 3 structured documents in new `wiki/jung/theory/` folder + folder index. Documents: [[CW8 Theoretical Foundations]] (psychic energy/libido, causal-vs-final standpoint, entropy & tension of opposites, progression/regression, symbol formation, complex, archetype/instinct, the Self, synchronicity), [[CW8 Dream Methodology]] (compensation + its 3 modes, "taking up the context", the four-phase dramatic structure, dream-series & "big" dreams), [[CW8 Integration Framework]] (how CW 8 grounds CW 5 symbols + von Franz craft; thematic symbol bundles; second-half-of-life shift). All three feed the runnable loop [[Working with Dream Symbols]] (built session 11a). **Key find:** the ¶555 snake/treasure/cave "big dream" is CW 8 explicitly invoking the CW 5 corpus under a strict gate — the textbook case for *when* archetypal amplification is licensed.

**Session 11 directly read (PDF page = printed page = CW ¶):**
- *On Psychic Energy* ¶42–68 (pp. 40–56): "What to the causal view is *fact* to the final view is *symbol*" (¶45); symbol's value-quantum exceeds the cause (¶47); energy from tension of opposites (¶49–50); progression/regression (¶60–66)
- *On the Nature of the Psyche* ¶421–430 (pp. 281–292): collective consciousness vs collective unconscious; the Self as totality-figure; *abaissement du niveau mental* (¶430)
- *General Aspects of Dream Psychology* ¶517–529 + *On the Nature of Dreams* ¶530–569 (pp. 353–385): "I have no idea what this dream means" (¶533); "taking up the context" (¶542); compensation (¶545–546); dream-series = individuation (¶550); the four-phase dramatic structure exposition→development→culmination→lysis (¶561–565)
- *Synchronicity* ¶963–968 + *On Synchronicity* ¶969–984 (pp. 648–662): definition (¶969); Pauli quaternio (¶963); archetype as *a priori* psychic orderedness (¶965); the golden scarab case (¶982–983)
- Synthesized (not full-fidelity read): *A Review of the Complex Theory* ¶194–219; *The Stages of Life* ¶749–795 — flagged in the documents.

Earlier this session: built [[Working with Dream Symbols]] — the methodological controller governing when the symbol corpus is consulted (the highest-leverage item from the dream-app to-do list). Total sources: 10. Domains: 2.

---

2026-06-24 (session 10): **Jung CW 5 Symbols of Transformation ingested.** Magnum opus on symbol, myth, and psychological transformation. Complete 1273-page scan. 1 source page + 4 new concept pages + 2 new entity pages + expanded 2 existing concept pages. New concepts: [[Libido Transformation]] (psychic energy as genuine transformation, not sexual reduction), [[Hero Archetype]] (individuation as the hero's journey), [[Symbol and Myth]] (myth as direct collective unconscious expression), [[Psychological Sacrifice]] (ego-death as necessary for transformation). New entities: [[Sigmund Freud]] (theoretical contrast), [[Miss Miller]] (case subject whose fantasies evidence the collective unconscious). Expanded: [[Mother Archetype]] (battle for deliverance, the Dual Mother), [[Individuation]] (hero's journey pattern, second-half-of-life transformation). Total pages: 85. Sources: 9. Domains: 2 (depth-psychology, quantitative-finance).

**Session 10 core material (directly read):**
- Complete frontmatter, TOC, plates (pp. 1-35): Jung's three forewords establish his break from Freud's reductionism
- Core thesis: myth is psychological fact, not primitive science or sexual disguise; the hero myth expresses the individuation journey; Miss Miller's fantasies recapitulate universal archetypal patterns
- CW 5 is the definitive articulation of: libido transformation (vs. Freud's reduction to sexuality), symbol as bridge (not disguise), comparative mythology as psychological method, the Mother Archetype as both source and obstacle in psychological development, sacrifice as necessary to ego-death

---

2026-06-24 (session 9): **Jung CW 9i essays I & II extracted.** Continuation of CW 9i ingest. 2 new foundational essay pages created: [[Archetypes of the Collective Unconscious]] (1934/1954) and [[Concept of the Collective Unconscious]] (1936). Directly read paras 1-95 (pp. 1-130): Jung's definition of archetype, myths as inner psychological drama, Western symbol-poverty post-Reformation, anima as archetype, instinct-archetype analogy, archetype vs historical elaboration, possession danger, consciousness vs unconscious. Total pages: 65. Sources: 8. Domains: 2.

**Session 9 core concepts (paras 1-95 directly read):**
- Archetypes are not concrete images but predispositions to form images (pre-existent forms, like Platonic eidos)
- Personal unconscious = complexes (feeling-toned forgotten material); Collective unconscious = archetypes (inborn, hereditary, universal forms)
- Myths are NOT allegories of nature but symbolic expressions of the inner, unconscious drama of the psyche
- Reformation iconoclasm broke the "protective wall of sacred images," leaving Western consciousness impoverished in symbols
- Archetype vs historical elaboration: the archetype is raw and naive in dreams; polished and elaborated in myths and dogmas
- The anima is one archetype among many, not the whole unconscious; she is felt as "outside" and projected onto women
- Archetypes are patterns of instinctual behavior — a hypothesis no more mystical than admitting humans have instincts
- Consciousness separates and isolates; the unconscious experiences everything indivisibly (participation mystique)
- The archetype of meaning is the final achievement of individuation; the paradox is life is meaningless without interpretation

2026-06-24 (session 8): **Von Franz Dreams (1998) ingest complete.** New source: Marie-Louise von Franz's *Dreams* (Shambhala 1998, 220 pages). 11 new pages created: source summary, 2 concepts (Dream Analysis & Interpretation; Dreams as Self-Knowledge), 7 historical figure entities (Socrates, Descartes, Themistocles, Hannibal, Monica, Bernard, Dominic), 1 expanded entity (Marie-Louise von Franz). Total pages: 63. Sources: 8. Domains: 2 (depth-psychology, quantitative-finance).

**Session 8 core content (pp. 1-134 directly read):**
- Foreword + Chapter 1 (The Hidden Source of Self-Knowledge, pp. 1-20): Delphic "gnothi seauton" maxim; philosophy vs religion in self-knowledge; dreams as access to unconscious wisdom
- Chapter 2 (How C.G. Jung Lived with His Dreams, pp. 21-34): Jung's earliest dream (childhood, ritual phallus/man-eater); amplification method; Jung's two personalities ("No. 1" and "No. 2"); synchronistic phenomenon (Jung's 1913 WWI vision); dreams as messages from superior intelligence
- Chapter 3 (The Dream of Socrates, pp. 35-64): Two dreams from Plato (*Phaedo*, *Crito*); white woman as anima; Socrates' split consciousness (Logos without Eros); failure to integrate the feminine
- Chapter 5 (Bernard/Dominic mothers, pp. 94-106): Aleth's dream (white/red dog); Bernard's mother complex; Dominic's mother's dream (dog with torch); alchemical color stages (albedo, rubedo); warrior saints caught between contemplation and action
- Chapter 6 (Descartes, pp. 107-126): Descartes' 1619 enlightenment at Ulm; three dreams; mathematical breakthrough; critique of how Descartes rejected the dream's message (anima, feminine, irrational); Cartesian split as historical tragedy

---

2026-06-24 (session 7): **Jung Dream Analysis, Lecture VI complete + Winter Second Part Lectures I-V (pp. 75-134 directly read).** Source page [[jung-dream-analysis-1928-1930]] expanded with 60 more pages. Now covers pp. 3-134; Dreams [1]-[5] fully analysed. Total pages unchanged: 52.

**Session 7 core content (pp. 75-134):**
- Lecture VI completion (pp. 75-82): Bush fear; shadow = "you are my brother, I must accept you"; Jewish legend of Evil Demon of Passion (Talmud Yoma 69b; Scholem footnote); Rider Haggard's *She* as anima paradigm; anima as filter/mood-regulator; "crept up 365 steps" active imagination
- Winter Second Part Lec. I (23 Jan): Dream [2] (tailoress/T.B.); tailoress = maker of new skin/new immortality; Negro shedding-skin myth; two machines = two methods; "Analysis fastens them together, and that is integration"; Eros vs. Logos asymmetry; woman's two minds (natural/conventional); Penguin Island "Donnez leur une ame mais une petite"
- Winter Second Part Lec. II (30 Jan): Mr. Gibb's question on symbol vs. generalization; Jung: "The symbol is a fact, not a facade"; Dream [3] (steamroller/labyrinth from above); Dante's wood; Jacob Bernoulli spiral gravestone "Eadem mutata resurgo"; Gilgamesh = Perfect Man two-thirds divine; diastole/systole; two melodies (masculine/feminine amplitudes)
- Winter Second Part Lec. III (6 Feb): FIRST USE of term "mandala" in seminar (footnote 1); patient's drawing = first intimation of whole analysis purpose; I Ching Hexagram 50 Cauldron (ting) = technique for producing new man = lapis lapidum = alchemist's retort = krater; Dream [4] (cage/four chickens); tapas (Sanskrit self-incubation); chickens = inferior feeling function; eagles vs. chickens distinction
- Winter Second Part Lec. IV (13 Feb): Akbar Divan-i-Khas at Fatehpur Sikri; Chichen Itza mandala (Earl Morris/Carnegie, 1929); Chinese "Square Inch Field" = Imperishable Body; Secret of the Golden Flower; analysis = I Ching = Yoga; astrology: spring point at 29 Pisces, entering Aquarius; four sons of Horus; Christ = three unconscious + one conscious function; restriction mentale
- Winter Second Part Lec. V (20 Feb): Dream [5] (saint Papatheanon/sciatica/shore/youngest son); sea = primordial medium; conscious = bay in unconscious; connection to Cauldron = pharmakon athanasias; Egyptian priest reads Isis/Ra hymn for snake-bite; Galen; Pleroma (Gnostic, opposites together); Mulungu/Mana; papa = Pope/patriarch; Mithras papyrus; sciatica = no forward movement = "no physical relation to his wife"

---

2026-06-24 (session 4): **arXiv 2605.21504 ingested.** Das, Goyal, Yadav (Santa Clara U.), "Multivariate Financial Forecasting using the Chronos Time Series Foundation Models." 1 source page created; [[quantitative-finance]] domain expanded. Total pages: 51. Sources: 6.

**Key claims (directly read):**
- Chronos-2 (open-source, zero-shot, encoder-only transformer with group attention) evaluated on Magnificent-7 stocks (AAPL, AMZN, GOOGL, MSFT, NFLX, NVDA, TSLA) and 10 Treasury maturities (DGS3MO-DGS30), rolling monthly 2000-2025
- MV consistently beats UV: ~60% MAPE improvement for rates; ~16% for stocks; improvement holds for every individual series
- Cross-domain mixing degrades accuracy: rates + stocks combined slightly worse than each group separately (MV gains are domain-conditional)
- Input window length n in {126, 252, 504, 756} days makes little difference
- Post-2023 forecasts more accurate than pre-2023, ruling out leakage from Chronos pre-training
- Not a portfolio-return or alpha claim; result is about raw forecast accuracy (RMSE/MAPE)

**Chronos-2 key design:** patch-based encoder, Time Attention (RoPE within-series) + Group Attention (cross-series at each patch index), sinh^-1 robust scaling, 21-quantile probabilistic output, zero-shot deployment.

**Notable:** Appendix A discloses paper was produced with AI assistance (Gemini + GPT-5.2 / OpenAI Prism for drafting; human final editing).

---

2026-06-24 (session 3b): **Full extraction of arXiv 2606.09420 (pp. 1-20, all tables).** [[zhang2026-benchmarking-deep-ts-equity]] source page expanded with all 15 model names, Tables 3/5/6/7/9/10/12/15, formal definitions, and data design details.

**15 models (Table 2):** TS-RIDGE, TS-OLS, AR1-GARCH11 (linear); LSTM, GRU, RNN (recurrent); TransEnc-8, TransEnc-10, PatchTST-8, PatchTST-16, NBEATS (transformer/patch/residual); TSMixer-8, TSMixer-10, MoE-MLP, GraphRNN (mixer/graph).

**Five promoted models** (constrained-portfolio follow-through set): TS-RIDGE, LSTM, TransEnc-8, TransEnc-10, TS-OLS.

**Key numerical results (directly read):**
- Table 3: TS-RIDGE gross Sharpe 3.88 (turnover 7.95); TransEnc-8 0.71 (turnover 0.66); LSTM 0.98 (turnover 1.21)
- Table 6 SMAA rank-1: TransEnc-8 0.352, TS-RIDGE 0.199, PatchTST-16 0.172, LSTM 0.168
- Table 9 cost sensitivity: TS-RIDGE leads at 0-10 bps; LSTM/TS-RIDGE tied at 20 bps; TransEnc-8 leads at 50 bps
- Table 12 constrained-QP net Sharpe: TransEnc-8 -0.76 (best); TS-RIDGE -2.37; TS-OLS -3.99 (all negative)
- Table 15 deployment regret: TransEnc-8 regret=0 (selected); LSTM 0.49; TS-RIDGE 1.61; TS-OLS 3.23
- Table 10 regime: LSTM dominates high-volatility (rank-1 0.470); TransEnc-8/10 dominate low-volatility (0.337/0.230)
- Kendall tau = 0.80 between SMAA expected ranks and constrained-QP ranks, stable 0-50 bps

**Formal core:** 7-criterion vector V_m = (SR_gross, SR_net20, SR_vw, |t_FF5|, -TO, -MDD, 1-p_m). Deployment-adjusted index = Gibbs update: DA_m proportional to RA_m(1) exp{-R_m^d / tau_d}. Turnover-weight alignment: lambda(u) = kappa * u / (1-u) (Proposition 4).

---

2026-06-24 (session 2): **Jung CW 9ii (Aion) ingest complete.** 3 new pages created; 7 meta pages updated. Pages: [[jung-cw9ii-aion]], [[Self (archetype)]], [[Ego]]. Shadow and Anima/Animus expanded to mature. Directly read: Foreword + Chs I-V (paras 1-71).

**Key Aion claims (directly read):** Ego = center of consciousness, subordinate to Self; Self = total personality, cannot be fully known; Shadow = moral problem, emotional/possessive, projection mechanism; Anima NOT a substitute for the mother; marriage quaternio (ego-shadow-syzygy-Self); "Christ exemplifies the archetype of the self" (para 70); net Sharpe at Pisces aeon end = antimimon pneuma.

---

2026-06-24 (session 1): **Jung CW 9i ingest complete.** New domain [[depth-psychology]] created. 10 new pages, 6 meta pages updated. Pages: source, domain, C.G. Jung, Collective Unconscious, Archetype, Individuation, Shadow, Anima/Animus, Mother Archetype, Trickster, Mandala Symbolism.

---

2026-05-17 (very late): **v1.7.1 patch shipped locally** (branch `v1.7.0-compound-vault`, NOT pushed). Final verifier: 0/0/0/0 SHIP. Score: 100/100.

## Plugin State

- **Version**: 1.7.1 (local-only branch `v1.7.0-compound-vault`, no push, no tag)
- **Total wiki pages**: 52
- **Sources ingested**: 7
- **Domains**: 2 (depth-psychology, quantitative-finance)

## Style Preferences

- No em dashes (U+2014) or `--` as punctuation. Periods, commas, colons, or parentheses.
- Short and direct responses. No trailing summaries.
- Parallel tool calls when independent.

## Active Threads

- Jung CW 9i and CW 9ii ingested. Follow-on: CW 12 (Psychology and Alchemy), CW 6 (Psychological Types).
- arXiv 2606.09420 ingested; quantitative finance domain open for more papers.
- v1.7.1 local only. No push or tag without explicit user go.
- CLAUDE.md has pre-existing uncommitted change ("Release Blog Post" section).

## Repo Locations

- Working: `~/Desktop/claude-obsidian/`
- Public: https://github.com/AI-Marketing-Hub/claude-obsidian
