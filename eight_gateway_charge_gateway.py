"""
eight_gateway_charge_gateway.py
我的sc2 脚本
种族：p
创建时间：2020/06/26
2020/06/26T16:52:开始尝试实现两块 8bg 提速叉一波
2020/06/26T20:38:完成 两矿八兵营提速叉一波，然后开三矿并补到12兵营出叉
注：此处的8bg有时会多补或者少补一个
"""
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random

class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS_2=35
        self.MAX_WORKERS_3=51
        self.MAX_WORKERS_4=80
        self.MAX_GATEWAY=7
        self.MAX_GATEWAY_2=11
        self.MAX_ASSIMILATOR=1
        self.charge_started=False
        self.ATTACK_ZEALOT_NUM=10
        self.DEFEND_ZEALOT_NUM=8

    async def on_step(self, iteration: int):
        if iteration == 0:
            await self.chat_send("glhf")
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.build_assimilators()
        await self.quick_expand()
        await self.build_by()
        await self.builc_vc()
        await self.upgrade_charge()
        await self.late_expand()
        await self.build_gateway()
        await self.build_zealots()
        await self.zealot_attack()

    async def build_workers(self):
        """
        选择空闲基地建造农民
        当只有两矿时，补到35个农民
        当三矿开出去之后，补到51个农民
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
        人口空余不足5 且没有水晶正在建造时，放下水晶。
        """
        if self.supply_used<200:
            if self.supply_left < 18 and not self.already_pending(PYLON) and self.units(ZEALOT).amount>3:
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 20))
            elif self.supply_left < 5 and not self.already_pending(PYLON):
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        if self.units(PYLON).amount<1:
                            await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 4))
                        else:
                            await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 15))
                        #await  self.build(PYLON, near=nexuses.random)  # near表示建造地点，具体坐标是基地旁随机的一块范围
        #下面的这个快速补房子可能导致直接补到两百人口
        #elif self.supply_left < 5 and self.units(ZEALOT).amount>5 and self.already_pending(PYLON).amount<4:
        #    p = self.game_info.map_center.towards(self.enemy_start_locations[0], 90)
        #    if self.can_afford(PYLON):
        #        await  self.build(PYLON, near=p.random)  #为了防止在爆兵的时候卡人口，在爆兵时取消建造一个水晶时不能同时建造第二个水晶的限制,在兵营旁边补水晶

    async def wild_pylons(self):
        if self.supply_used<194:
            if self.supply_left < 8 and not self.already_pending(PYLON):
                p = self.game_info.map_center.towards(self.enemy_start_locations[0], 90)
                if p.exists:
                    if self.can_afford(PYLON):
                        await  self.build(PYLON, near=p.random)

    async def build_assimilators(self):
        """
        bg好之后再开气，仅开一个气
        建造气矿
        """
        if self.units(GATEWAY).amount>0:
            if self.units(ASSIMILATOR).amount<self.MAX_ASSIMILATOR and not self.already_pending(ASSIMILATOR):
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
        if self.units(ZEALOT).amount>14 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def build_gateway(self):
        if self.units(NEXUS).amount>1 and not self.units(GATEWAY):
            if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#先造一个bg，然后造by，等会再补到8bg
        if self.units(NEXUS).amount>1 and self.units(PROBE).amount>30:
            if self.units(GATEWAY).amount<self.MAX_GATEWAY:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#两矿满采之后，再开始补兵营
        if self.units(NEXUS).amount>2 and self.units(PROBE).amount>60:
            if self.units(GATEWAY).amount<self.MAX_GATEWAY_2:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#开出四矿之后，再补兵营

    async def build_zealots(self):
        if self.units(GATEWAY).amount<2:
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<2:
                    if self.can_afford(ZEALOT) and self.supply_left>1:
                        await self.do(gw.train(ZEALOT))
        else:
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<60:
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
        if self.units(ZEALOT).amount>self.ATTACK_ZEALOT_NUM:
            for z in self.units(ZEALOT).idle:
                await self.do(z.attack(self.find_target(self.state)))#如果有超过ATTACK_ZEALOT_NUM个插，那么发起进攻

        if self.units(ZEALOT).amount>self.DEFEND_ZEALOT_NUM:
            if self.known_enemy_units.amount > 10:
                for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(random.choice(self.known_enemy_units)))

    async def build_by(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            # 建造BY
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

    async def builc_vc(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(CYBERNETICSCORE).ready.exists and not self.units(TWILIGHTCOUNCIL):
                if self.can_afford(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                    await self.build(TWILIGHTCOUNCIL, near=pylon)
    
    async def upgrade_charge(self):
        if self.units(TWILIGHTCOUNCIL).ready.exists:
                if self.can_afford(RESEARCH_CHARGE) and not self.charge_started:
                    twc = self.units(TWILIGHTCOUNCIL).ready.first
                    await self.do(twc(RESEARCH_CHARGE))
                    charge_started = True#升级冲锋

def main():
    run_game(maps.get("EphemeronLE"), [
        Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Zerg, Difficulty.Harder)], realtime=False
        ,save_replay_as="eight_gateway_rush.SC2Replay"
        )  # realtime设为False可以加速


if __name__ == '__main__':
    main()