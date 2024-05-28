import os
import easyvvuq as uq
import chaospy as cp

import matplotlib.pyplot as plt
import numpy as np
#from easyvvuq.actions import CreateRunDirectory, Encode, Decode, CleanUp, ExecuteLocal, Actions

work_dir = os.path.dirname(os.path.abspath(__file__))
campaign_work_dir = os.path.join(work_dir, "easyvvuq_coffeeCupCooling")
#
myCampaign = uq.Campaign(name='coffeeCooling')#, work_dir=campaign_work_dir )


T_0 = 273.15 #  0°C = 273.15 K

#Definition of parameters
params = {
    "temp_init": {"type":"float", "min":0.0+T_0, 'max': 100.0+T_0, 'default': 95.0 + T_0 },
    "t_env": {'type': 'float', 'min': -10+T_0, 'max': 20.0+T_0, 'default': 5.0 + T_0},
    "outerRadius":{'type': 'float', 'min': 0, 'max':7.0 / 100, 'default': 2.0/100  },

    "cupThickness":{'type': 'float', 'min': 0, 'max':5.0 / 100, 'default':1.0 / 1000 },

    "cupHeight":{'type': 'float', 'min': 10/100, 'max':20.0/100, 'default': 14/100 },

    "lidThickness":{'type': 'float', 'min': 0, 'max':5.0/1000, 'default':0.5/1000 },

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
    "outerRadius": cp.Normal(7.0/100 /2, 0.5/100),

    #    "d_cup":{'type': 'float', 'min': 0, 'max':5.0, 'default':1.0 / 1000},

    "cupHeight": cp.Normal(14.0/100, 0.5/100),

    #    "d_lid":{'type': 'float', 'min': 0, 'max':5.0, 'default':0.5/1000},

    't_env': cp.Normal(5.0 + T_0, 3.0)  #cp.Uniform(0+T_0, 10+T_0)
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
#stats = results['statistical_moments']['te'];
#percentiles = results['percentiles']['te']
#sobolIndices=results['sobols_first']['te']

temps = results.describe("te", "mean")
std = results.describe('te', 'std')
percentile90 = results.describe('te', '90%')
percentile10 = results.describe('te', '10%')

# Time axis for plots
# Should correspond to the simulated axis!
t = np.linspace(0, 2500, 500)


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
ax.plot(t, sobolIndices1['outerRadius'], color='g', label='outer radius')
ax.plot(t, sobolIndices1['cupHeight'], color='r', label='cup height')
ax.plot(t, sobolIndices1['t_env'], color='b', label='outer temperature')

ax.set_xlabel("Time [s]")
ax.set_ylabel("Sobol index")
ax.legend()
ax.grid()
plt.tight_layout()
fig.savefig("SobolIndices_NormalDist.png")
plt.close()


fig = plt.figure(figsize=(9,9))

ax = fig.gca()
ax.plot(t, sobolIndices2['outerRadius']['cupHeight'], color='g', label='outer radius w. height')
ax.plot(t, sobolIndices2['outerRadius']['t_env'], color='r', label='outer radius w. temperature')
#ax.plot(t, sobolIndices2['t_env'], color='b', label='outer temperature')

ax.set_xlabel("Time [s]")
ax.set_ylabel("Sobol index 2")
ax.legend()
ax.grid()
plt.tight_layout()
fig.savefig("SobolIndices2.png")
plt.close()

