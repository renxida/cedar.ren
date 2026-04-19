# Anime is Iteration

Usually the anime you see is at least iterated once. First, manga. Then, anime.

Fullmetal Alchemist went through more rounds.

```
 2001    manga begins
           ↓
 2003    FMA                     speculative ending — manga wasn't done yet;
         (the "first" anime)     the anime had to wing its own conclusion
           ↓
 2009    FMA: Brotherhood        faithful re-adaptation — the manga was
                                 almost done; endings synced up
           ↓
 2010    manga ends
```

Shield Hero went even further. It started as wordvomit on [小説家になろう](https://syosetu.com/), got cleaned up into a <ruby>文庫<rt>ぶんこ</rt></ruby> light novel, became a manga, then the anime:

```
 2012   web novel         raw; posted chapter-by-chapter on Narou
   ↓
 2013   light novel       editor passes; MF Books imprint
   ↓
 2014   manga             visual grammar; paneling, pacing
   ↓
 2019   anime             sound, motion, color; the expensive final form
```

Each step costs more and commits harder. Each step catches things the last one missed.

Lots of opportunities to get feedback.

---

Reminds me of chip design.

A silicon tape-out costs millions and takes months. You don't start there.

```
 napkin math     is this even worth doing?
      ↓
 python sim      does the broad idea work? animate it.
      ↓
 C++ model       cycle-accurate golden reference; DV target
      ↓
 RTL             the actual Verilog; emulate, DV against the C++ model
      ↓
 FPGA            does it run real workloads?
      ↓
 silicon         $$$, lead time in months, can't undo
```

A bug caught on the napkin is free. The same bug in silicon is a respin.

You don't run the ladder once. You go back up when a lower rung surfaces something the rung above couldn't see.

Same shape both sides:

```
                                           cheap, speculative
                                                  ▲
   WRITING            SILICON                     │
   ─────────────      ──────────────              │
   napkin             napkin                      │
   web novel          python sim                  │
   light novel        C++ model                   │
   manga              RTL                         │
   anime              silicon                     ▼
                                           expensive, committed
```

The manga is the golden reference the anime DVs against. Fans notice when the anime diverges from the manga the same way a verification engineer notices RTL drifting from the C++ model.
