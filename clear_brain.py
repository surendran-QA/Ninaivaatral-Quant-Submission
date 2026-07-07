import cognee
import asyncio
import os
import console_ui

async def clear_brain():
    console_ui.print_logo()
    console_ui.print_header("CLEARING BRAIN DATA")
    await cognee.prune.prune_data()
    await cognee.prune.prune_system(metadata=True)
    print("Brain cleared successfully!")

if __name__ == "__main__":
    asyncio.run(clear_brain())
