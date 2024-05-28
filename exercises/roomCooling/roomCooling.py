import os
import easyvvuq as uq
import chaospy as cp

import matplotlib.pyplot as plt
import numpy as np
#from easyvvuq.actions import CreateRunDirectory, Encode, Decode, CleanUp, ExecuteLocal, Actions

work_dir = os.path.dirname(os.path.abspath(__file__))
campaign_work_dir = os.path.join(work_dir, "easyvvuq_roomCooling")
#
myCampaign = uq.Campaign(name='roomCooling')


T_0 = 273.15 # K = 0 °C, offset for abs. temp

#Definition of parameters
params = {
    "temp_init": {"type":"float", "min":-10.0+T_0, 'max': 50.0+T_0, 'default': 20.0 + T_0 },
    "t_env": {'type': 'float', 'min': -10+T_0, 'max': 50.0+T_0, 'default': 10.0 + T_0},
    "roomWidth":{'type': 'float', 'min':, 'max':, 'default':  },
    "roomHeight":{'type': 'float', 'min': , 'max':, 'default': },
    "roomLength":{'type': 'float', 'min':, 'max': , 'default': },
    "shortWallWidth":{'type': 'float', 'min': , 'max': , 'default': },
    "wallThickness":{'type': 'float', 'min': , 'max': , 'default': },
    #door parameters
    "doorWidth":{'type': 'float', 'min': , 'max': , 'default':},
    "doorHeight":{'type': 'float', 'min':, 'max': , 'default': },
    "doorThickness":{'type': 'float', 'min': , 'max': , 'default':},
    #window parameters
    "windowWidth":{'type': 'float', 'min': , 'max': , 'default':},
    "windowHeight":{'type': 'float', 'min': , 'max': , 'default': },
    "airGapThickness":{'type': 'float', 'min': 0.5/100 , 'max': 2.0/100, 'default': 1.0/100 },
    "glassThickness":{'type': 'float', 'min': 1/1000 , 'max': 10/1000 , 'default': 5.0/1000 },
    "Qheater":{'type': 'float', 'min': 0.0, 'max': 500, 'default': 0.0 },
    "out_file": { 'type':'string','default':'output.csv' }
}


print("Creating encoders and collator")
# en/decoder and collator

encoder = uq.encoders.GenericEncoder(
                template_fname='cooling/cooling.template',
                delimiter='$',
                target_filename='cooling_in.json');

decoder = uq.decoders.SimpleCSV(target_filename='output.csv',
                output_columns=["te"])
#                header=0);

executor = uq.actions.ExecuteLocal('python3 {}/cooling/cooling_model.py cooling_in.json'.format(work_dir))

actions = uq.actions.Actions(
                uq.actions.CreateRunDirectory('/tmp'),
                uq.actions.Encode(encoder),
                executor, 
                uq.actions.Decode(decoder))

#collater = uq.collate.AggregateSamples(average=False);

myCampaign.add_app(name='cooling',#the name does not have to correspond to the executable name
                params=params,
                actions=actions);

# Sampler

vary = {
    "airGapThickness": cp.Uniform(0.8/100, 1.5/100),
    "glassThickness": cp.Uniform(3/1000, 5/1000),
    't_env': cp.Normal(10.0 + T_0, 3.0)
}

mySampler = uq.sampling.PCESampler(vary=vary, polynomial_order=3)

myCampaign.set_sampler(mySampler)

print("Running")
# Draw samples
myCampaign.draw_samples()

results =  myCampaign.execute().collate()



print("Analysis step")
# Post-processing analysis
analysis = uq.analysis.PCEAnalysis(sampler=mySampler, qoi_cols=['te'])
myCampaign.apply_analysis(analysis);

# Statistics

results = myCampaign.get_last_analysis()

temps = results.describe("te", "mean")
std = results.describe('te', 'std')
percentile90 = results.describe('te', '90%')
percentile10 = results.describe('te', '10%')

# 24h in seconds, using 750 sample points
t = np.linspace(0, 3600*24, 750)


fig = plt.figure(figsize=(9,9))

ax = fig.gca()

ax.plot(t, temps - T_0, color='k', label='mean Temp')

ax.fill_between(t, temps-std - T_0, temps+std - T_0, color='b', alpha=0.5, label='1-std')

ax.fill_between(t, percentile10 - T_0, percentile90 - T_0, color='r', alpha=0.1, label='10-90%')

ax.set_xlabel("Time [s]")
ax.set_ylabel("Temperature [°C]")
ax.legend()
ax.grid()
plt.tight_layout()
fig.savefig("Temp_NormalDist.png")
#plt.show()
plt.close()
# plot sobol indices


sobolIndices1 = results.sobols_first('te')
sobolIndices2 = results.sobols_second('te')

fig = plt.figure(figsize=(9,9))

ax = fig.gca()
#ax.plot(t, sobolIndices1['roomHeight'], color='g', label='width')
#ax.plot(t, sobolIndices1['wallThickness'], color='r', label='height')
ax.plot(t, sobolIndices1['t_env'], color='b', label='outer temperature')
ax.plot(t, sobolIndices1['airGapThickness'], color='m', label='gap thickness')

ax.set_xlabel("Time [s]")
ax.set_ylabel("Sobol index")
ax.legend()
ax.grid()
plt.tight_layout()
fig.savefig("SobolIndices_NormalDist.png")
plt.close()


