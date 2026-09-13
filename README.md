# TraderMath

A suite of 7 quant trading games, built to practice the probability, EV, and game theory skills that come up in trading interviews.

## Games

**Phase 0. Smoke test** (`run_phase0_smoketest.py`)
Quick check that the game engine and environment are set up right before running the real games.

**Phase 1. Dice game** (`run_phase1_dice_game.py`)
Classic expected value game. Roll a die, decide whether to take the payout or reroll. Tests fast EV math and knowing when to walk away.

**Phase 2. Card game** (`run_phase2_card_game.py`)
Probability game built around a deck of cards. You price bets or make decisions as cards get revealed and the odds shift. Tests conditional probability and updating on the fly.

**Phase 3. ETF arbitrage** (`run_phase3_etf_arbitrage.py`)
Simulates spotting and trading a mispricing between an ETF and its underlying basket of holdings. Tests relative value thinking and quick arithmetic across a basket of prices.

**Phase 4. Fermi estimation** (`run_phase4_fermi.py`)
Estimation problems where you break a big, hard to know question ("how many X are there") into smaller pieces you can reasonably guess. Tests structured mental math under uncertainty.

**Phase 5. Auction** (`run_phase5_auction.py`)
Game theory game around bidding. You figure out how much to bid given what you think something's worth and what others might bid. Tests strategy and avoiding the winner's curse.

**Phase 6. Secretary problem** (`run_phase6_secretary.py`)
The classic optimal stopping problem. Candidates (or options) arrive one at a time, and you accept or reject each on the spot, trying to pick the best one overall. Tests stopping rule strategy (the "37% rule" is the famous solution).

**Phase 7. Combined** (`run_phase7_combined.py`)
Runs multiple games together in one session instead of in isolation.

Note: these descriptions match the standard versions of these classic quant trading interview games. If your implementations do anything different, let me know and I'll fix the wording.

## Structure

- `core/`: shared game engine and logic used across games
- `games/`: individual game implementations
- `run_phaseN_*.py`: entry point to run each game on its own

## Running a game

```bash
python run_phase1_dice_game.py
```

Swap in whichever phase script you want to run.
