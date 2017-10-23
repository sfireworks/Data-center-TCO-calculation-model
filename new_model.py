import math
import os
import sys
#import string

#定义数据集
data_size = 100#PB
data_preservation_time = 50#years

#基本参数
power_price = 0.35 # 
human_labor_price = 25000         #one people each year
#migration_price = 60000
migration_price = 600       #$/TB
building_price = 2000    #$/m^2
cap_step = 1024
year_time = 365 * 24 * 3600/360000

#考虑到通货膨胀,添加货币价值相对现有价值的比例,以年为单位考虑变化比例
inflation_rate = [1.0]*(data_preservation_time + 1)
inflation_file = open("us_infation_rate.txt")
readdata = inflation_file.readlines()

for i in range(0,data_preservation_time + 1) :
        inflation_rate[i] = float(readdata[i])

#print (inflation_rate)

inflation_file.close()

def get_inflation_rate(year_no):
        return inflation_rate[year_no]

#定义介质的容量增长上限,达到上限之后不再继续增长
media_uplimit = [12,50,30,100]


#介质参数数组,按照介质type值排序,0:disc,1:hdd,2:ssd,3:tape
#参数顺序为price/capacity/lifecycle/throughput/AFR/price_decrease_rate/Kr_rate/power
media_para = [[10,0.3,50,30,0.0005,0.4,0.01,0],
              [100,4,5,150,0.0485,0.4,0.01,9.45],
              [619,1,5,400,0.0061,0.4,0.01,3.5],
              [42,6.25,10,100,0.015,0.4,0.01,0]]
"""
media_para = [[10,0.3,50,30,0.0005,0.05,0.01,0],
              [100,4,5,150,0.0485,0.05,0.01,9.45],
              [619,1,5,400,0.0061,0.05,0.01,3.5],
              [42,6.25,10,100,0.015,0.05,0.01,0]]
"""

#服务器参数数组,按照服务器type顺序
#参数顺序为media_count/drive_count/drive_price/lifecycle/volume/basic_cost/basic_power
server_para = [[11240,12,100,30,0.25,20000,100],
               [24,24,0,10,0.25,20000,350],
               [24,24,0,10,0.25,20000,300],
               [32,24,6000,15,0.25,15800,200]]

"""
server_para = [[11240,12,100,30,0.25,20000,100],
               [24,24,0,10,0.25,20000,350],
               [24,24,0,10,0.25,20000,300],
               [32,24,6000,15,0.25,15800,200]]
"""

#机柜参数数组，按照机柜type顺序
#机柜参数顺序为server_count/controller_count/controller_cost/switch_count/switch_cost/lifecycle/rack_basic_power/rack空闲状态时间占比
rack_para = [[1,1,20000,1,16100,20,100,200,0.2],
             [8,1,20000,1,16100,20,200,1200,0.5],
             [8,1,20000,1,16100,20,200,1000,0.5],
             [1,1,20000,1,16100,20,150,400,0.3]]

"""
rack_para = [[1,1,20000,1,16100,20,100,200,0.2],
             [8,1,20000,1,16100,20,200,1200,0.5],
             [8,1,20000,1,16100,20,200,1000,0.5],
             [1,1,20000,1,16100,20,150,400,0.3]]
"""

#定义数据中心参数
#数据中心参数,每机柜需要的电力和制冷花费
dc_para = [[30000],
           [100000],
           [80000],
           [60000]]

"""
dc_para = [[30000],
           [100000],
           [80000],
           [60000]]

"""

#定义存储介质
class storage_media:
        #basic media storage info 
        m_type = 1
        m_price = 1
        m_capacity = 1
        m_lifecycle = 1
        m_throughput = 1
        m_AFR = 0.01
        m_price_drate = 0.05
        m_Kr_rate = 0.01
        m_power = 1
        #basic method
        #def __init__(self,storage_type,price,cap,life,throughput,afr,Kr_rate,power):
        def __init__(self,storage_type):
                self.m_type = storage_type
                self.m_price = media_para[storage_type][0]
                self.m_capacity = media_para[storage_type][1]
                self.m_lifecycle = media_para[storage_type][2]
                self.m_throughput = media_para[storage_type][3]
                self.m_AFR = media_para[storage_type][4]
                self.m_price_drate = media_para[storage_type][5]
                self.m_Kr_rate = media_para[storage_type][6]
                self.m_power = media_para[storage_type][7]
        def getmedia_capacity(self,year_NO):
                return self.m_capacity * pow(1 + (self.m_Kr_rate),year_NO)
        def getmedia_price(self,year_NO):
                return self.m_price * pow(1 - (self.m_price_drate),year_NO)

