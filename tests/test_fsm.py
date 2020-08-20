from enum import Enum

import pytest

import afsm


class States(Enum):
    PASSED = 'passed'
    FAILED = 'failed'


class Transition(afsm.Transition):
    async def pre(self, current_state, context, args):
        arg_value = self.get_arg(args, 'arg_name')

        print(f'arg_name={arg_value} state={current_state} context={context}')

        if arg_value == 'fail!':
            return (True, context + ':failed!')

        return (False, context)


class Machine(afsm.FSM):
    check = Transition({States.PASSED: States.FAILED}, args=['arg_name'])

    def __init__(self, initial_context):
        super().__init__(get_initial_state=lambda: States.PASSED,
                         get_initial_context=lambda: initial_context)


@pytest.mark.asyncio
async def test_afsm():
    initial_context = 'some-context'
    my_machine = Machine(initial_context)
    state, context = await my_machine.check('ok')
    assert state == States.PASSED and context == initial_context
    state, context = await my_machine.check('fail!')
    assert state == States.FAILED and context == f'{initial_context}:failed!'
    state, context = await my_machine.check('ok')
    assert state == States.FAILED and context == f'{initial_context}:failed!'
    with pytest.raises(ValueError):
        state, context = await my_machine.check('fail!')



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
        if 'water' in context and 'beans' in context:
            return (True, context)

        # we can't turn on coffeemaker without water and beans
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


@pytest.mark.asyncio
async def test_coffeemaker():
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
