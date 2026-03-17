from __future__ import annotations

import argparse
import json
import os

from .analysis import analyze_asset
from .fetchers import MarketDataFetcher
from .models import MetricObservation


FETCHERS: dict[str, str] = {
    "sp500": "fetch_sp500",
    "nasdaq100": "fetch_nasdaq100",
    "semiconductor": "fetch_semiconductor",
    "a_share_dividend_low_vol": "fetch_a_share_dividend_low_vol",
}


def build_brief(asset_type: str) -> dict[str, object]:
    if os.environ.get("DAILY_INVESTMENT_BRIEF_FAKE_FETCH") == "1":
        observations = {
            "price_snapshot": MetricObservation("标普500", 6700, 6650, "前一交易日", "上升"),
            "cnn_fear_greed": MetricObservation("CNN恐惧贪婪指数", 22, 18, "前一交易日", "上升"),
            "vix": MetricObservation("VIX", 23.51, 27.19, "前一交易日", "下降"),
        }
        return analyze_asset(asset_type=asset_type, observations=observations, data_gaps=[])

    fetcher = MarketDataFetcher()
    method_name = FETCHERS[asset_type]
    observations, data_gaps = getattr(fetcher, method_name)()
    return analyze_asset(asset_type=asset_type, observations=observations, data_gaps=data_gaps)


def entrypoint() -> None:
    parser = argparse.ArgumentParser(description="Generate daily investment brief with live data fetching")
    parser.add_argument("--asset", required=True, choices=sorted(FETCHERS))
    parser.add_argument("--render-mode", choices=["structured", "report", "both"], default="both")
    args = parser.parse_args()

    result = build_brief(args.asset)
    if args.render_mode == "structured":
        print(json.dumps(result["analysis_json"], ensure_ascii=False, indent=2))
        return
    if args.render_mode == "report":
        print(result["report_text"])
        return

    print(json.dumps(result["analysis_json"], ensure_ascii=False, indent=2))
    print()
    print(result["report_text"])


if __name__ == "__main__":
    entrypoint()