#定义服务器
class storage_server:
        #basic device info
        s_server_type = 0
        s_media_ins = storage_media(s_server_type)
        s_media_count = 1
        s_drive_count = 1
        s_drive_price = 1
        s_lifecycle = 1
        s_volume = 1
        s_basic_cost = 1
        s_basic_power = 1
        s_server_power = 1
        s_server_capacity = 1
        #basic method
        def __init__(self,server_type):
                self.s_server_type = server_type
                self.s_media_ins = storage_media(server_type)
                self.s_media_count = server_para[server_type][0]
                self.s_drive_count = server_para[server_type][1]
                self.s_drive_price = server_para[server_type][2]
                self.s_lifecycle = server_para[server_type][3]
                self.s_volume = server_para[server_type][4]
                self.s_basic_cost = server_para[server_type][5]
                self.s_basic_power = server_para[server_type][6]
                self.s_server_capacity = self.s_media_ins.m_capacity * self.s_media_count
        def getserver_power(self):
                return self.s_media_count * self.s_media_ins.m_power + self.s_basic_power
        def getserver_AFR(self):
                return self.s_media_ins.m_AFR
        def getserver_capacity(self,year_NO):
                return self.s_media_count * self.s_media_ins.getmedia_capacity(year_NO)
        def getserver_throughput(self):
                return self.s_drive_count * self.s_media_ins.m_throughput
        def getserver_cost(self,year_NO):
                if year_NO % self.s_lifecycle == 0 :
                        return self.s_drive_count * self.s_drive_price + self.s_media_count * self.s_media_ins.getmedia_price(year_NO) + self.s_basic_cost
                else :
                        return self.s_drive_count * self.s_drive_price + self.s_media_count * self.s_media_ins.getmedia_price(year_NO)

#定义机柜
class storage_rack:
        #basic rack info
        r_rack_type = 0
        s_server_ins = storage_server(r_rack_type)
        r_server_count = 1
        r_controller_count = 1
        r_controller_cost = 1
        r_switch_count = 1
        r_switch_cost = 1
        r_rack_lifecycle = 1
        r_rack_volume = 1
        r_basic_power = 1
        r_rack_power = 1
        r_rack_idle_powerrate  = 0.1
        r_rack_capacity = 1
        #basic method
        def __init__(self, rack_type):
                self.r_rack_type = rack_type
                self.s_server_ins = storage_server(rack_type)
                self.r_server_count = rack_para[rack_type][0]
                self.r_controller_count = rack_para[rack_type][1]
                self.r_controller_cost  =rack_para[rack_type][2]
                self.r_switch_count = rack_para[rack_type][3]
                self.r_swicth_cost = rack_para[rack_type][4]
                self.r_rack_lifecycle = rack_para[rack_type][5]
                self.r_basic_power = rack_para[rack_type][6]
                self.r_rack_cool_power = rack_para[rack_type][7]
                self.r_rack_idle_powerrate = rack_para[rack_type][8]
                self.r_rack_capacity = self.s_server_ins.s_server_capacity * self.r_server_count
                self.r_rack_volume = self.s_server_ins.s_volume
        def getrack_power(self):
                return self.r_basic_power + self.s_server_ins.s_server_power * self.r_server_count
        def getrack_AFR(self):
                return self.s_server_ins.s_media_ins.m_AFR
        def getrack_throughput(self):
                return self.r_server_count * self.s_server_ins.getserver_throughput()
        def getrack_capacity(self,year_NO):
                return self.r_server_count * self.s_server_ins.getserver_capacity(year_NO)
        def getrack_cost(self,year_NO):
                if year_NO % self.r_rack_lifecycle == 0 :
                        return self.r_server_count * self.s_server_ins.getserver_cost(year_NO) + self.r_controller_cost * self.r_controller_count + self.r_switch_cost * self.r_switch_count
                else :
                        return self.r_server_count * self.s_server_ins.getserver_cost(year_NO)

