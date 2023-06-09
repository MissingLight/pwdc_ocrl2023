"""
"""

import pickle
import numpy as np
import context
import pwdc
import misc

folder = "data/test_small_1/"

def getConfig():
 
  np.random.seed(0)
  map_grid = np.random.rand(16,16)
  obst_thres = 0.75
  map_grid[map_grid < obst_thres] = 0
  map_grid[map_grid >= obst_thres] = 1

  configs = dict()
  configs["folder"] = folder
  configs["map_grid"] = map_grid
  configs["n"] = 5
  configs["m"] = 2
  configs["Sinit"] = np.array([0.5, 0.05, 0, 0, 0])
  configs["Sgoal"] = np.array([0.1, 0.8, 0 ,0, 0])
  configs["interval_value"] = 0.1
  configs["npix"] = 100
  configs["emoa_path"] = "../public_emoa/build/run_emoa"
  configs["iters_per_episode"] = 100
  configs["optm_weights"] = [0.01, 5000, 200]
    # w1 = 0.01 # control cost, for the u terms.
    # w2 = 5000 # obstacle cost, larger = stay more far away from obstacles
    # w3 = 200 # stay close to the initial guess, larger = stay closer to the initial guess.
  configs["total_epi"] = 10
  configs["hausdorf_filter_thres"] = 10
  configs["obst_cov_val"] = 6*1e-4
  return configs

def test_pwdc():
  """
  """
  configs = getConfig()
  solver = pwdc.PWDC(configs)
  solver.Solve()
  print("PWDC get", len(solver.sol), " solutions.")
  misc.SavePickle(solver, folder+"result.pickle")
  return

def test_pwdc_plot():
  """
  """
  solver = misc.LoadPickle(folder+"result.pickle")
  # solver = loaded[1]
  configs = solver.cfg
  fig_sz,_ = solver.map_grid.shape
  fig_sz = fig_sz/6
  res = solver.sol
  print(" get ", len(solver.emoa_res_dict), " Pareto paths" )
  for k in res:
    px,py = solver._path2xy(res[k].init_path)
    pwdc.plotTraj(solver.obs_pf, configs, \
                  np.array([px,py]), np.array([res[k].getPosX(),res[k].getPosY()]), \
                  folder+"solTraj_"+str(k)+".png", fig_sz)
    print("k = ", k, "converge episode = ", res[k].epiIdxCvg, " costJ = ", res[k].J, " traj L = ", res[k].l)
  return

if __name__ == "__main__":
  test_pwdc()
  test_pwdc_plot()