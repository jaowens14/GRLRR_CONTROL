import traceback
import asyncio
from grlrr import Grlrr

if __name__ == "__main__":

    try:
        grlrr = Grlrr()
        asyncio.run(grlrr.main(), debug=True)

    except Exception as e:
        print(e.__class__.__name__)
        traceback.print_exc()