#定义数据中心
class datacenter:
        #basic datacenter info
        dc_type = 0
        rack_ins = storage_rack(dc_type)
        dc_rack_count = 1
        dc_lifecycle = 1
        dc_square = 1
        dc_rack_per_square = 2.5
        dc_coolingfra_cost_per_rack = 1
        dc_IT_power = 1
        dc_cool_power = 1
        dc_pue = 1.5
        dc_throughput = 1
        dc_stuff_per_rack = 0.00001
        dc_use_rate = 0.5
        #dc basic non-IT cost
        dc_infra_cost = 0
        dc_energy_cost = 0
        dc_maintanance_cost = 0
        #dc IT cost
        dc_IT_cost = 1
        #basic method
        def __init__(self,datacenter_type):
                self.dc_type = datacenter_type
                self.rack_ins = storage_rack(datacenter_type)
                self.dc_rack_count = data_size * cap_step / self.rack_ins.r_rack_capacity
                self.dc_squre = self.dc_rack_count * self.dc_rack_per_square
                self.dc_lifecycle = 25
                self.dc_coolinfra_cost_per_rack = dc_para[datacenter_type][0]
                #self.dc_cool_power = dc_para[datacenter_type][1]
        def getdc_throughput(self):
                return self.rack_ins. getrack_throughput() * self.dc_rack_count
        
        def getdc_infra_cost(self,year_NO):
                if year_NO % self.dc_lifecycle == 0 :
                        return self.dc_square * building_price + self.dc_rack_count * self.dc_coolingfra_cost_per_rack
                else :
                        return 0
        def getdc_energy_cost(self,year_NO) :
                self.dc_rack_count = data_size * cap_step / self.rack_ins.getrack_capacity(year_NO)
                self.dc_IT_power = self.dc_rack_count * self.rack_ins.getrack_power()
                #self.dc_cool_power = self.dc_rack_count * self.rack_ins.r_rack_cool_power
                return (power_price * year_time * self.dc_use_rate * self.dc_IT_power +  power_price * year_time * (1 - self.dc_use_rate) * self.dc_IT_power * self.rack_ins.r_rack_idle_powerrate) * (1 + self.dc_pue)
                #return power_price * self.dc_cool_power * year_time + power_price * year_time * self.dc_use_rate * self.dc_IT_power +  power_price * year_time * (1 - self.dc_use_rate) * self.dc_IT_power * self.rack_ins.r_rack_idle_powerrate#    IT and cooling energy cost

        def getdc_maintan_cost(self,year_NO) :
                self.dc_maintanance_cost = 0
                if year_NO ==0 :
                        return self.dc_maintanance_cost
                self.dc_maintanance_cost += self.dc_rack_count * human_labor_price * self.dc_stuff_per_rack# human labor cost
                #dc_maintanance_cost += self.dc_rack_count * self.rack_ins.getrack_AFR() * self.rack_ins.getrack_cost(year_NO)# media fail every year, replace cost
                self.dc_maintanance_cost += self.rack_ins.getrack_AFR() * data_size * cap_step * migration_price # media fails every year, migrate the data on the failed media to new one,migration cost
                if year_NO % self.rack_ins.s_server_ins.s_media_ins.m_lifecycle == 0 : #  storage media reach their lifecycle , migration of all the data  is needed  
                        self.dc_maintanance_cost += data_size * cap_step * migration_price
                        return self.dc_maintanance_cost
                else :
                        return self.dc_maintanance_cost

        def getdc_IT_cost(self,year_NO) :
                self.dc_IT_cost = 0
                self.dc_rack_count = data_size * cap_step / self.rack_ins.getrack_capacity(year_NO)
                self.dc_IT_cost += self.dc_rack_count * self.rack_ins.getrack_AFR() * self.rack_ins.getrack_cost(year_NO) # media fail every year, replace cost
                if year_NO % self.rack_ins.s_server_ins.s_media_ins.m_lifecycle == 0 :# the media need repurchase
                        self.dc_IT_cost += self.dc_rack_count * self.rack_ins.getrack_cost(year_NO)
                        return self.dc_IT_cost
                else :
                        return self.dc_IT_cost

total_cost_OD = 0
total_cost_hdd = 0
total_cost_ssd = 0
total_cost_tape = 0

total_OD_cost_year = [0]*(data_preservation_time + 1)
total_hdd_cost_year = [0]*(data_preservation_time + 1)
total_ssd_cost_year = [0]*(data_preservation_time + 1)
total_tape_cost_year = [0]*(data_preservation_time + 1)
OD_total_cost = 0
hdd_total_cost = 0
ssd_total_cost = 0
tape_total_cost = 0

