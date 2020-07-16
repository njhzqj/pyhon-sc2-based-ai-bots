"""
Mutile_attack_bot
race:p
target enemy:z

this is a python sc2 robot that have four kind of strategys 
and it can randomly choose one when the game starts
actually, this robot is not smart and most of human players can defeat it very very very easily

author:pan jia xin
start_time:2020/07/03
last_modified_time:2020/07/05 22:40
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

class Mutile_attack_bot(sc2.BotAI):
    def __init__(self):
        self.choice=1#defult:1
        ran_num=random.randint(0, 9)
        if ran_num==0:
            self.choice=0
        if ran_num>=1 and ran_num<=3:
            self.choice=1
        if ran_num>=4 and ran_num<=6:
            self.choice=2
        if ran_num>=7 and ran_num<=9:
            self.choice=3
        #print("game started and robot choose strategys :")#show what strategys we choose
        #print(self.choice)
        self.charge_started=False
        self.blink_started=False
        self.warpgate_started=False
        self.extendthermallance_started=False
        self.GROUND_A1_STARTED=False
        self.GROUND_W1_STARTED=False
        self.GROUND_A2_STARTED=False
        self.GROUND_W2_STARTED=False
        self.GROUND_A3_STARTED=False
        self.GROUND_W3_STARTED=False
        self.SHIELD_1_STARTED=False
        self.SHIELD_2_STARTED=False
        self.SHIELD_3_STARTED=False
        self.AIR_W1_STARTED=False
        self.AIR_A1_STARTED=False
        self.AIR_W2_STARTED=False
        self.AIR_A2_STARTED=False
        self.AIR_W3_STARTED=False
        self.AIR_A3_STARTED=False
        self.FORGE_NUM=2
        self.MAX_ROBOTICSFACILITY=2
        self.MAX_STARGATE=2
        self.MAX_STARGATE_2=4
        self.MAX_OB_NUM=1#max number of ob exists
        self.MAX_VOIDRAY=16#max number of voidray exists
        self.MAX_IMMORTAL_NUM=2#max number of immortal exists
        self.MAX_COLOSSUS_NUM=6#max number of colossus exists

    async def on_step(self, iteration: int):
        #print(self.game_info.map_size)
        #print(self.time)
        #print(random.randint(0, 3))
        if iteration == 0:
            await self.chat_send("gl")
        #if iteration == 60:
        #    await self.chat_send("hf")
        await self.distribute_workers()
        await self.build_pylons()
        await self.nexus_boost()
        #do as its strategys             
        if self.choice == 0:
            #使用两矿八兵营叉子一波
            await self.choice_0_build_workers()
            await self.choice_0_expand()
            await self.choice_01_additional_pylon()
            await self.choice_0_build_gateway()
            await self.choice_0_build_zealots()
            await self.choice_0_zealot_attack()
        elif self.choice == 1:
            #使用提速叉一波
            await self.build_ob()
            await self.scout()
            await self.choice_1_build_workers()
            await self.choice_1_expand()
            await self.choice_01_additional_pylon()
            await self.choice_1_build_gateway()
            await self.choice_1_build_assimilators()
            await self.build_by()
            await self.build_vc()
            await self.upgrade_charge()
            await self.upgrade_wrapgate()
            await self.choice_1_build_zealots()
            await self.choice_1_defend_and_attack()
            if self.time>500:
                await self.build_vr()
            if self.time>600:
                await self.build_forge()
                if self.units(ZEALOT).amount>10:
                    await self.upgrade_gnd_1w_1a()
        elif self.choice == 2:
            #使用光束流
            await self.build_ob()
            await self.scout()
            await self.choice_2_defend_and_attack()
            await self.choice_2_additional_pylon()
            await self.choice_2_build_workers()
            await self.choice_2_expand()
            await self.choice_2_build_gateway()
            await self.choice_2_build_assimilators()
            await self.build_immortal()
            await self.build_colossus()
            await self.build_voidray()
            await self.build_by()
            await self.build_vr()
            await self.build_vs()
            if self.units(ROBOTICSFACILITY).amount>1:
                await self.build_vb()
            await self.build_forge()
            if self.units(VOIDRAY).amount>1:
                await self.upgrade_extendthermallance()
            if self.units(VOIDRAY).amount>2:
                await self.upgrade_gnd_1w_1a()
            await self.choice_2_build_zealots()
            if self.units(STARGATE).amount>1:
                await self.upgrade_air_a1()
                await self.upgrade_air_w1()
                await self.upgrade_shield_level1()
            if self.units(VOIDRAY).amount>=8:
                await self.build_vc()
            if self.units(VOIDRAY).amount>10:
                await self.upgrade_gnd_2w_2a()
                await self.upgrade_shield_level2()
                await self.upgrade_shield_level2()
            if self.time>610.0:
                await self.upgrade_charge()
        elif self.choice == 3:
            #使用闪烁追猎压制
            await self.build_ob()
            await self.scout()
            if self.time>420.0:
                await self.build_vr()
            if self.time>460.0:
                await self.build_forge()
                await self.upgrade_charge()
                if self.units(STALKER).amount>12:
                    await self.upgrade_gnd_1w_1a()
                    await self.upgrade_gnd_2w_2a()
                    await self.upgrade_gnd_3w_3a()
            await self.choice_3_expand()
            await self.choice_3_additional_pylon()
            await self.choice_3_build_workers()
            await self.choice_3_build_gateway()
            await self.choice_3_build_assimilators()
            await self.choice_3_build_zealot_stalker()
            await self.build_by()
            await self.build_vc()
            await self.upgrade_wrapgate()
            await self.upgrade_blink()
            await self.choice_3_defend_and_attack()
            await self.blink()
    
    #****************以下是两矿八兵营叉子一波的相关函数****************
    async def choice_01_additional_pylon(self):
        if self.supply_used>38 and self.already_pending(PYLON)<2 and self.supply_left<10 and self.supply_used<80:
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await  self.build(PYLON, near=nexuses.first.position.towards(self.game_info.map_center, 28))

    async def choice_0_build_workers(self):
        """
        选择空闲基地建造农民
        当只有两矿时，补到32个农民
        当三矿开出去之后，补到48个农民
        当有了四矿之后，补到64个农民
        """
        if self.units(PROBE).amount<32 and self.units(NEXUS).amount<3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<48 and self.units(NEXUS).amount==3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<64 and self.units(NEXUS).amount>3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE)) 

    async def choice_0_expand(self):
        """
        裸双开
        基地数量少于2个且资源足够的情况下就立即扩张
        """
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()
        elif self.units(ZEALOT).amount>25 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def choice_0_build_gateway(self):
        if self.units(NEXUS).amount>1 and self.units(PROBE).amount>28:
            if self.units(GATEWAY).amount<8:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)

    async def choice_0_build_zealots(self):
        for gw in self.units(GATEWAY).ready.noqueue:
            if self.units(ZEALOT).amount<40:
                if self.can_afford(ZEALOT) and self.supply_left>1:
                    await self.do(gw.train(ZEALOT))
    
    async def choice_0_zealot_attack(self):
        if self.units(ZEALOT).amount>26:
            for z in self.units(ZEALOT).idle:
                await self.do(z.attack(self.find_target(self.state)))#如果有超过30个插，那么发起进攻
        if self.units(ZEALOT).amount>3:
            if self.known_enemy_units.amount > 0:
                for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(random.choice(self.known_enemy_units)))#否则在家防御

    #***********************战术：提速叉一波的函数*********************：

    async def choice_1_build_workers(self):
        """
        选择空闲基地建造农民
        当只有两矿时，补到35个农民
        当三矿开出去之后，补到51个农民
        当有了四矿之后，补到67个农民
        """
        if self.units(PROBE).amount<35 and self.units(NEXUS).amount<3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<51 and self.units(NEXUS).amount==3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<67 and self.units(NEXUS).amount>3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE)) 

    async def choice_1_build_assimilators(self):
        """
        bg好之后再开气，仅开一个气
        建造气矿
        """
        if self.units(GATEWAY).amount>0:
            if self.units(ASSIMILATOR).amount<1 and not self.already_pending(ASSIMILATOR):
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

    async def choice_1_expand(self):
        """
        裸双开
        """
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS):
            await self.expand_now()
        elif self.units(ZEALOT).amount>16 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def choice_1_build_gateway(self):
        if self.units(NEXUS).amount>1 and not self.units(GATEWAY):
            if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#先造一个bg，然后造by，等会再补到8bg
        if self.units(NEXUS).amount>1 and self.units(PROBE).amount>30:
            if self.units(GATEWAY).amount<8:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#两矿满采之后，再开始补兵营
        if self.units(NEXUS).amount>=3 and self.units(PROBE).amount>62:
            if self.units(GATEWAY).amount<14:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)#开出四矿之后，再补兵营
    
    async def warp_zealot(self, proxy, num):
        for warpgate in self.units(WARPGATE).ready:
            if self.units(ZEALOT).amount<num:
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

    async def choice_1_build_zealots(self):
        if self.units(WARPGATE).amount>0:
                proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
                await self.warp_zealot(proxy,40)
        else:    
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<2:
                    if self.can_afford(ZEALOT) and self.supply_left>1:
                        await self.do(gw.train(ZEALOT))

    async def choice_1_defend_and_attack(self):
        if self.time<300.0:
            attack_num=18
        else:
            attack_num=30
        if self.supply_army<attack_num and self.units(PYLON).ready.exists:
            proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
            nexuses = self.units(NEXUS).ready
            threats_close_enemy_units = self.known_enemy_units.closer_than(80, nexuses.first)
            if self.units(ZEALOT).amount>0:
                if threats_close_enemy_units:
                    for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(random.choice(threats_close_enemy_units)))
                else:
                    for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(proxy.position))
        else:
            for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(self.find_target(self.state)))


    #**********************战术：光束流的函数****************************：
    async def choice_2_additional_pylon(self):
        if self.supply_used>38 and self.already_pending(PYLON)<2 and self.supply_left<8 and self.supply_used<150:
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await  self.build(PYLON, near=nexuses.first.position.towards(self.game_info.map_center, 35))

    async def choice_2_build_workers(self):
        """
        选择空闲基地建造农民
        当只有两矿时，补到42个农民
        当三矿开出去之后，补到58个农民
        当有了四矿之后，补到72个农民
        """
        if self.units(PROBE).amount<42 and self.units(NEXUS).amount<3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<58 and self.units(NEXUS).amount==3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<72 and self.units(NEXUS).amount>3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE)) 

    async def choice_2_build_gateway(self):
        if self.units(NEXUS).amount>1 and not self.units(GATEWAY):
            if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)
        if self.time>610.0:
            if self.units(NEXUS).amount>2 and self.units(GATEWAY).amount<4:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)

    async def choice_2_build_zealots(self):
        for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<1:
                    if self.can_afford(ZEALOT) and self.supply_left>1:
                        await self.do(gw.train(ZEALOT))
        if self.time>540.0 :
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<7:
                    if self.can_afford(ZEALOT) and self.supply_left>0:
                        await self.do(gw.train(ZEALOT))

    async def choice_2_expand(self):
        """
        裸双开
        """
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()
        elif self.supply_used>110 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def choice_2_build_assimilators(self):
        """
        先气再bg
        因为战术的原因，需要很多的气矿，所以气开的比较多
        """
        if self.units(NEXUS).amount>1:
            if self.units(ASSIMILATOR).amount<4 and not self.already_pending(ASSIMILATOR):
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
            if self.units(ASSIMILATOR).amount < 6 and not self.already_pending(ASSIMILATOR) and self.units(NEXUS).amount==3:
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
            if self.units(ASSIMILATOR).amount < 10 and not self.already_pending(ASSIMILATOR) and self.units(NEXUS).amount>3:
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

    async def choice_2_defend_and_attack(self):
        if self.time<600.0:
            attack_num=68
        else:
            attack_num=94
        if self.supply_army<attack_num and self.units(PYLON).ready.exists:
            proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
            nexuses = self.units(NEXUS).ready
            threats_close_enemy_units = self.known_enemy_units.closer_than(60, nexuses.first)
            if self.units(VOIDRAY).amount>0:
                if threats_close_enemy_units:
                    for v in self.units(VOIDRAY).idle:
                        await self.do(v.attack(random.choice(threats_close_enemy_units)))
                else:
                    for v in self.units(VOIDRAY).idle:
                        await self.do(v.attack(proxy.position))
            if self.units(ZEALOT).amount>0:
                if threats_close_enemy_units:
                    for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(random.choice(threats_close_enemy_units)))
                else:
                    for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(proxy.position))
            if self.units(IMMORTAL).amount>0:
                if threats_close_enemy_units:
                    for i in self.units(IMMORTAL).idle:
                        await self.do(i.attack(random.choice(threats_close_enemy_units)))
                else:
                    for i in self.units(IMMORTAL).idle:
                        await self.do(i.attack(proxy.position))
            if self.units(COLOSSUS).amount>0:
                if threats_close_enemy_units:
                    for c in self.units(COLOSSUS).idle:
                        await self.do(c.attack(random.choice(threats_close_enemy_units)))
                else:
                    for c in self.units(COLOSSUS).idle:
                        await self.do(c.attack(proxy.position))
        else:
            for v in self.units(VOIDRAY).idle:
                        await self.do(v.attack(self.find_target(self.state)))
            for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(self.find_target(self.state)))
            for i in self.units(IMMORTAL).idle:
                        await self.do(i.attack(self.find_target(self.state)))
            for c in self.units(COLOSSUS).idle:
                        await self.do(c.attack(self.find_target(self.state)))



    #*********************战术：闪烁追猎的函数****************************：

    async def choice_3_additional_pylon(self):
        if self.supply_used>38 and self.already_pending(PYLON)<2 and self.supply_left<10 and self.supply_used<160:
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    await  self.build(PYLON, near=nexuses.first.position.towards(self.game_info.map_center, 28))

    async def choice_3_build_workers(self):
        """
        选择空闲基地建造农民
        当只有两矿时，补到35个农民
        当三矿开出去之后，补到54个农民
        当有了四矿之后，补到70个农民
        """
        if self.units(PROBE).amount<35 and self.units(NEXUS).amount<3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<54 and self.units(NEXUS).amount==3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE))
        elif self.units(PROBE).amount<70 and self.units(NEXUS).amount>3:
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE):
                    await self.do(nexus.train(PROBE)) 

    async def choice_3_build_assimilators(self):
        """
        先bg再氣
        """
        if self.units(GATEWAY).amount>0:
            if self.units(ASSIMILATOR).amount<1 and not self.already_pending(ASSIMILATOR):
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
            if self.units(ASSIMILATOR).amount<3 and self.units(TWILIGHTCOUNCIL).amount>0 and not self.already_pending(ASSIMILATOR):
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
            if self.units(ASSIMILATOR).amount<7 and self.units(NEXUS).amount>=4 and not self.already_pending(ASSIMILATOR):
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

    async def warp_stalker(self, proxy, num):
        for warpgate in self.units(WARPGATE).ready:
            if self.units(STALKER).amount<num:
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

    async def choice_3_build_zealot_stalker(self):
        if self.units(WARPGATE).amount>0:
            if self.time<420.0: 
                proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
                await self.warp_stalker(proxy,30)
            else:
                proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
                await self.warp_stalker(proxy,50)
                await self.warp_zealot(proxy,10)
        else:    
            for gw in self.units(GATEWAY).ready.noqueue:
                if self.units(ZEALOT).amount<2:
                    if self.can_afford(ZEALOT) and self.supply_left>0:
                        await self.do(gw.train(ZEALOT))

    async def choice_3_expand(self):
        """
        裸双开
        """
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()
        elif self.supply_used>110 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()

    async def choice_3_build_gateway(self):
        if self.units(NEXUS).amount>1 and self.units(GATEWAY).amount<1:
            if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)
        elif self.units(CYBERNETICSCORE).ready.exists:
            if self.units(NEXUS).amount>=2 and self.units(GATEWAY).amount<7 and self.already_pending(GATEWAY)<2:
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).ready.random
                    if self.can_afford(GATEWAY):
                        await self.build(GATEWAY,near=pylon)

    async def choice_3_defend_and_attack(self):
        if self.time<500.0:
            attack_num=24
        elif self.time<600.0:
            attack_num=36
        else:
            attack_num=50
        if self.supply_army<attack_num and self.units(PYLON).ready.exists:
            proxy = self.units(PYLON).closest_to(self.enemy_start_locations[0])
            nexuses = self.units(NEXUS).ready
            threats_close_enemy_units = self.known_enemy_units.closer_than(80, nexuses.first)
            if self.units(ZEALOT).amount>0:
                if threats_close_enemy_units:
                    for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(random.choice(threats_close_enemy_units)))
                else:
                    for z in self.units(ZEALOT).idle:
                        await self.do(z.attack(proxy.position))
            if self.units(STALKER).amount>0:
                if threats_close_enemy_units:
                    for s in self.units(STALKER).idle:
                        await self.do(s.attack(random.choice(threats_close_enemy_units)))
                else:
                    for s in self.units(STALKER).idle:
                        await self.do(s.attack(proxy.position))
        else:
            for z in self.units(ZEALOT).idle:
                    await self.do(z.attack(self.find_target(self.state)))
            for s in self.units(STALKER).idle:
                    await self.do(s.attack(self.find_target(self.state)))

    #**********************************************************************************
    #***************************以下都是通用函数*****************************************
    #**********************************************************************************
    # check if we have an ability
    async def has_ability(self, ability, unit):
        abilities = await self.get_available_abilities(unit)
        if ability in abilities:
            return True
        else:
            return False

    async def blink(self):
        for stalker in self.units(STALKER):
            has_blink = await self.has_ability(EFFECT_BLINK_STALKER, stalker)
            threatsClose = self.known_enemy_units.filter(lambda x: x.can_attack_ground).closer_than(5, stalker)
            if threatsClose and stalker.shield < 10:
                ex=threatsClose.first.position[0]
                ey=threatsClose.first.position[1]
                sx=stalker.position[0]
                sy=stalker.position[1]
                x=2*sx-ex
                y=2*sy-ey
                blink_to = position.Point2(position.Pointlike((x, y)))
                escape_location = stalker.position.towards(blink_to, 4)
                if has_blink:
                    await self.do(stalker(EFFECT_BLINK_STALKER, escape_location))

    def find_target(self,state):
        emeny_army_units=self.known_enemy_units.filter(lambda x: x.can_attack_ground)
        if self.known_enemy_units.amount>0 and emeny_army_units:
            return random.choice(emeny_army_units).position
        elif self.known_enemy_structures.amount>0:
            return random.choice(self.known_enemy_structures).position
        else:
            return self.enemy_start_locations[0]

    def random_location_variance(self, enemy_start_location):
        x = enemy_start_location[0]
        y = enemy_start_location[1]

        x += ((random.randrange(-40, 40)) / 100) * enemy_start_location[0]
        y += ((random.randrange(-40, 40)) / 100) * enemy_start_location[1]

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.game_info.map_size[0]:
            x = self.game_info.map_size[0]
        if y > self.game_info.map_size[1]:
            y = self.game_info.map_size[1]

        # Have to convert the position to Point2 from pointlike
        go_to = position.Point2(position.Pointlike((x, y)))
        return go_to

    # Use our obesvers to look the enemy
    async def scout(self):
        if len(self.units(OBSERVER)) > 0:
            scout = self.units(OBSERVER)[0]
            if scout.is_idle:
                enemy_location = self.enemy_start_locations[0]
                move_to = self.random_location_variance(enemy_location)
                await self.do(scout.move(move_to))

    #基地加速
    async def nexus_boost(self):
        nexus = self.units(NEXUS).ready.random
        if not nexus.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
            abilities = await self.get_available_abilities(nexus)
            if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                await self.do(nexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, nexus))   
                 
    #****************建造类***********************************************
    """
    包括造水晶、by、vc、vr、vs、vb
    造ob、不朽、巨像、虚空等
    """
    #建造水晶
    async def build_pylons(self):
        """
        人口空余不足 且没有水晶正在建造时，放下水晶。
        """
        if self.supply_used<200:
            if self.supply_left < 18 and not self.already_pending(PYLON) and self.units(ZEALOT).amount>2:
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 12))
            elif self.supply_left < 3 and not self.already_pending(PYLON):
                nexuses = self.units(NEXUS).ready
                if nexuses.exists:
                    if self.can_afford(PYLON):
                        if self.units(PYLON).amount<1:
                            await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 5))
                        else:
                            await self.build(PYLON,near=nexuses.first.position.towards(self.game_info.map_center, 23))
    
    async def build_forge(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.units(FORGE).amount<self.FORGE_NUM and not self.already_pending(FORGE):
            if self.units(PYLON).ready.exists:
                pylon = self.units(PYLON).ready.random
                if self.can_afford(FORGE):
                    await self.build(FORGE,near=pylon)

    #造by
    async def build_by(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            # 建造BY
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)

    #造vc
    async def build_vc(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(CYBERNETICSCORE).ready.exists and not self.units(TWILIGHTCOUNCIL):
                if self.can_afford(TWILIGHTCOUNCIL) and not self.already_pending(TWILIGHTCOUNCIL):
                    await self.build(TWILIGHTCOUNCIL, near=pylon)
    
    #造vr
    async def build_vr(self):
        #Robotics Facility
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(CYBERNETICSCORE).ready.exists and self.units(ROBOTICSFACILITY).amount<self.MAX_ROBOTICSFACILITY:
                if self.can_afford(ROBOTICSFACILITY) and not self.already_pending(ROBOTICSFACILITY):
                    await self.build(ROBOTICSFACILITY, near=pylon)

    #造vb
    async def build_vb(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            if self.units(PYLON).ready.exists:
                pylon = self.units(PYLON).ready.random
                if self.units(ROBOTICSBAY).amount<1:
                    if self.can_afford(ROBOTICSBAY) and not self.already_pending(ROBOTICSBAY):
                        await self.build(ROBOTICSBAY, near=pylon)
    
    #造vs
    async def build_vs(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            if self.units(CYBERNETICSCORE).ready.exists and self.units(STARGATE).amount<self.MAX_STARGATE:
                if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    await self.build(STARGATE, near=pylon)
            if self.units(CYBERNETICSCORE).ready.exists and self.units(STARGATE).amount<self.MAX_STARGATE_2 and self.supply_used>130:
                if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                    await self.build(STARGATE, near=pylon)

    #造ob
    async def build_ob(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            for vr in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.units(OBSERVER).amount<self.MAX_OB_NUM and self.can_afford(OBSERVER) and self.supply_left>0:
                    await self.do(vr.train(OBSERVER))

    #造不朽
    async def build_immortal(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            for vr in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.units(IMMORTAL).amount<self.MAX_IMMORTAL_NUM and self.can_afford(IMMORTAL) and self.supply_left>1:
                    await self.do(vr.train(IMMORTAL))

    #造巨像
    async def build_colossus(self):
        if self.units(ROBOTICSBAY).ready.exists:
            for vr in self.units(ROBOTICSFACILITY).ready.noqueue:
                if self.units(COLOSSUS).amount<self.MAX_COLOSSUS_NUM and self.can_afford(COLOSSUS) and self.supply_left>1:
                    await self.do(vr.train(COLOSSUS))
    
    #造虚空光辉舰
    async def build_voidray(self):
        if self.units(STARGATE).ready.exists:
            for sg in self.units(STARGATE).ready.noqueue:
                if self.can_afford(VOIDRAY) and self.units(VOIDRAY).amount<self.MAX_VOIDRAY and self.supply_left>1:
                    await self.do(sg.train(VOIDRAY))

    #**************研究升级类*****************************
    """
    包括升级冲锋、闪烁、折跃门、攻防等
    """
    #升级冲锋
    async def upgrade_charge(self):
        if self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.can_afford(RESEARCH_CHARGE) and not self.charge_started:
                twc = self.units(TWILIGHTCOUNCIL).ready.first
                await self.do(twc(RESEARCH_CHARGE))
                charge_started = True

    #升级blink闪烁
    async def upgrade_blink(self):
        if self.units(TWILIGHTCOUNCIL).ready.exists:
            if self.can_afford(RESEARCH_BLINK) and not self.blink_started:
                twc = self.units(TWILIGHTCOUNCIL).ready.first
                await self.do(twc(RESEARCH_BLINK))
                blink_started = True

    #升级折跃门
    async def upgrade_wrapgate(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(RESEARCH_WARPGATE) and not self.warpgate_started:
            ccore = self.units(CYBERNETICSCORE).ready.first
            await self.do(ccore(RESEARCH_WARPGATE))
            self.warpgate_started = True

    #升级巨像射程 RESEARCH_EXTENDEDTHERMALLANCE 
    async def upgrade_extendthermallance(self):
        if self.units(ROBOTICSBAY).ready.exists and self.can_afford(RESEARCH_EXTENDEDTHERMALLANCE) and not self.extendthermallance_started:
            vb = self.units(ROBOTICSBAY).ready.first
            await self.do(vb(RESEARCH_EXTENDEDTHERMALLANCE))
            self.extendthermallance_started = True
    
    #升级盾牌
    #FORGERESEARCH_PROTOSSSHIELDSLEVEL1 
    async def upgrade_shield_level1(self):
        if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSSHIELDSLEVEL1) and not self.SHIELD_1_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.SHIELD_1_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSSHIELDSLEVEL1))
                        self.SHIELD_1_STARTED=True

    #FORGERESEARCH_PROTOSSSHIELDSLEVEL2 
    async def upgrade_shield_level2(self):
        if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSSHIELDSLEVEL2) and not self.SHIELD_2_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.SHIELD_2_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSSHIELDSLEVEL2))
                        self.SHIELD_2_STARTED=True

    #FORGERESEARCH_PROTOSSSHIELDSLEVEL3 
    async def upgrade_shield_level3(self):
        if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSSHIELDSLEVEL3) and not self.SHIELD_3_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.SHIELD_3_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSSHIELDSLEVEL3))
                        self.SHIELD_3_STARTED=True

    #升级空军攻防
    #CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1 
    async def upgrade_air_w1(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1) and not self.AIR_W1_STARTED:
                for fo in self.units(CYBERNETICSCORE).ready.noqueue:
                    if not self.AIR_W1_STARTED:
                        await self.do(fo(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL1))
                        self.AIR_W1_STARTED=True

    #CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2 
    async def upgrade_air_w2(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2) and not self.AIR_W2_STARTED:
                for fo in self.units(CYBERNETICSCORE).ready.noqueue:
                    if not self.AIR_W2_STARTED:
                        await self.do(fo(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL2))
                        self.AIR_W2_STARTED=True

    #CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3 
    async def upgrade_air_w3(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3) and not self.AIR_W3_STARTED:
                for fo in self.units(CYBERNETICSCORE).ready.noqueue:
                    if not self.AIR_W3_STARTED:
                        await self.do(fo(CYBERNETICSCORERESEARCH_PROTOSSAIRWEAPONSLEVEL3))
                        self.AIR_W3_STARTED=True

    #CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1 
    async def upgrade_air_a1(self):
        if self.units(STARGATE).ready.exists and self.units(CYBERNETICSCORE).ready.exists and self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1) and not self.AIR_A1_STARTED:
                for fo in self.units(CYBERNETICSCORE).ready.noqueue:
                    if not self.AIR_A1_STARTED:
                        await self.do(fo(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL1))
                        self.AIR_A1_STARTED=True

    #CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2 
    async def upgrade_air_a2(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2) and not self.AIR_A2_STARTED:
                for fo in self.units(CYBERNETICSCORE).ready.noqueue:
                    if not self.AIR_A2_STARTED:
                        await self.do(fo(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL2))
                        self.AIR_A2_STARTED=True

    #CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3
    async def upgrade_air_a3(self):
        if self.units(CYBERNETICSCORE).ready.exists and self.can_afford(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3) and not self.AIR_A3_STARTED:
                for fo in self.units(CYBERNETICSCORE).ready.noqueue:
                    if not self.AIR_A3_STARTED:
                        await self.do(fo(CYBERNETICSCORERESEARCH_PROTOSSAIRARMORLEVEL3))
                        self.AIR_A3_STARTED=True

    #双升升级地面攻防，注：默认需要有已经建成的vc之后才会开始升级攻防，可以修改
    async def upgrade_gnd_1w_1a(self):
    #Ground Weapons Level 1 Ground Armor Level 1
        if self.units(STARGATE).ready.exists:
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1) and not self.GROUND_W1_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_W1_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL1 ))
                        self.GROUND_W1_STARTED=True
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1) and not self.GROUND_A1_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_A1_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL1))
                        self.GROUND_A1_STARTED=True
   
    async def upgrade_gnd_2w_2a(self):
    #Ground Weapons Level 2 Ground Armor Level 2
        if self.units(STARGATE).ready.exists:
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2) and not self.GROUND_W2_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_W2_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL2))
                        self.GROUND_W2_STARTED=True
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2) and not self.GROUND_A2_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_A2_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL2))
                        self.GROUND_A2_STARTED=True
    
    async def upgrade_gnd_3w_3a(self):
    #Ground Weapons Level 3 Ground Armor Level 3
        if self.units(STARGATE).ready.exists:
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3) and not self.GROUND_W3_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_W3_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDWEAPONSLEVEL3))
                        self.GROUND_W3_STARTED=True
            if self.units(FORGE).ready.exists and self.can_afford(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3) and not self.GROUND_A3_STARTED:
                for fo in self.units(FORGE).ready.noqueue:
                    if not self.GROUND_A3_STARTED:
                        await self.do(fo(FORGERESEARCH_PROTOSSGROUNDARMORLEVEL3))
                        self.GROUND_A3_STARTED=True

    #*******************************************************************************
    #*******************************************************************************
    #*******************************************************************************

def main():
    
    run_game(maps.get("KingsCoveLE"), [
        Bot(Race.Protoss, Mutile_attack_bot()),
        Computer(Race.Zerg, Difficulty.Hard)], realtime=False
        ,save_replay_as="test_choice_3.SC2Replay"
        )  
        #set realtime to False can let the game run faster
        #最高电脑难度：CheatInsane
    """
    run_game(maps.get("KingsCoveLE"), [
        Human(Race.Zerg),
        Bot(Race.Protoss, Mutile_attack_bot())],
        realtime=True,save_replay_as="test.SC2Replay")
        
    """
if __name__ == '__main__':
    main()
