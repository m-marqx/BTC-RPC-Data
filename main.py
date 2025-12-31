"""
BTC Single-Core Updater for GitHub Actions.

This script fetches Bitcoin blockchain data sequentially.
"""

import logging
import os
import time
from datetime import datetime, timezone

import pandas as pd
import numpy as np

from crypto_explorer import QuickNodeAPI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def get_date_suffix() -> str:
    """
    Get current UTC date as suffix for file naming.

    Returns
    -------
    str
        Date string in YYYY-MM-DD format.
    """
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def update_onchain_data(quant_node_api: QuickNodeAPI, max_blocks: int = 5) -> None:
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

    highest_height = quant_node_api.get_blockchain_info()["blocks"]
    logger.info("Current blockchain height: %s", highest_height)

    data = pd.read_parquet("data/onchain/BTC/block_stats_fragments")

    max_height_diff = data["height"].diff().max()
    if max_height_diff > 1:
        raise ValueError("There are missing blocks in the data")

    data["time"] = np.where(data["time"] < 1e10, data["time"] * 1000, data["time"])
    data = data.set_index("time")

    incremental_folder = "data/onchain/BTC/block_stats_fragments/incremental"
    if not os.path.exists(incremental_folder):
        os.makedirs(incremental_folder)
        logger.info("Incremental folder created!")

    date_suffix = get_date_suffix()
    file_path = f"{incremental_folder}/incremental_block_stats_{date_suffix}.parquet"

    last_height = int(data["height"].iloc[-1]) + 1
    logger.info("Last saved height: %s", last_height - 1)

    blocks_to_fetch = min(highest_height - last_height, max_blocks)

    if blocks_to_fetch <= 0:
        logger.info("No new blocks to fetch. Data is up to date.")
        return

    batch_end = last_height + blocks_to_fetch
    logger.info(
        "Fetching blocks %s to %s (%s blocks)",
        last_height,
        batch_end - 1,
        blocks_to_fetch,
    )

    batch_data = []
    for block_height in range(last_height, batch_end):
        try:
            block_stats = quant_node_api.get_block_stats(block_height)
            if block_stats:
                batch_data.append(block_stats)

            progress = block_height - last_height + 1
            logger.info(
                "Progress: %s/%s - Block %s fetched",
                progress,
                blocks_to_fetch,
                block_height,
            )

        except Exception as e:
            logger.error("Failed to fetch block %s: %s", block_height, e)
            continue

    if not batch_data:
        logger.warning("No new blocks were successfully fetched.")
        return

    new_onchain_data = pd.DataFrame(batch_data)

    if os.path.exists(file_path):
        existing_data = pd.read_parquet(file_path)
        combined_data = pd.concat([existing_data, new_onchain_data], ignore_index=True)
        combined_data = combined_data.drop_duplicates(subset=["height"], keep="last")
    else:
        combined_data = new_onchain_data

    combined_data.to_parquet(file_path)

    elapsed_time = time.perf_counter() - start_time
    logger.info("=== Update Complete ===")
    logger.info("Blocks saved: %s", len(batch_data))
    logger.info("Total records in today's file: %s", len(combined_data))
    logger.info("Elapsed time: %.2f seconds", elapsed_time)
    logger.info("File saved: %s", file_path)


def main() -> None:
    """
    Run the BTC data updater.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If no QuickNode API keys are found in environment variables.
    """
    logger.info("=== BTC Single-Core Updater ===")
    logger.info(
        "Run time: %s UTC",
        datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
    )

    api_keys = []
    for x in range(1, 11):
        api_key = os.getenv(f"quicknode_endpoint_{x}")
        if api_key:
            api_keys.append(api_key)

    if not api_keys:
        raise ValueError("No QuickNode API keys found in environment variables")

    logger.info("Loaded %s API key(s)", len(api_keys))

    quant_node_api = QuickNodeAPI(api_keys, 0)

    logger.info("--- Updating On-Chain Data ---")
    update_onchain_data(quant_node_api, max_blocks=5)

    logger.info("=== Update Complete ===")


if __name__ == "__main__":
    main()
