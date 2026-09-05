"""
Runs the Auction / Winner's Curse Game (Game 5) comparing the naive
raw-signal bidder against the optimal winner's-curse-corrected bidder.

Run: python run_phase5_auction.py
"""

from core.harness import compare_strategies
from core.reporting import print_comparison_table, plot_dashboard
from games.auction_winners_curse import AuctionWinnersCurseGame, NaiveRawSignalStrategy, OptimalWinnersCurseStrategy

if __name__ == "__main__":
    game = AuctionWinnersCurseGame()
    strategies = [NaiveRawSignalStrategy(), OptimalWinnersCurseStrategy()]

    results = compare_strategies(game, strategies, n_rounds=10_000, seed=42)

    print_comparison_table(results)
    plot_dashboard(results, save_path="phase5_auction.png")