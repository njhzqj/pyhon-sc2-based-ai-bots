"""
test.py 
我的sc2 脚本
种族：p
创建时间：2020/06/24
"""
import sc2
from sc2 import run_game, maps, Race, Difficulty, position, Result
from sc2.player import Bot, Computer, Human
from sc2.constants import *
import random
import numpy as np
import time
import multiprocessing
import os

class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.MAX_WORKERS_2=38
        self.MAX_WORKERS_3=55
        self.MAX_WORKERS_4=82
        self.MAX_GATEWAY=3
        self.MAX_GATEWAY_2=9
        self.MAX_ASSIMILATOR=2
        self.MAX_ASSIMILATOR_2=3
        self.charge_started=False
        self.warpgate_started=False
        self.GROUND_A1_STARTED=False
        self.GROUND_W1_STARTED=False
        self.GROUND_A2_STARTED=False
        self.GROUND_W2_STARTED=False
        self.GROUND_A3_STARTED=False
        self.GROUND_W3_STARTED=False
        self.ATTACK_ZEALOT_NUM=8
        self.DEFEND_ZEALOT_NUM=1
        self.ATTACK_STALKER_NUM=5
        self.ATTACK_IMMORTAL_NUM=1
        self.DEFEND_STALKER_NUM=0
        self.MAX_OB_NUM=2
        self.MAX_IMMORTAL_NUM=8
        self.MAX_ZEALOT_NUM=16
        self.MAX_STALKER_NUM=16
        self.MAX_ROBOTICSFACILITY=1
        self.FORGE_NUM=2

    async def on_step(self, iteration: int):
        if iteration == 0:
            await self.chat_send("glgl")
        await self.nexus_boost()
        await self.distribute_workers()
        await self.build_workers()
        await self.build_pylons()
        await self.wild_pylons()
        await self.build_assimilators()
        await self.quick_expand()
        await self.late_expand()
        await self.build_by()
        await self.builc_vc()
        await self.build_vr()
        await self.build_forge()
        await self.upgrade_charge()
        await self.upgrade_wrapgate()
        await self.upgrade_gnd_1w_1a()
        await self.upgrade_gnd_2w_2a()
        await self.upgrade_gnd_3w_3a()
        await self.build_immortal()
        await self.build_zealots()
        await self.build_stalker()
        await self.build_ob()
        await self.build_gateway()
        #await self.zealot_attack()
        #await self.zealot_stalker_attack()
        await self.attack()

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
        人口空余不足 且没有水晶正在建造时，放下水晶。
        """
        if self.supply_used<200:
            if self.supply_left < 18 and not self.already_pending(PYLON) and self.units(ZEALOT).amount>2:
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 15))
            elif self.supply_left < 3 and not self.already_pending(PYLON):
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        if self.units(PYLON).amount<1:
                            await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 5))
                        else:
                            await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 21))
                        #await  self.build(PYLON, near=nexuses.random)  # near表示建造地点，具体坐标是基地旁随机的一块范围
        #下面的这个快速补房子可能导致直接补到两百人口
        #elif self.supply_left < 5 and self.units(ZEALOT).amount>5 and self.already_pending(PYLON).amount<4:
        #    p = self.game_info.map_center.towards(self.enemy_start_locations[0], 90)
        #    if self.can_afford(PYLON):
        #        await  self.build(PYLON, near=p.random)  #为了防止在爆兵的时候卡人口，在爆兵时取消建造一个水晶时不能同时建造第二个水晶的限制,在兵营旁边补水晶

    async def wild_pylons(self):
        if self.supply_left < 4 and self.supply_used>120 and self.already_pending(PYLON)<2:
            p = self.game_info.map_center.towards(self.enemy_start_locations[0], 0)
            if self.can_afford(PYLON):
                await  self.build(PYLON, near=p)

    async def build_forge(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.units(FORGE).amount<self.FORGE_NUM and not self.already_pending(FORGE):
            if self.units(PYLON).ready.exists:
                pylon = self.units(PYLON).ready.random
                if self.can_afford(FORGE):
                    await self.build(FORGE,near=pylon)


    async def build_assimilators(self):
        """
        先气再bg
        建造气矿
        """
        if self.units(NEXUS).amount>1:
            if self.units(ASSIMILATOR).amount<self.MAX_ASSIMILATOR and not self.already_pending(ASSIMILATOR):
                for nexus in self.units(NEXUS).ready:  # 在建造好的基地附近寻找气矿
                    vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
                    for vespene in vespenes:
                        if not self.can_afford(ASSIMILATOR):
                            break
                        worker = self.select_build_worker(vespene.position)
                        if worker is None:
                            break
                        if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                            await self.do(worker.build(ASSIMILATOR, vespene))
            elif self.units(ASSIMILATOR).amount<self.MAX_ASSIMILATOR_2 and not self.already_pending(ASSIMILATOR) and self.units(NEXUS).amount>2:
                for nexus in self.units(NEXUS).ready:  # 在建造好的基地附近寻找气矿
                    vespenes = self.state.vespene_geyser.closer_than(15.0, nexus)
                    for vespene in vespenes:
                        if not self.can_afford(ASSIMILATOR):
                            break
                        worker = self.select_build_worker(vespene.position)
                        if worker is None:
                            break
                        if not self.units(ASSIMILATOR).closer_than(1.0, vespene).exists:
                            await self.do(worker.build(ASSIMILATOR, vespene))

    async def nexus_boost(self):
        nexus = self.units(NEXUS).ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            abilities = await self.get_available_abilities(nexus)
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                if self.units(GATEWAY).ready.exists and self.units(FORGE).amount<2:
                    gw=self.units(GATEWAY).ready.random
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, gw))
                elif self.units(FORGE).amount>1:
                    bf=self.units(FORGE).ready.random
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, bf))
                elif self.units(NEXUS).amount>6:
                    gw=self.units(GATEWAY).ready.random
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, gw))
                else:
                    await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))                

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
        部队前压的同时开三矿
        """
        if self.supply_used>50 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def build_gateway(self):
        if self.units(NEXUS).amount>1 and self.units(GATEWAY).amount<1:
            if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#先造一个bg，然后造by，等会再补到8bg
        if self.units(NEXUS).amount>1 and self.units(PROBE).amount>36:
            if self.units(GATEWAY).amount<self.MAX_GATEWAY:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#两矿满采之后，再开始补兵营
        if self.units(NEXUS).amount>3 and self.units(PROBE).amount>70:
            if self.units(GATEWAY).amount<self.MAX_GATEWAY_2 and not self.already_pending(GATEWAY):
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#开出四矿之后，再补兵营

    async def warp_stalker(self, proxy):
        for warpgate in self.units(WARPGATE).ready:
            if self.units(STALKER).amount<self.MAX_STALKER_NUM:
                abilities = await self.get_available_abilities(warpgate)
                # STALKER
                if AbilityId.WARPGATETRAIN_STALKER in abilities:
                    pos = proxy.position.to2.random_on_distance(2)
                    placement = await self.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                    if placement is None:
                        #return ActionResult.CantFindPlacementLocation
                        print("can't place STALKER")
                        return
                    await self.do(warpgate.warp_in(STALKER, placement))

    async def warp_zealot(self, proxy):
        for warpgate in self.units(WARPGATE).ready:
            if self.units(ZEALOT).amount<self.MAX_ZEALOT_NUM:
                abilities = await self.get_available_abilities(warpgate)
                # all the units have the same cooldown anyway so let's just look at ZEALOT
                if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                    pos = proxy.position.to2.random_on_distance(4)
                    placement = await self.find_placement(AbilityId.WARPGATETRAIN_ZEALOT, pos, placement_step=1)
                    if placement is None:
                        #return ActionResult.CantFindPlacementLocation
                        print("can't place ZEALOT")
                        return
                    await self.do(warpgate.warp_in(ZEALOT, placement))

    async def build_zealots(self):
        if self.units(GATEWAY).amount<2:
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<3:
                    if self.can_afford(ZEALOT) and self.supply_left>1:
                        await self.do(gw.train(ZEALOT))#只有一个兵营的时候，造两个叉
        else:
            if self.units(WARPGATE).amount>0:
                proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
                await self.warp_zealot(proxy)
            else:    
                for gw in self.units(GATEWAY).ready.noqueue:
                    if self.units(ZEALOT).amount<self.MAX_ZEALOT_NUM:
                        if self.can_afford(ZEALOT) and self.supply_left>1:
                           await self.do(gw.train(ZEALOT))#兵营补好之后，一直补叉

    async def build_stalker(self):
        if self.units(WARPGATE).amount>0:
            proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
            await self.warp_stalker(proxy)
        elif self.units(CYBERNETICSCORE).ready.exists:
            for gw in self.units(GATEWAY).ready.noqueue:
                    if self.units(STALKER).amount<self.MAX_STALKER_NUM:
                        if self.can_afford(STALKER) and self.supply_left>1:
                           await self.do(gw.train(STALKER))

    async def build_ob(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            for vr in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.units(OBSERVER).amount<self.MAX_OB_NUM and self.can_afford(OBSERVER) and self.supply_left>0:
                    await self.do(vr.train(OBSERVER))

    async def build_immortal(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            for vr in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.units(IMMORTAL).amount<self.MAX_IMMORTAL_NUM and self.can_afford(IMMORTAL) and self.supply_left>1:
                    await self.do(vr.train(IMMORTAL))

    def find_target(self,state):
        if self.known_enemy_units.amount>0:
            return random.choice(self.known_enemy_units)
        elif self.known_enemy_structures.amount>0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_locations[0]

    async def attack(self):
        #有足够部队之后，进攻敌人基地
        if self.supply_used>170:
            if self.units(OBSERVER).amount>0:
                ob=self.units(OBSERVER).first
                await(self.do(ob.move(self.enemy_start_locations[0])))
            for z in self.units(ZEALOT).idle:
                await self.do(z.attack(self.find_target(self.state)))
            for s in self.units(STALKER).idle:
                await self.do(s.attack(self.find_target(self.state)))
            for i in self.units(IMMORTAL).idle:
                await self.do(i.attack(self.find_target(self.state)))

        elif self.units(ZEALOT).amount>self.DEFEND_ZEALOT_NUM and self.units(STALKER).amount>self.DEFEND_STALKER_NUM:
            if self.known_enemy_units.amount > 0:
                for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(random.choice(self.known_enemy_units)))
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))
                if self.units(IMMORTAL).amount>0:
                    for i in self.units(IMMORTAL).idle:
                        await self.do(i.attack(random.choice(self.known_enemy_units)))

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
    
    async def build_vr(self):
        #Robotics Facility
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(CYBERNETICSCORE).ready.exists and self.units(ROBOTICSFACILITY).amount<self.MAX_ROBOTICSFACILITY:
                if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    await self.build(ROBOTICSFACILITY, near=pylon)

    async def upgrade_charge(self):
        if self.units(TWILIGHTCOUNCIL).ready.exists:
                if self.can_afford(RESEARCH_CHARGE) and not self.charge_started:
                    twc = self.units(TWILIGHTCOUNCIL).ready.first
                    await self.do(twc(RESEARCH_CHARGE))
                    charge_started = True

    async def upgrade_wrapgate(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(RESEARCH_WARPGATE) and not self.warpgate_started:
            ccore = self.units(CYBERNETICSCORE).ready.first
            await self.do(ccore(RESEARCH_WARPGATE))
            self.warpgate_started = True

    async def upgrade_gnd_1w_1a(self):
    #Ground Weapons Level 1 Ground Armor Level 1
        if self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1) and not self.GROUND_W1_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_W1_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1 ))
                        self.GROUND_W1_STARTED=True
            elif self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1) and not self.GROUND_A1_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_A1_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                        self.GROUND_A1_STARTED=True
   
    async def upgrade_gnd_2w_2a(self):
    #Ground Weapons Level 2 Ground Armor Level 2
        if self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2) and not self.GROUND_W2_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_W2_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2))
                        self.GROUND_W2_STARTED=True
            elif self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2) and not self.GROUND_A2_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_A2_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2))
                        self.GROUND_A2_STARTED=True
    
    async def upgrade_gnd_3w_3a(self):
    #Ground Weapons Level 3 Ground Armor Level 3
        if self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3) and not self.GROUND_W3_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_W3_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3))
                        self.GROUND_W3_STARTED=True
            elif self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3) and not self.GROUND_A3_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_A3_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3))
                        self.GROUND_A3_STARTED=True

def main():
    run_game(maps.get("TritonLE"), [
        Bot(Race.Protoss, SentdeBot()),
        Computer(Race.Zerg, Difficulty.Harder)], realtime=False
        ,save_replay_as="biebiele.SC2Replay"
        )  # realtime设为False可以加速


if __name__ == '__main__':
    main()
