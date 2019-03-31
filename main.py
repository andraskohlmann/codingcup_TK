from time import sleep

from communications import Communications
from utils import token
from world import World

with Communications() as c:
    data = c.send_and_receive(token())
    should_quit = False

    world = World()

    while not should_quit:
        sleep(1)
        msg = world.update(data)

        data = c.send_and_receive(msg)

print('exit')