from asyncio.queues import Queue
import itertools


class _StateSwitcher:
    """ Glue between Transition object and FSM object. """

    def __init__(self, machine, transition):
        self._machine = machine
        self._transition = transition

        # add states from transition
        self._machine.add_states(self._transition.known_states)

    async def __call__(self, *args):
        current_state, context = await self._machine.query()
        next_state, new_context = await self._transition.call(current_state, context, args)
        await self._machine.update(next_state, new_context)

        return next_state, new_context


class Transition:
    def __init__(self, transitions_map, args=None):
        self._transitions_map = transitions_map
        self._args = args

    @property
    def known_states(self):
        return list(itertools.chain.from_iterable(self._transitions_map.items()))

    def get_arg(self, args, arg_name):
        if self._args is None:
            raise ValueError('no args specified')

        for a_name, a_val in zip(self._args, args):
            if a_name == arg_name:
                return a_val

        raise ValueError('invalid argument')

    def __get__(self, obj, objtype):
        return _StateSwitcher(obj, self)

    async def pre(self, current_state, context, args):
        """ Check pre-conditions and/or pre-process `context`.
        When result is (`True`, _) transition should be performed.
        """
        return (True, context)

    async def post(self, prev_state, next_state, context, args):
        """ Post-process transition. For `context` post-processing purposes. """
        return context

    async def call(self, current_state, context, args):
        """ Perform transition. """
        should_advance, new_ctx = await self.pre(current_state, context, args)
        if not should_advance:
            return (current_state, new_ctx)

        next_state = self._transitions_map.get(current_state)
        if next_state is None:
            raise ValueError(f'there is no transition from: {current_state}')

        new_ctx = await self.post(current_state, next_state, new_ctx, args)

        return (next_state, new_ctx)


class FSM:
    def __init__(self,
                 get_initial_state=lambda: None,
                 get_initial_context=lambda: None):
        initial_ = (get_initial_state(), get_initial_context())

        self._inbox = Queue(1)
        self._inbox.put_nowait(initial_)

        self._states = set()

    def add_states(self, states):
        self._states.update(set(states))

    async def query(self):
        return await self._inbox.get()

    async def update(self, state, context):
        if state not in self._states:
            raise ValueError(f'invalid state: {state}')

        await self._inbox.put((state, context))
