#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@date: 16 January 2025 (update)

This source code is provided by Richard J Smith 'as is' and 'with all faults'. The provider makes no 
representations or warranties of any kind concerning the safety, suitability, inaccuracies, 
typographical errors, or other harmful components of this software.
"""

import matplotlib.pyplot as plt
import numpy as np
from pyXSteam.XSteam import XSteam

steamTable = XSteam(XSteam.UNIT_SYSTEM_MKS)

print('Rankine nuclear cycle analysis')

p1 = 56.9 #steam generator outlet pressure (bar)
p2 = 5 #Wet steam pressure at inlet to seperator (bar)
p4 = 0.0728 #Condenser pressure (bar)
t3 = 250 # low pressure turbine inlet temperature (deg C)
p10 = (1+0.05)*p1 #feedwater supply pressure (bar)
eff_HPC = 0.89 #HPC isentropic efficiency
eff_LPC = 0.86 #LPC isentropic efficiency
eff_Pump = 0.8 # pump efficiency

def wspHEXPANSIONPPEFF(p0,p1,eff):
    t0 = steamTable.tsat_p(p0)
    h0 = steamTable.h_tx(t0,1)
    s0 = steamTable.s_ph(p0,h0)
    s1 = s0
    t1 = steamTable.tsat_p(p1)
    x1 = steamTable.x_ps(p1,s1)
    h1 = steamTable.h_tx(t1,x1)
    return h0-(h0-h1)*eff

def wspHEXPANSIONPTPEFF(p0,t0,p1,eff):
    h0 = steamTable.h_pt(p0,t0)
    s0 = steamTable.s_pt(p0,t0)
    s1 = s0
    t1 = steamTable.t_ps(p1,s1)
    # need to determine if single phase or two phase
    x1 = steamTable.x_ps(p1,s1)
    h1 = steamTable.h_tx(t1,x1)
    return h0 - (h0 - h1)*eff
  
def wspHCOMPRESSIONPPEFF(p0,p1,eff):
    h0 = steamTable.h_px(p0,0)
    s0 = steamTable.s_ph(p0,h0)
    s1 = s0
    h1 = steamTable.h_ps(p1,s1)
    return h0+((h1-h0)/eff)
  
def wspHCOMPRESSIONPTPEFF(p0,t0,p1,eff):
    h0 = steamTable.h_pt(p0,t0)
    s0 = steamTable.s_pt(p0,t0)
    s1 = s0
    h1 = steamTable.h_ps(p1,s1)
    return h0+((h1-h0)/eff)

def find_a_sh(quality,hwater1,hwater2,enthalpy1,enthalpy2,enthalpy3):
    for x in range(100):
        y = ((1-quality)*hwater2)+((x/100)*hwater1)+(quality*enthalpy3)
        z = y-((x/100)*enthalpy1)
        if z < enthalpy2:
            for p in range(100):
                y = ((1-quality)*hwater2)+((((x-1)/100)+(p/10000))*hwater1)+(quality*enthalpy3)
                z = y-((((x-1)/100+(p/10000)))*enthalpy1)
                if z < enthalpy2:
                    return ((x-1)/100)+((p-1)/10000)            

def find_h9(sh,hwater1,enthalpy8):
    for x in range(500):
        y=(sh*hwater1)+enthalpy8
        z=(1+sh)*x
        if z > y:
            for p in range(100):
                y=(sh*hwater1)+enthalpy8
                z=(1+sh)*(x-1)+(p/100)
                if z > y:
                    return ((x-1)+((p-1)/100))


#extra for trend
t1a = steamTable.tsat_p(p1)
h1a = steamTable.h_px(p1,0)
s1a = steamTable.s_ph(p1,h1a)

#inlet to HPC
t1 = steamTable.tsat_p(p1)
h1 = steamTable.h_px(p1,1)
s1 = steamTable.s_ph(p1,h1)
print('\nPoint 1 - main steam (HP turbine inlet) conditions')
print(f"P1: {round(float(p1),1)} bar")
print(f"T1: {round(float(t1),1)} degC")
print(f"H1: {round(float(h1),1)} kJ/kg")
print(f"S1: {round(float(s1),3)} kJ/kg K")

#water from superheater
hw1 = steamTable.h_px(p1,0)

#steam inlet to seperator
t2 = steamTable.tsat_p(p2)
hw2 = steamTable.h_px(p2,0)
s2 = s1
h2 = wspHEXPANSIONPPEFF(p1,p2,eff_HPC)
x2 = steamTable.x_ph(p2,h2)
print('\nPoint 2 - HP turbine outlet (seperator inlet) conditions')
print(f"P2: {round(float(p2),1)} bar")
print(f"T2: {round(float(t2),1)} degC")
print(f"H2: {round(float(h2),1)} kJ/kg")
print(f"S2: {round(float(s2),3)} kJ/kg K")

#extra for trend
t2a = t2
p2a = p2
h2a = steamTable.h_tx(t2a,1)
s2a = steamTable.s_ph(p2a,h2a)

#inlet to LPC
p3 = p2
h3 = steamTable.h_pt(p3,t3)
s3 = steamTable.s_ph(p3,h3)
print('\nPoint 3 - LP turbine inlet conditions')
print(f"P3: {round(float(p3),1)} bar")
print(f"T3: {round(float(t3),1)} degC")
print(f"H3: {round(float(h3),1)} kJ/kg")
print(f"S3: {round(float(s3),3)} kJ/kg K")

#outlet of LPC
t4 = steamTable.tsat_p(p4)
h4 = wspHEXPANSIONPTPEFF(p3,t3,p4,eff_LPC)
x4 = steamTable.x_ph(p4,h4)
s4 = steamTable.s_ph(p4,h4)
print('\nPoint 4 - LP turbine exhaust conditions')
print(f"P4: {round(float(p4),4)} bar")
print(f"T4: {round(float(t4),1)} degC")
print(f"H4: {round(float(h4),1)} kJ/kg")
print(f"S4: {round(float(s4),3)} kJ/kg K")

#outlet of condenser
p5 = p4
h5 = steamTable.h_px(p5,0)
t5 = steamTable.tsat_p(p4)
s5 = steamTable.s_ph(p5,h5)
print('\nPoint 5 - Condenser outlet before pump')
print(f"P5: {round(float(p5),4)} bar")
print(f"T5: {round(float(t5),1)} degC")
print(f"H5: {round(float(h5),1)} kJ/kg")
print(f"S5: {round(float(s5),3)} kJ/kg K")

#percentage steam flow to seperator to reheat HP exhaust
a_sh = find_a_sh(x2,hw1,hw2,h1,h2,h3)
print('\nPoint X - percentage main steam flow to seperator')
print(f"a_sh : {round(float(a_sh*100),2)} %")

#putlet of CEP 1
h6 = wspHCOMPRESSIONPPEFF(p5,p2,eff_Pump)
s6 = steamTable.s_ph(p5,h6)

#inlet of CEP 2
h7 = (x2*h5)+((1-x2)*hw2)
t7 = steamTable.t_ph(p2,h7)
s7 = steamTable.s_ph(p5,h7)

#outlet of CEP 2
h8 = wspHCOMPRESSIONPTPEFF(p2,t7,p1,eff_Pump)
t8 = steamTable.t_ph(p1,h8)
s8 = steamTable.s_ph(p1,h8)

#inlet of feedpump
h9 = find_h9(a_sh,hw1,h8)
t9 = steamTable.t_ph(p1,h9)
s9 = steamTable.s_ph(p1,h9)

#outlet of feedpump
h10 = wspHCOMPRESSIONPTPEFF(p1,t9,p10,eff_Pump)
t10 = steamTable.t_ph(p10,h10)
s10 = steamTable.s_ph(p10,h10)
print('\nPoint 10 - Feedpump outlet')
print(f"P10: {round(float(p10),4)} bar")
print(f"T10: {round(float(t10),1)} degC")
print(f"H10: {round(float(h10),1)} kJ/kg")
print(f"S10: {round(float(s10),3)} kJ/kg K")

print('\nSummary')
#pump work
w_pump=((x2/100)*(h6-h5))+(h8-h7)+((1+(a_sh/100))*(h10-h9))

#HPC work
w_HPC = 1*(h1-h2)
print(f"Work generated by HP turbine: {round(float(w_HPC),1)} kJ/kg")

#LPC work
w_LPC = x2*(h3-h4)
print(f"Work generated by LP turbine: {round(float(w_LPC),1)} kJ/kg")

#Specific work of SG
w_SG = (1+(a_sh))*(h1-h7)
print(f"Heat input by Steam Generator: {round(float(w_SG),1)} kJ/kg")

#cycle efficiency
eta_th = (w_HPC+w_LPC-w_pump)/w_SG
print(f"Thermal efficiency is: {round(float(eta_th*100),2)} %")

HRcycle = 3600*100/(eta_th*100)
print(f"HR rankine cycle: {round(float(HRcycle),1)} kJ/kWh")

font = {'family' : 'Times New Roman',
        'size'   : 22}

plt.figure(figsize=(15,10))
plt.title('T-s Diagram - Rankine Nuclear Cycle')
plt.rc('font', **font)

plt.ylabel('Temperature (C)')
plt.xlabel('Entropy (s)')
plt.xlim(-2,10)
plt.ylim(0,600)

T = np.linspace(0, 373.945, 400) # range of temperatures
# saturated vapor and liquid entropy lines
svap = [s for s in [steamTable.sL_t(t) for t in T]]
sliq = [s for s in [steamTable.sV_t(t) for t in T]]

plt.plot(svap, T, 'b-', linewidth=2.0)
plt.plot(sliq, T, 'r-', linewidth=2.0)

plt.plot([s10, s1a, s1, s2, s2a, s3, s4, s5, s10],[t10, t1a, t1, t2, t2a, t3, t4, t5, t10], 'black', linewidth=2.0)


plt.savefig('images/11_rankine_nuclear_cycle-TSdiagram.png')
