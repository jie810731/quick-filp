from operator import attrgetter
import utility
import time
import timeit


attrgetter1 =  [
                {
                    "trait_type": "accessory",
                    "value": "Cowboy Hat",
                    "display_type": "null",
                    "max_value": "null",
                    "trait_count": 142,
                    "order": "null"
                },
                {
                    "trait_type": "type",
                    "value": "Ape",
                    "display_type": "null",
                    "max_value": "null",
                    "trait_count": 24,
                    "order": "null"
                },
                {
                    "trait_type": "accessory",
                    "value": "1 attributes",
                    "display_type": "null",
                    "max_value": "null",
                    "trait_count": 177,
                    "order": "null"
                }
            ]


attrgetter2 =   [
                {
                    "trait_type": "accessory",
                    "value": "Fedora",
                    "display_type": "null",
                    "max_value": "null",
                    "trait_count": 186,
                    "order": "null"
                },
                {
                    "trait_type": "type",
                    "value": "Ape",
                    "display_type": "null",
                    "max_value": "null",
                    "trait_count": 24,
                    "order": "null"
                },
                {
                    "trait_type": "accessory",
                    "value": "1 attributes",
                    "display_type": "null",
                    "max_value": "null",
                    "trait_count": 177,
                    "order": "null"
                }
            ]

start = timeit.default_timer()
utility.getJaccardDistance(attrgetter1,attrgetter2)
# time.sleep(1)
done = timeit.default_timer()

print('Time: ', done - start)  