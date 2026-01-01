"""
BTC Single-Core Updater for GitHub Actions.

Fetches Bitcoin blockchain data sequentially using the QuickNode API.
"""

import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from crypto_explorer import QuickNodeAPI

DATA_DIR = Path("data/onchain/BTC/block_stats_fragments")
INCREMENTAL_DIR = DATA_DIR / "incremental"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def update_onchain_data(api: QuickNodeAPI, max_blocks: int = 5) -> None:
    """
    Update on-chain block stats data sequentially.

    Parameters
    ----------
    quant_node_api : QuickNodeAPI
        QuickNode API instance for fetching block stats.
    max_blocks : int, optional
        Maximum number of blocks to fetch per run, by default 5.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If there are missing blocks in the existing data.
    """
    start_time = time.perf_counter()

    current_height = api.get_blockchain_info()["blocks"]
    logger.info("Current blockchain height: %d", current_height)

    # Load and validate existing data
    data = pd.read_parquet(DATA_DIR)
    if data["height"].diff().max() > 1:
        raise ValueError("Missing blocks detected in existing data")

    # Normalize timestamps
    data["time"] = np.where(data["time"] < 1e10, data["time"] * 1e+6, data["time"])
    data["time"] = np.where(data["time"] < 1e13, data["time"] * 1e+3, data["time"])
    data = data.set_index("time")

    last_height = int(data["height"].iloc[-1])
    blocks_to_fetch = min(current_height - last_height, max_blocks)
    logger.info("Last saved height: %d", last_height)

    if blocks_to_fetch <= 0:
        logger.info("No new blocks to fetch. Data is up to date.")
        return

    # Fetch blocks
    start_height = last_height + 1
    end_height = start_height + blocks_to_fetch

    logger.info(
        "Fetching blocks %s to %s (%s blocks)",
        last_height,
        end_height - 1,
        blocks_to_fetch,
    )

    batch_data = []
    for height in range(start_height, end_height):
        try:
            if block_stats := api.get_block_stats(height):
                batch_data.append(block_stats)
            logger.info("Fetched block %d (%d/%d)", height, len(batch_data), blocks_to_fetch)
        except Exception:
            logger.exception("Failed to fetch block %d", height)

    if not batch_data:
        logger.warning("No blocks were successfully fetched.")
        return

    # Save to incremental file
    INCREMENTAL_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    file_path = INCREMENTAL_DIR / f"incremental_block_stats_{date_str}.parquet"

    new_data = pd.DataFrame(batch_data)
    if file_path.exists():
        existing = pd.read_parquet(file_path)
        new_data = pd.concat([existing, new_data], ignore_index=True)
        new_data = new_data.drop_duplicates(subset=["height"], keep="last")

    new_data.to_parquet(file_path)

    elapsed = time.perf_counter() - start_time
    logger.info("Saved %d blocks to %s (%.2fs)", len(batch_data), file_path, elapsed)


def main() -> None:
    """Run the BTC data updater."""
    logger.info("=== BTC Single-Core Updater ===")

    api_keys = [
        key for i in range(1, 11)
        if (key := os.getenv(f"quicknode_endpoint_{i}"))
    ]
    if not api_keys:
        raise ValueError("No QuickNode API keys found (quicknode_endpoint_1..10)")

    logger.info("Loaded %d API key(s)", len(api_keys))

    api = QuickNodeAPI(api_keys, 0)
    update_onchain_data(api, max_blocks=5)

    logger.info("=== Done ===")


if __name__ == "__main__":
    main()