OD_energy_cost_year = [0]*(data_preservation_time + 1)
hdd_energy_cost_year = [0]*(data_preservation_time + 1)
ssd_energy_cost_year = [0]*(data_preservation_time + 1)
tape_energy_cost_year = [0]*(data_preservation_time + 1)
OD_total_energy_cost = 0
hdd_total_energy_cost = 0
ssd_total_energy_cost = 0
tape_total_energy_cost = 0

OD_infra_cost_year = [0]*(data_preservation_time + 1)
hdd_infra_cost_year = [0]*(data_preservation_time + 1)
ssd_infra_cost_year = [0]*(data_preservation_time + 1)
tape_infra_cost_year = [0]*(data_preservation_time + 1)
OD_total_infra_cost = 0
hdd_total_infra_cost = 0
ssd_total_infra_cost = 0
tape_total_infra_cost = 0

OD_mt_cost_year = [0]*(data_preservation_time + 1)
hdd_mt_cost_year = [0]*(data_preservation_time + 1)
ssd_mt_cost_year = [0]*(data_preservation_time + 1)
tape_mt_cost_year = [0]*(data_preservation_time + 1)
OD_total_mt_cost = 0
hdd_total_mt_cost = 0
ssd_total_mt_cost = 0
tape_total_mt_cost = 0

OD_IT_cost_year = [0]*(data_preservation_time + 1)
hdd_IT_cost_year = [0]*(data_preservation_time + 1)
ssd_IT_cost_year = [0]*(data_preservation_time + 1)
tape_IT_cost_year = [0]*(data_preservation_time + 1)
OD_total_IT_cost = 0
hdd_total_IT_cost = 0
ssd_total_IT_cost = 0
tape_total_IT_cost = 0

OD_dc = datacenter(0)
hdd_dc = datacenter(1)
ssd_dc = datacenter(2)
tape_dc = datacenter(3)

OD_file = open("od_file.txt","w+")
hdd_file = open("hdd_file.txt","w+")
ssd_file = open("ssd_file.txt","w+")
tape_file = open("tape_file.txt","w+")

OD_file.writelines("year_NO\t infrastruture cost\t energy cost\t maintanence cost\t IT cost \t total cost \n")
hdd_file.writelines("year_NO\t infrastruture cost\t energy cost\t maintanence cost\t IT cost \t total cost \n")
ssd_file.writelines("year_NO\t infrastruture cost\t energy cost\t maintanence cost\t IT cost \t total cost \n")
tape_file.writelines("year_NO\t infrastruture cost\t energy cost\t maintanence cost\t IT cost \t total cost \n")

