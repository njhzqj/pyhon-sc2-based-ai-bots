"""
eiaght_gateway_rush.py 
我的sc2 脚本
种族：p
创建时间：2020/06/24
2020/06/24:现在这个ai可以进行：补农民、采矿、修水晶、开气矿并进行采集的操作；准备下一步实现：爆叉子一波。
2020/06/25T11:10:现在这个ai会打两矿八兵营爆走地叉一波，当人口高于80时，如果有余钱就继续扩张
注：此处的8bg有时会多补或者少补一个
"""
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
    CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY, ZEALOT
import random

class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS_2=32
        self.MAX_WORKERS_3=48
        self.MAX_WORKERS_4=80
        self.MAX_GATEWAY=7
        self.MAX_ASSIMILATOR=2

    async def on_step(self, iteration: int):
        if iteration == 0:
            await self.chat_send("glhf")
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        #await self.build_assimilators()
        await self.quick_expand()
        await self.late_expand()
        await self.build_gateway()
        await self.build_zealots()
        await self.zealot_attack()

    async def build_workers(self):
        """
        选择空闲基地建造农民
        当只有两矿时，补到32个农民
        当三矿开出去之后，补到48个农民
        当有了四矿之后，补到80个农民
        """
        if self.units(PROBE).amount<self.MAX_WORKERS_2 and self.units(NEXUS).amount<3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<self.MAX_WORKERS_3 and self.units(NEXUS).amount==3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<self.MAX_WORKERS_4 and self.units(NEXUS).amount>3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE)) 
          

    async def build_pylons(self):
        """
        人口空余不足8 且没有水晶正在建造时，放下水晶。
        """
        if self.supply_used<194:
            if self.supply_left < 5 and not self.already_pending(PYLON):
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        await  self.build(PYLON, near=nexuses.random)  # near表示建造地点，具体坐标是基地旁随机的一块范围
        #下面的这个快速补房子可能导致直接补到两百人口
        #elif self.supply_left < 5 and self.units(ZEALOT).amount>5 and self.already_pending(PYLON).amount<4:
        #    p = self.game_info.map_center.towards(self.enemy_start_locations[0], 90)
        #    if self.can_afford(PYLON):
        #        await  self.build(PYLON, near=p.random)  #为了防止在爆兵的时候卡人口，在爆兵时取消建造一个水晶时不能同时建造第二个水晶的限制,在兵营旁边补水晶

    async def build_assimilators(self):
        """
        建造气矿
        """
        if self.units(ASSIMILATOR).amount<self.MAX_ASSIMILATOR:
            for nexus in self.units(NEXUS).ready:  # 在建造好的基地附近寻找气矿
                vespenes = self.state.vespene_geyser.closer_than(25.0, nexus)
                for vespene in vespenes:
                    if not self.can_afford(ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vespene.position)
                    if worker is None:
                        break
                    if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                        await self.do(worker.build(ASSIMILATOR, vespene))

    async def quick_expand(self):
        """
        裸双开
        基地数量少于2个且资源足够的情况下就立即扩张
        """
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()

    async def late_expand(self):
        """
        当人口到达一定程度后，开始继续扩张
        """
        if self.units(ZEALOT).amount>28 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def build_gateway(self):
        if self.units(NEXUS).amount>1 and self.units(PROBE).amount>32:
            if self.units(GATEWAY).amount<self.MAX_GATEWAY:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)

    async def build_zealots(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.units(ZEALOT).amount<30:
                if self.can_afford(ZEALOT) and self.supply_left>1:
                    await self.do(gw.train(ZEALOT))

    def find_target(self,state):
        if self.known_enemy_units.amount>0:
            return random.choice(self.known_enemy_units)
        elif self.known_enemy_structures.amount>0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]
    
    async def zealot_attack(self):
        if self.units(ZEALOT).amount>30:
            for z in self.units(ZEALOT).idle:
                await self.do(z.attack(self.find_target(self.state)))#如果有超过30个插，那么发起进攻

        if self.units(ZEALOT).amount>3:
            if self.known_enemy_units.amount > 0:
                for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(random.choice(self.known_enemy_units)))#否则在家防御

def main():
    run_game(maps.get("EphemeronLE"), [
        Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Zerg, Difficulty.Hard)], realtime=False
        ,save_replay_as="eight_gateway_rush.SC2Replay"
        )  # realtime设为False可以加速 


if __name__ == '__main__':
    main()