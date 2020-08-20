# Simple asyncio FSM

## Usage

```python
from enum import Enum
import afsm


class CoffeeMakerStates(Enum):
    EMPTY = 'empty'
    HAS_WATER = 'has_water'
    HAS_BEANS = 'has_beans'
    ON = 'on'
    OFF = 'off'
    READY = 'ready'


class AddWater(afsm.Transition):
    async def post(self, prev_state, next_state, context, args):
        return dict(context, water=True)


class AddBeans(afsm.Transition):
    async def post(self, prev_state, next_state, context, args):
        return dict(context, beans=True)


class Trigger(afsm.Transition):
    async def pre(self, current_state, context, args):
        # we can't turn on coffeemaker without water and beans
        if 'water' in context and 'beans' in context:
            return (True, context)

        if current_state == CoffeeMakerStates.EMPTY:
            return (False, context)

        return (False, context)


class CoffeeMaker(afsm.FSM):
    add_water = AddWater({CoffeeMakerStates.EMPTY: CoffeeMakerStates.HAS_WATER,
                          CoffeeMakerStates.HAS_BEANS: CoffeeMakerStates.READY})

    add_beans = AddBeans({CoffeeMakerStates.EMPTY: CoffeeMakerStates.HAS_BEANS,
                          CoffeeMakerStates.HAS_WATER: CoffeeMakerStates.READY})

    trigger = Trigger({
        CoffeeMakerStates.OFF: CoffeeMakerStates.EMPTY,
        CoffeeMakerStates.READY: CoffeeMakerStates.ON,
        CoffeeMakerStates.ON: CoffeeMakerStates.OFF})

    def __init__(self):
        super().__init__(get_initial_state=lambda: CoffeeMakerStates.EMPTY,
                         get_initial_context=dict)


async def main()
    cm = CoffeeMaker()
    state, _ = await cm.trigger()
    assert state == CoffeeMakerStates.EMPTY
    state, context = await cm.add_beans()
    assert state == CoffeeMakerStates.HAS_BEANS and 'beans' in context
    # try again
    state, context = await cm.trigger()
    assert state == CoffeeMakerStates.HAS_BEANS and 'beans' in context
    state, context = await cm.add_water()
    assert state == CoffeeMakerStates.READY and 'water' in context
    # and again
    state, context = await cm.trigger()
    assert state == CoffeeMakerStates.ON and 'beans' in context and 'water' in context


asyncio.run(main())

```