for i in range(0,data_preservation_time + 1) :
        OD_infra_cost_year[i] = OD_dc.getdc_infra_cost(i) * inflation_rate[i]
        OD_energy_cost_year[i] = OD_dc.getdc_energy_cost(i) * inflation_rate[i]
        OD_mt_cost_year[i] = OD_dc.getdc_maintan_cost(i) * inflation_rate[i]
        OD_IT_cost_year[i] = OD_dc.getdc_IT_cost(i) * inflation_rate[i]
        total_OD_cost_year[i] = OD_infra_cost_year[i] + OD_energy_cost_year[i] +  OD_mt_cost_year[i] + OD_IT_cost_year[i]
        
        OD_total_infra_cost += OD_infra_cost_year[i]
        OD_total_energy_cost += OD_energy_cost_year[i]
        OD_total_mt_cost += OD_mt_cost_year[i]
        OD_total_IT_cost += OD_IT_cost_year[i]
        OD_total_cost += total_OD_cost_year[i]
        OD_file.writelines(str(i) + "\t" + str(OD_infra_cost_year[i]) + "\t" + str( OD_energy_cost_year[i]) + "\t" +str(OD_mt_cost_year[i] ) + "\t" +str( OD_IT_cost_year[i] ) + "\t" +str(total_OD_cost_year[i]) + "\n")

        hdd_infra_cost_year[i] = hdd_dc.getdc_infra_cost(i) * inflation_rate[i]
        hdd_energy_cost_year[i] = hdd_dc.getdc_energy_cost(i) * inflation_rate[i]
        hdd_mt_cost_year[i] = hdd_dc.getdc_maintan_cost(i) * inflation_rate[i]
        hdd_IT_cost_year[i] = hdd_dc.getdc_IT_cost(i) * inflation_rate[i]
        total_hdd_cost_year[i] = hdd_infra_cost_year[i] + hdd_energy_cost_year[i] +  hdd_mt_cost_year[i] + hdd_IT_cost_year[i]

        hdd_total_infra_cost += hdd_infra_cost_year[i]
        hdd_total_energy_cost += hdd_energy_cost_year[i]
        hdd_total_mt_cost += hdd_mt_cost_year[i]
        hdd_total_IT_cost += hdd_IT_cost_year[i]
        hdd_total_cost += total_hdd_cost_year[i]
        hdd_file.writelines( str(i) + "\t" + str(hdd_infra_cost_year[i]) + "\t" + str( hdd_energy_cost_year[i]) + "\t" +str(hdd_mt_cost_year[i] ) + "\t" +str( hdd_IT_cost_year[i] ) + "\t" +str(total_hdd_cost_year[i]) + "\n")

        ssd_infra_cost_year[i] = ssd_dc.getdc_infra_cost(i) * inflation_rate[i]
        ssd_energy_cost_year[i] = ssd_dc.getdc_energy_cost(i) * inflation_rate[i]
        ssd_mt_cost_year[i] = ssd_dc.getdc_maintan_cost(i) * inflation_rate[i]
        ssd_IT_cost_year[i] = ssd_dc.getdc_IT_cost(i) * inflation_rate[i]
        total_ssd_cost_year[i] = ssd_infra_cost_year[i] + ssd_energy_cost_year[i] +  ssd_mt_cost_year[i] + ssd_IT_cost_year[i]

        ssd_total_infra_cost += ssd_infra_cost_year[i]
        ssd_total_energy_cost += ssd_energy_cost_year[i]
        ssd_total_mt_cost += ssd_mt_cost_year[i]
        ssd_total_IT_cost += ssd_IT_cost_year[i]
        ssd_total_cost += total_ssd_cost_year[i]
        ssd_file.writelines(str(i) + "\t" + str(ssd_infra_cost_year[i]) + "\t" + str( ssd_energy_cost_year[i]) + "\t" +str(ssd_mt_cost_year[i] ) + "\t" +str( ssd_IT_cost_year[i] ) + "\t" +str(total_ssd_cost_year[i]) + "\n")

        tape_infra_cost_year[i] = tape_dc.getdc_infra_cost(i) * inflation_rate[i]
        tape_energy_cost_year[i] = tape_dc.getdc_energy_cost(i) * inflation_rate[i]
        tape_mt_cost_year[i] = tape_dc.getdc_maintan_cost(i) * inflation_rate[i]
        tape_IT_cost_year[i] = tape_dc.getdc_IT_cost(i) * inflation_rate[i]
        total_tape_cost_year[i] = tape_infra_cost_year[i] + tape_energy_cost_year[i] +  tape_mt_cost_year[i] + tape_IT_cost_year[i]

        tape_total_infra_cost += tape_infra_cost_year[i]
        tape_total_energy_cost += tape_energy_cost_year[i]
        tape_total_mt_cost += tape_mt_cost_year[i]
        tape_total_IT_cost += tape_IT_cost_year[i]
        tape_total_cost += total_tape_cost_year[i]
        tape_file.writelines( str(i) + "\t" + str(tape_infra_cost_year[i]) + "\t" + str( tape_energy_cost_year[i]) + "\t" +str(tape_mt_cost_year[i] ) + "\t" +str( tape_IT_cost_year[i] ) + "\t" +str(total_tape_cost_year[i]) + "\n")

OD_file.writelines("total\t" + str(OD_total_infra_cost) + "\t" + str(OD_total_energy_cost) + "\t" + str(OD_total_mt_cost) + "\t" + str(OD_total_IT_cost) + "\t" + str(OD_total_cost) + "\n")
hdd_file.writelines("total\t" + str(hdd_total_infra_cost) + "\t" + str(hdd_total_energy_cost) + "\t" + str(hdd_total_mt_cost) + "\t" + str(hdd_total_IT_cost) + "\t" + str(hdd_total_cost) + "\n")
ssd_file.writelines("total\t" + str(ssd_total_infra_cost) + "\t" + str(ssd_total_energy_cost) + "\t" + str(ssd_total_mt_cost) + "\t" + str(ssd_total_IT_cost) + "\t" + str(ssd_total_cost) + "\n")
tape_file.writelines("total\t" + str(tape_total_infra_cost) + "\t" + str(tape_total_energy_cost) + "\t" + str(tape_total_mt_cost) + "\t" + str(tape_total_IT_cost) + "\t" + str(tape_total_cost) + "\n")
        
OD_file.close()
hdd_file.close()
ssd_file.close()
tape_file.close()
