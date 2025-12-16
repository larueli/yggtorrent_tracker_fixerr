import asyncio
import json
import logging

import httpx

logger = logging.getLogger("yggtorrent_tracker_fixerr")


async def wait_until_external_api_is_up(external_url: str, timeout: float = 60.0):
    async with httpx.AsyncClient() as client:
        deadline = asyncio.get_running_loop().time() + timeout
        while True:
            try:
                resp = await client.get(external_url, timeout=2)
                if resp.status_code < 500:
                    return
            except Exception:
                logger.debug("API still not up")
            if asyncio.get_running_loop().time() >= deadline:
                raise RuntimeError("API did not become ready in time")
            await asyncio.sleep(1)


async def run_job_periodically(interval_seconds, job_func, *args, **kwargs):
    while True:
        try:
            await asyncio.to_thread(job_func, *args, **kwargs)
            await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info(f"Job {job_func.__name__} cancelled")
            break
        except Exception as e:
            logger.error(f"Error in {job_func.__name__}: {e}")
            raise e
            # await asyncio.sleep(interval_seconds)


def dicts_equals(dict1, dict2):
    """
    Compare dictionaries using JSON serialization
    Works with any serializable data types
    """
    try:
        return json.dumps(dict1, sort_keys=True) == json.dumps(dict2, sort_keys=True)
    except (TypeError, ValueError):
        return False
