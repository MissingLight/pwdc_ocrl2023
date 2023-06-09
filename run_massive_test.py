"""
"""

import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import context
import pwdc
import pwdc_AStar

import misc

import optm_ddc2
import obstacle as obs
import naive_init_baseline as naive
import kAstar_init_baseline as kAstar
# import scaleAstar_init_baseline as scaleAstar
import scaleAstar_init_baseline_refactor as scaleAstar
import trrt_init_baseline as tRRT

import pandas as pd

import getConfig


##########################################
### Global params BEGIN ###
##########################################

# mapname = 'random32A'
# mapname = 'random32B'
# mapname = 'random32C'
# mapname = 'random32D'

# mapname = 'random32E'
# mapname = 'random32F'
# mapname = 'random32G'
# mapname = 'random32H'
# mapname = 'random32I'
# mapname = 'random32J'

# mapname = 'random32AA'
# mapname = 'random32K_1'
# mapname = 'random32K_2'
# mapname = 'random32K_3'

# mapname = 'random32K_4'
# mapname = 'random32K_5'
# mapname = 'random32K_6'

# mapname = 'random32L_1'
# mapname = 'random32L_2'
# mapname = 'random32L_3'


# mapname = 'random32L_4'
# mapname = 'random32L_5'
# mapname = 'random32L_6'
# mapname = 'random32L_7'
# mduiapname = 'random32L_8'
# mapname = 'random32L_9'
# mapname = 'random32L_10'

# mapname = 'random32A_trrt'
# mapname = 'random32B_trrt'
# mapname = 'random32C_trrt'

# mapname = 'random32L_8_refactor'
# mapname = 'random32L_9_refactor'
# mapname = 'random32F_refactor'
# mapname = 'random32E_refactor'
# mapname = 'random32A_refactor'
# mapname = 'random32D_refactor'
# mapname = 'random32I_refactor'
mapname = 'random32_simu_refactor'

# mapname = 'random32M_refactor'
# mapname = 'random32N_refactor'
# mapname = 'random32O_refactor'



ConfigClass = getConfig.Config(mapname)
NInstance = 10

##########################################
### Global params END ###
##########################################


def PlotPwdc(configs, start_state, goal_state, idx,type = "pwdc"):

  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  res_file_path = configs["folder"]+"instance_"+str(idx)+"_" + type +"_result.pickle"
  
  solver = misc.LoadPickle(res_file_path)
  # configs = solver.cfg
  fig_sz,_ = solver.map_grid.shape
  fig_sz = 4 # fixed figure size, (or adaptive? based on grid size)
  res = solver.sol
  print(" get ", len(solver.emoa_res_dict), " Pareto paths" )
  print(" npix = ", configs["npix"] )

  # traj plot
  fig = plt.figure(figsize=(fig_sz,fig_sz))
  s = configs["Sinit"]
  d = configs["Sgoal"]
  xx = np.linspace(0,1,num=configs["npix"])
  yy = np.linspace(0,1,num=configs["npix"])
  Y,X = np.meshgrid(xx,yy) # this seems to be the correct way... Y first, X next.
  pf = solver.obs_pf
  plt.contourf(X, Y, pf, levels=np.linspace(np.min(pf), np.max(pf),200), cmap='gray_r')
  plt.plot(s[0],s[1],"ro")
  plt.plot(d[0],d[1],"r*")

  for k in res:
    px,py = solver._path2xy(res[k].init_path)
    plt.plot(px,py,"b--", alpha=0.6)

    tj = np.array([res[k].getPosX(),res[k].getPosY()])
    # plt.plot(tj[0,:], tj[1,:], "r.", markersize=1.0, alpha=0.6) # random 32x32
    plt.plot(tj[0,:], tj[1,:], "r.", markersize=1.5, alpha=0.6) # random 16x16

    print("k = ", k, "converge episode = ", res[k].epiIdxCvg, " costJ = ", res[k].J, " traj L = ", res[k].l)
  
  plt.xticks([0,1])
  plt.yticks([0,1])
  # plt.axis('off')
  plt.draw()
  plt.pause(1)
  save_path = configs["folder"]+"instance_"+str(idx)+ "_" +type+"_solTrajs.png"
  plt.savefig(save_path, bbox_inches='tight', pad_inches = 0, dpi=200)

  return

def RunWeightedAstar(configs, start_state, goal_state, idx):
  """
  """
  # override the default start and goal with the input ones.
  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  
  pwdc_fname = configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle"
  solver_pwdc = misc.LoadPickle(pwdc_fname)
  # emoa_res = solver_pwdc.emoa_res_dict

  w1 = 0.5
  w2 = 0.5
  print("weight = ", w1, w2)
  configs["Astar_weight_list"].append([w1,w2])

  astarSol = scaleAstar.AStar(configs, solver_pwdc.obs_pf)
  astarSol.solveScaleAstar()

  res_fname = configs["folder"]+"instance_"+str(idx)+"_wghA_result.pickle"
  misc.SavePickle(astarSol, res_fname)
  return

def RunTranlationRRT(configs, start_state, goal_state, idx):
  """
  """
  # override the default start and goal with the input ones.
  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  
  pwdc_fname = configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle"
  solver_pwdc = misc.LoadPickle(pwdc_fname)
  # emoa_res = solver_pwdc.emoa_res_dict

  tRRTSol = tRRT.transitionRRT(configs, solver_pwdc.obs_pf)
  tRRT_res = tRRTSol.solveTRRT()

  res_fname = configs["folder"]+"instance_"+str(idx)+"_tRRT_result.pickle"
  misc.SavePickle(tRRTSol, res_fname)
  return


def RunNaiveInit(configs, start_state, goal_state, idx, obs_pf):
  """
  """
  # override the default start and goal with the input ones.
  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state

  pwdc_fname = configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle"
  solver_pwdc = misc.LoadPickle(pwdc_fname)
  pwdc_res = solver_pwdc.sol
  trajLenList_pwdc = []
  for k in pwdc_res:
    trajLenList_pwdc.append(pwdc_res[k].l)
  trajLenList_pwdc = np.array(trajLenList_pwdc)

  res_dict = dict()
  if len(trajLenList_pwdc) == 0: # PWDC fails
    res_dict["num_nodes"] = 0
    res_dict["lin_sol"] = []
    res_dict["lin_sol_cost"] = np.nan
    res_dict["rdm_sol"] = []
    res_dict["rdm_sol_cost"] = np.nan
    res_dict["max_iter"] = 0
    # res_dict["pf"] = pf
  else:
    num_nodes = int(np.mean(trajLenList_pwdc))
    max_iter = int(configs["iters_per_episode"]* configs["total_epi"])
    print('num nodes of the navie init',num_nodes, "max_iter = ", max_iter)
    # naive.run_naive_init(folder, configs, num_nodes, save_path, max_iter)
    save_fig_path = configs["folder"]+"instance_"+str(idx)+"_naive_init_fig.png"
    res_dict = naive.run_naive_init_for_test(configs, num_nodes, save_fig_path, max_iter, obs_pf)

  save_path = configs["folder"] + "instance_"+str(idx)+"_dirColInit_result.pickle"
  misc.SavePickle(res_dict, save_path)
  return


def plot_pareto_front():

  configs = ConfigClass.configs
  # TODO: ADD WEIGHTED A STAR 

  solver = misc.LoadPickle(configs["folder"]+"result.pickle")
  res = solver.emoa_res_dict
  # print(res)
  plt.figure(figsize=(3,3))
  cost_array = np.array( list(res['costs'].values()) )
  
  print("total EMOA* #sol = ", len(cost_array))
  for k in res["costs"]:
    c = res['costs'][k]
    plt.plot(c[0],c[1]/np.min(cost_array),"g.", alpha=0.5)

  print("total PWDC converged #sol = ", len(solver.sol))
  for k in solver.sol:
    c = res['costs'][k]
    plt.plot(c[0],c[1]/np.min(cost_array),"ro", alpha=0.6)
  
  print("total PWDC un-converged #sol = ", len(solver.tjObjDict))
  for k in solver.tjObjDict:
    c = res['costs'][k]
    plt.plot(c[0],c[1]/np.min(cost_array),"bo", alpha=0.6)
  plt.grid("on")
  plt.draw()
  plt.pause(2)
  plt.savefig(configs["folder"]+"pareto_front.png", bbox_inches='tight', dpi=200)
  return


def PlotParetoPaths(configs, start_state, goal_state, idx):
  """
  """

  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  solver = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle")
  plt.figure(figsize=(4,4))
  
  # configs = solver.cfg
  pf = solver.obs_pf
  xx = np.linspace(0,1,num=configs["npix"])
  yy = np.linspace(0,1,num=configs["npix"])
  Y,X = np.meshgrid(xx,yy) # this seems to be the correct way... Y first, X next.
  plt.contourf(X, Y, pf, levels=np.linspace(np.min(pf), np.max(pf),200), cmap='gray_r')
  plt.plot(configs["Sinit"][0],configs["Sinit"][1],"ro")
  plt.plot(configs["Sgoal"][0],configs["Sgoal"][1],"r*")

  res = solver.emoa_res_dict
  npix = solver.cfg["npix"]
  for k in res["paths"]:
    p = res['paths'][k]
    px = list()
    py = list()
    for v in p:
      py.append( ((v%(npix*npix))%npix)*(1/npix) )
      px.append( int(np.floor((v%(npix*npix))/npix))*(1.0/npix) )
    plt.plot(px,py,"g")

  for k in solver.sol:
    p = res['paths'][k]
    px = list()
    py = list()
    for v in p:
      py.append( ((v%(npix*npix))%npix)*(1/npix) )
      px.append( int(np.floor((v%(npix*npix))/npix))*(1.0/npix) )
    plt.plot(px,py,"r--")

  for k in solver.tjObjDict:
    p = res['paths'][k]
    px = list()
    py = list()
    for v in p:
      py.append( ((v%(npix*npix))%npix)*(1/npix) )
      px.append( int(np.floor((v%(npix*npix))/npix))*(1.0/npix) )
    plt.plot(px,py,"b:")
    
  plt.xlim([-0.01,1.01])
  plt.xticks([0,1])
  plt.ylim([-0.01,1.01])
  plt.yticks([0,1])
  plt.draw()
  plt.pause(2)
  save_name = configs["folder"]+"instance_"+str(idx)+"_pareto_paths.png"
  plt.savefig(save_name, bbox_inches='tight', dpi=200)
  return


def main_test_wghA():
  """
    # must run weighted A* after PWDC, since weighted A* needs the #sol in PWDC.
  """
  configs = ConfigClass.configs
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  for ii in range(start_states.shape[0]):
    RunWeightedAstar(configs, start_states[ii,:], goal_states[ii,:], ii)
  return

def main_test_tRRT():
  """
  """
  configs = ConfigClass.configs
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  for ii in range(start_states.shape[0]):
  # for ii in [2]:
    RunTranlationRRT(configs, start_states[ii,:], goal_states[ii,:], ii)
  return

def main_test_naiveInit():
  configs = ConfigClass.configs
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  for ii in range(start_states.shape[0]):
    RunNaiveInit(configs, start_states[ii,:], goal_states[ii,:], ii, obs_pf)
  return

def main_plot_pwdc():
  print("--- main_plot_pwdc ---")
  configs = ConfigClass.configs
  print("configs[npix] = ", configs["npix"])
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  # ii = 1
  for ii in range(NInstance):
    PlotPwdc(configs, start_states[ii,:], goal_states[ii,:], ii)
    PlotParetoPaths(configs, start_states[ii,:], goal_states[ii,:], ii)


def main_plot_pwdc_AStar():
  print("--- main_plot_pwdc_AStar ---")
  configs = ConfigClass.configs
  print("configs[npix] = ", configs["npix"])
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  # ii = 1
  for ii in range(NInstance):
    PlotPwdc(configs, start_states[ii,:], goal_states[ii,:], ii,"pwdc_AStar")


def main_plot_baseline():
  print("--- main_plot_baseline ---")
  configs = ConfigClass.configs
  print("configs[npix] = ", configs["npix"])
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  # ii = 1
  for ii in range(NInstance):
    # Plotbaseline(configs, start_states[ii,:], goal_states[ii,:], ii,"wghA")
    Plotbaseline(configs, start_states[ii,:], goal_states[ii,:], ii,"tRRT")
    PlotPwdc(configs, start_states[ii,:], goal_states[ii,:], ii,"pwdc_AStar")


def Plotbaseline(configs, start_state, goal_state, idx,baseline):

  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  res_file_path = configs["folder"]+"instance_"+str(idx)+"_"+baseline+"_result.pickle"
  
  solver = misc.LoadPickle(res_file_path)
  # print('len(solver.Astar_pathlist)',len(solver.Astar_pathlist))
  # configs = solver.cfg
  fig_sz,_ = solver.map_grid.shape
  fig_sz = 4 # fixed figure size, (or adaptive? based on grid size)
  res = solver.sol

  # traj plot
  fig = plt.figure(figsize=(fig_sz,fig_sz))
  s = configs["Sinit"]
  d = configs["Sgoal"]
  xx = np.linspace(0,1,num=configs["npix"])
  yy = np.linspace(0,1,num=configs["npix"])
  Y,X = np.meshgrid(xx,yy) # this seems to be the correct way... Y first, X next.
  pf = solver.obs_pf

  plt.contourf(X, Y, pf, levels=np.linspace(np.min(pf), np.max(pf),200), cmap='gray_r')
  plt.plot(s[0],s[1],"ro")
  plt.plot(d[0],d[1],"r*")

  if baseline =="tRRT":
    for node in solver.node_list:
        if node.parent:
            plt.plot([node.x/configs["npix"], node.parent.x/configs["npix"]],
                     [node.y/configs["npix"], node.parent.y/configs["npix"]], "-y")


  
  print("Baseline",baseline,", length of res", len(res))
  for k in res:
    px,py,_ = solver._path2xy(res[k].init_path)
    plt.plot(px,py,"b--", alpha=0.6)

    print("Baseline",baseline,", length of path", len(px))

    tj = np.array([res[k].getPosX(),res[k].getPosY()])
    # plt.plot(tj[0,:], tj[1,:], "r.", markersize=1.0, alpha=0.6) # random 32x32
    plt.plot(tj[0,:], tj[1,:], "r.", markersize=1.5, alpha=0.6) # random 16x16

    print("k = ", k, "converge episode = ", res[k].epiIdxCvg, " costJ = ", res[k].J, " traj L = ", res[k].l)
  
  plt.xticks([0,1])
  plt.yticks([0,1])
  # plt.axis('off')
  plt.draw()
  plt.pause(1)
  save_path = configs["folder"]+"instance_"+str(idx)+"_"+baseline+"Trajs.png"
  plt.savefig(save_path, bbox_inches='tight', pad_inches = 0, dpi=200)

  return


def PlotCvgIters(idx):

  configs = ConfigClass.configs
  pwdc_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle")
  scaleAstar_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_pwdc_AStar_result.pickle")  
  # scaleAstar_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_wghA_result.pickle")
  tRRT_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_tRRT_result.pickle")  
  naive_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_dirColInit_result.pickle")

  # kAstar_res_dict = misc.LoadPickle(configs["folder"]+"kAstar_res.pickle")
  pwdc_res = pwdc_res_dict.sol
  plt.figure(figsize=(3,2))
  epiIdxList_pwdc = list()
  JcostList_pwdc = list()
  trajLenList_pwdc = list()
  for k in pwdc_res:
    epiIdxList_pwdc.append(pwdc_res[k].epiIdxCvg)
    JcostList_pwdc.append(pwdc_res[k].J)
    trajLenList_pwdc.append(pwdc_res[k].l)
  epiIdxList_pwdc = np.array(epiIdxList_pwdc)
  JcostList_pwdc = np.array(JcostList_pwdc)
  trajLenList_pwdc = np.array(trajLenList_pwdc)
  if len(epiIdxList_pwdc) > 0:
    plt.plot(epiIdxList_pwdc+1, JcostList_pwdc/np.min(JcostList_pwdc), "ro",alpha=0.5)
  # plt.plot(epiIdxList+1, trajLenList/np.min(trajLenList), "bo")

  scaleAstar_res = scaleAstar_res_dict.sol
  epiIdxList_scaleAstar = list()
  JcostList_scaleAstar = list()
  trajLenList_scaleAstar = list()
  for k in scaleAstar_res:
    epiIdxList_scaleAstar.append(scaleAstar_res[k].epiIdxCvg)
    JcostList_scaleAstar.append(scaleAstar_res[k].J)
    trajLenList_scaleAstar.append(scaleAstar_res[k].l)
  epiIdxList_scaleAstar = np.array(epiIdxList_scaleAstar)
  JcostList_scaleAstar = np.array(JcostList_scaleAstar)
  trajLenList_scaleAstar = np.array(trajLenList_scaleAstar)
  if len(JcostList_pwdc) > 0:
    plt.plot(epiIdxList_scaleAstar + 1, JcostList_scaleAstar/np.min(JcostList_pwdc), "b^",alpha=0.5)
  # plt.plot(epiIdxList+1, trajLenList/np.min(trajLenList), "bo")

  tRRT_res = tRRT_res_dict.sol
  epiIdxList_tRRT = list()
  JcostList_tRRT = list()
  trajLenList_tRRT = list()
  for k in tRRT_res:
    epiIdxList_tRRT.append(tRRT_res[k].epiIdxCvg)
    JcostList_tRRT.append(tRRT_res[k].J)
    trajLenList_tRRT.append(tRRT_res[k].l)
  epiIdxList_tRRT = np.array(epiIdxList_tRRT)
  JcostList_tRRT = np.array(JcostList_tRRT)
  trajLenList_tRRT = np.array(trajLenList_tRRT)
  if len(JcostList_pwdc) > 0:
    plt.plot(epiIdxList_tRRT+1, JcostList_tRRT/np.min(JcostList_pwdc), "g^",alpha=0.5)
  # plt.plot(epiIdxList+1, trajLenList/np.min(trajLenList), "bo")

  ## DirCol + naive init

  if len(epiIdxList_pwdc) > 0:
    lin_sol_cost_ratio = naive_res_dict["lin_sol_cost"]/np.min(JcostList_pwdc)
    plt.plot([1,10],[lin_sol_cost_ratio,lin_sol_cost_ratio],'k--',lw=2)

    rdm_sol_cost_ratio = naive_res_dict["rdm_sol_cost"]/np.min(JcostList_pwdc)
    plt.plot([1,10],[rdm_sol_cost_ratio,rdm_sol_cost_ratio],'k-',lw=1)

  ### k-best
  # kastar_sol_cost_ratio = kAstar_res_dict["kAstar_sol_cost"]/np.min(JcostList_pwdc)
  # plt.plot([1,10],[kastar_sol_cost_ratio,kastar_sol_cost_ratio],'g--',lw=1)

  plt.grid("on")
  plt.draw()
  plt.pause(2)
  plt.savefig(configs["folder"]+"instance_"+str(idx)+"_iter_compare.png", bbox_inches='tight', dpi=200)
  return

def main_plot_cvg_iters():
  for idx in range(NInstance):
    PlotCvgIters(idx)

def main_compare_cvg_iters():
  """
  """
  configs = ConfigClass.configs
  mat_cvg_data = np.zeros([NInstance,3])
  mat_cost_data = np.zeros([NInstance,5])

  np.set_printoptions(precision=3, suppress=True)
  
  succ_count = 0
  for idx in range(NInstance):
    print("idx = ", idx)
    pwdc_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle")
    if len(pwdc_res_dict.sol) == 0:
      continue
    else:
      succ_count = succ_count + 1
    scaleAstar_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_pwdc_AStar_result.pickle")
    # scaleAstar_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_wghA_result.pickle")
    naive_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_dirColInit_result.pickle")
    tRRT_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_tRRT_result.pickle")  

    ## pwdc ##
    pwdc_res = pwdc_res_dict.sol
    epiIdxList_pwdc = list()
    JcostList_pwdc = list()
    for k in pwdc_res:
      epiIdxList_pwdc.append(pwdc_res[k].epiIdxCvg)
      JcostList_pwdc.append(pwdc_res[k].J)
    epiIdxList_pwdc = np.array(epiIdxList_pwdc)
    JcostList_pwdc = np.array(JcostList_pwdc)
    mat_cvg_data[idx,0] = np.min(epiIdxList_pwdc)
    mat_cost_data[idx,0] = np.min(JcostList_pwdc)

    ## wA* ##
    scaleAstar_res = scaleAstar_res_dict.sol
    epiIdxList_scaleAstar = list()
    JcostList_scaleAstar = list()
    trajLenList_scaleAstar = list()
    for k in scaleAstar_res:
      epiIdxList_scaleAstar.append(scaleAstar_res[k].epiIdxCvg)
      JcostList_scaleAstar.append(scaleAstar_res[k].J)
      trajLenList_scaleAstar.append(scaleAstar_res[k].l)
    if len(scaleAstar_res) > 0:
      epiIdxList_scaleAstar = np.array(epiIdxList_scaleAstar)
      JcostList_scaleAstar = np.array(JcostList_scaleAstar)
      mat_cvg_data[idx,1] = np.min(epiIdxList_scaleAstar)
      mat_cost_data[idx,1] = np.min(JcostList_scaleAstar)
    else:
      mat_cvg_data[idx,1] = np.inf
      mat_cost_data[idx,1] = np.inf

    ## tRRT ##
    tRRT_res = tRRT_res_dict.sol
    epiIdxList_tRRT = list()
    JcostList_tRRT = list()
    trajLenList_tRRT = list()
    for k in tRRT_res:
      epiIdxList_tRRT.append(tRRT_res[k].epiIdxCvg)
      JcostList_tRRT.append(tRRT_res[k].J)
      trajLenList_tRRT.append(tRRT_res[k].l)
    if len(tRRT_res) > 0:
      epiIdxList_tRRT = np.array(epiIdxList_tRRT)
      JcostList_tRRT = np.array(JcostList_tRRT)
      mat_cvg_data[idx,2] = np.min(epiIdxList_tRRT)
      mat_cost_data[idx,2] = np.min(JcostList_tRRT)
    else:
      mat_cvg_data[idx,2] = np.inf
      mat_cost_data[idx,2] = np.inf


    ## DirCol + naive init
    naive_res_dict = misc.LoadPickle(configs["folder"]+"instance_"+str(idx)+"_dirColInit_result.pickle")
    mat_cost_data[idx,3] = naive_res_dict["lin_sol_cost"]
    mat_cost_data[idx,4] = naive_res_dict["rdm_sol_cost"]

  print(mat_cost_data)

  print("----mapname = ", mapname, "----")
  print("----mat_cost_data----")
  print(mat_cost_data)
  print("----mat_cost_data, PWDC succeeds in = ", succ_count, " cases ----")
  print("DirCol-wA* > 2*PWDC", np.sum(mat_cost_data[:,1] > 2*mat_cost_data[:,0]), np.sum(mat_cost_data[:,1] > 2*mat_cost_data[:,0])/succ_count)
  print("DirCol-tRRT > 2.0*PWDC", np.sum(mat_cost_data[:,2] > 2*mat_cost_data[:,0]), np.sum(mat_cost_data[:,2] > 2.0*mat_cost_data[:,0])/succ_count)
  print("DirCol-linear > 2*PWDC", np.sum(mat_cost_data[:,3] > 2*mat_cost_data[:,0]), np.sum(mat_cost_data[:,3] > 2*mat_cost_data[:,0])/succ_count)
  print("DirCol-random > 2*PWDC", np.sum(mat_cost_data[:,4] > 2*mat_cost_data[:,0]), np.sum(mat_cost_data[:,4] > 2*mat_cost_data[:,0])/succ_count)
  print("------------------")
  print("DirCol-wA* > 1.5*PWDC", np.sum(mat_cost_data[:,1] > 1.5*mat_cost_data[:,0]), np.sum(mat_cost_data[:,1] > 1.5*mat_cost_data[:,0])/succ_count)
  print("DirCol-tRRT > 1.5*PWDC", np.sum(mat_cost_data[:,2] > 1.5*mat_cost_data[:,0]), np.sum(mat_cost_data[:,2] > 1.5*mat_cost_data[:,0])/succ_count)
  print("DirCol-linear > 1.5*PWDC", np.sum(mat_cost_data[:,3] > 1.5*mat_cost_data[:,0]), np.sum(mat_cost_data[:,3] > 1.5*mat_cost_data[:,0])/succ_count)
  print("DirCol-random > 1.5*PWDC", np.sum(mat_cost_data[:,4] > 1.5*mat_cost_data[:,0]), np.sum(mat_cost_data[:,4] > 1.5*mat_cost_data[:,0])/succ_count)
  print("------------------")
  print("DirCol-wA* > 1.0*PWDC", np.sum(mat_cost_data[:,1] > 1.0*mat_cost_data[:,0]), np.sum(mat_cost_data[:,1] > 1.0*mat_cost_data[:,0])/succ_count)
  print("DirCol-tRRT > 1.0*PWDC", np.sum(mat_cost_data[:,2] > 1.0*mat_cost_data[:,0]), np.sum(mat_cost_data[:,2] > 1.0*mat_cost_data[:,0])/succ_count)
  print("DirCol-linear > 1.0*PWDC", np.sum(mat_cost_data[:,3] > 1.0*mat_cost_data[:,0]), np.sum(mat_cost_data[:,3] > 1.0*mat_cost_data[:,0])/succ_count)
  print("DirCol-random > 1.0*PWDC", np.sum(mat_cost_data[:,4] > 1.0*mat_cost_data[:,0]), np.sum(mat_cost_data[:,4] > 1.0*mat_cost_data[:,0])/succ_count)

  print("----mat_cvg_data----")
  print(mat_cvg_data)
    
  print("DirCol-wA* > 2*PWDC", np.sum(mat_cvg_data[:,1] > 2*mat_cvg_data[:,0]), np.sum(mat_cvg_data[:,1] > 2*mat_cvg_data[:,0])/succ_count)
  print("DirCol-tRRT > 2*PWDC", np.sum(mat_cvg_data[:,2] > 2.0*mat_cvg_data[:,0]), np.sum(mat_cvg_data[:,2] > 2*mat_cvg_data[:,0])/succ_count)

  # print("DirCol-linear > 2*PWDC", np.sum(mat_cvg_data[:,2] > 2*mat_cvg_data[:,0]))
  # print("DirCol-random > 2*PWDC", np.sum(mat_cvg_data[:,3] > 2*mat_cvg_data[:,0]))

  with open(configs["folder"]+"costs_baseline_vs_PWTO.txt", 'w') as f:
    f.write("#costs, DirCol-wA* > 2*PWDC = " + str( np.sum(mat_cost_data[:,1] > 2*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,1] > 2*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-wA* > 1*PWDC = " + str( np.sum(mat_cost_data[:,1] > 1*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,1] > 1*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-wA* fail to converge = " + str( np.sum(mat_cost_data[:,1]==np.inf) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,1]==np.inf)/succ_count) )
    f.write("\n\n")

    f.write("#costs, DirCol-tRRT > 2*PWDC = " + str( np.sum(mat_cost_data[:,2] > 2*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,2] > 2*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-tRRT > 1*PWDC = " + str( np.sum(mat_cost_data[:,2] > 1*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,2] > 1*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-tRRT fail to converge = " + str( np.sum(mat_cost_data[:,2]==np.inf) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,2]==np.inf)/succ_count) )
    f.write("\n\n")

    f.write("#costs, DirCol-linear > 2*PWDC = " + str( np.sum(mat_cost_data[:,3] > 2*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,3] > 2*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-linear > 1*PWDC = " + str( np.sum(mat_cost_data[:,3] > 1*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,3] > 1*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-linear fail to converge = " + str( np.sum(mat_cost_data[:,3]==np.inf) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,3]==np.inf)/succ_count) )
    f.write("\n\n")

    f.write("#costs, DirCol-random > 2*PWDC = " + str( np.sum(mat_cost_data[:,4] > 2*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,4] > 2*mat_cost_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#costs, DirCol-random > 1*PWDC = " + str( np.sum(mat_cost_data[:,4] > 1*mat_cost_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,4] > 1*mat_cost_data[:,0])/succ_count) )
    f.write("\n")    
    f.write("#costs, DirCol-random fail to converge = " + str( np.sum(mat_cost_data[:,4]==np.inf) ) + 
            ", percentage = "+str(np.sum(mat_cost_data[:,4]==np.inf)/succ_count) )
    f.write("\n\n")


    ct = np.sum(mat_cost_data[:,1] > 2*mat_cost_data[:,0]) + np.sum(mat_cost_data[:,2] > 2*mat_cost_data[:,0]) \
       + np.sum(mat_cost_data[:,3] > 2*mat_cost_data[:,0]) + np.sum(mat_cost_data[:,4] > 2*mat_cost_data[:,0]) 
    f.write("#costs, all baselines > 2*PWDC = " + str(ct) + ", percentage = "+str(ct*1.0/succ_count/4 ))
    f.write("\n")
    ct = np.sum(mat_cost_data[:,1] > 1*mat_cost_data[:,0]) + np.sum(mat_cost_data[:,2] > 1*mat_cost_data[:,0]) \
       + np.sum(mat_cost_data[:,3] > 1*mat_cost_data[:,0]) + np.sum(mat_cost_data[:,4] > 1*mat_cost_data[:,0]) 
    f.write("#costs, all baselines > 1*PWDC = " + str(ct) + ", percentage = "+str(ct*1.0/succ_count/4) )
    f.write("\n")


  with open(configs["folder"]+"converge_iters_baseline_vs_PWTO.txt", 'w') as f:
    f.write("#iters, DirCol-wA* > 2*PWDC = " + str( np.sum(mat_cvg_data[:,1] > 2*mat_cvg_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cvg_data[:,1] > 2*mat_cvg_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#iters, DirCol-wA* fail to converge = " + str( np.sum(mat_cvg_data[:,1]==np.inf) ) + 
            ", percentage = "+str(np.sum(mat_cvg_data[:,1]==np.inf)/succ_count) )
    f.write("\n")

    f.write("#iters, DirCol-tRRT > 2*PWDC = " + str( np.sum(mat_cvg_data[:,2] > 2*mat_cvg_data[:,0]) ) + 
            ", percentage = "+str(np.sum(mat_cvg_data[:,2] > 2*mat_cvg_data[:,0])/succ_count) )
    f.write("\n")
    f.write("#iters, DirCol-tRRT fail to converge = " + str( np.sum(mat_cvg_data[:,2]==np.inf) ) + 
            ", percentage = "+str(np.sum(mat_cvg_data[:,2]==np.inf)/succ_count) )
    f.write("\n")

    ct = np.sum(mat_cvg_data[:,1] > 2*mat_cvg_data[:,0]) \
       + np.sum(mat_cvg_data[:,2] > 2*mat_cvg_data[:,0]) \
      #  + np.sum(mat_cvg_data[:,3] > 2*mat_cvg_data[:,0]) 
    f.write("#iters, all baselines > 2*PWDC = " + str(ct) + ", percentage = "+str(ct*1.0/succ_count/2) )
    f.write("\n")
    ct = np.sum(mat_cvg_data[:,1] > 1*mat_cvg_data[:,0]) \
       + np.sum(mat_cvg_data[:,2] > 1*mat_cvg_data[:,0]) \
      #  + np.sum(mat_cvg_data[:,3] > 1*mat_cvg_data[:,0]) 
    f.write("#iters, all baselines > 1*PWDC = " + str(ct) + ", percentage = "+str(ct*1.0/succ_count/2) )
    f.write("\n")

  notcoverge_pdwc = []
  for kkk in range(mat_cost_data.shape[0]):
    if mat_cost_data[kkk,0] == 0:
      notcoverge_pdwc.append(kkk)
  print(notcoverge_pdwc)
  mat_cost_data = np.delete(mat_cost_data,notcoverge_pdwc,0)
  
  cost_pwdc = mat_cost_data[:,0]
  cost_wA = mat_cost_data[:,1]
  cost_tRRT = mat_cost_data[:,2]
  cost_linear = mat_cost_data[:,3]
  cost_random = mat_cost_data[:,4]

  cost_pwdc_ratio = cost_pwdc/cost_pwdc
  cost_wA_ratio = cost_wA/cost_pwdc
  cost_tRRT_ratio = cost_tRRT/cost_pwdc
  cost_linear_ratio = cost_linear/cost_pwdc
  cost_random_ratio = cost_random/cost_pwdc

  plot_x_dev = np.random.normal(1, 0.06, cost_pwdc.shape[0])-1
  print('plot_x_dev',plot_x_dev)
  xs = [ np.ones_like(cost_pwdc)+ plot_x_dev, 
        2*np.ones_like(cost_wA)+plot_x_dev, 
        3*np.ones_like(cost_tRRT)+plot_x_dev, 
        4*np.ones_like(cost_linear)+plot_x_dev, 
        5*np.ones_like(cost_random)+plot_x_dev]
  vals = [cost_pwdc_ratio,cost_wA_ratio,cost_tRRT_ratio,cost_linear_ratio,cost_random_ratio]
  names = ['pwdc', 'weighted-A*', 't-RRT', 'linear','Random']
  
  print(cost_pwdc_ratio)
  print(cost_wA_ratio)
  print(cost_tRRT_ratio)
  print(cost_linear_ratio)
  print(cost_random_ratio)

  plt.figure(figsize=(5,4))
  
  palette = ['r', 'g', 'b', 'y','#FA70B5']
  for x, val, c in zip(xs, vals, palette):
    plt.scatter(x, val, alpha=0.4, s=50, color=c)
  plt.boxplot(vals, labels=names,showfliers = False)
  xxx = np.linspace(0.5, 5.5, num=50)
  plt.plot(xxx, np.ones_like(xxx),'--',c='#FC5A50' )
  # plt.ylim([0,10])
  plt.xlabel("Baselines")
  plt.ylabel("Cost Ratio")
  plt.draw()
  plt.pause(2)
  plt.savefig(configs["folder"]+"cost_ratio.png", bbox_inches='tight', dpi=200)
  
  plt.figure(figsize=(3,2))

  count, _ = np.histogram( mat_cost_data[:,1] /mat_cost_data[:,0], bins=[0.0, 1, 2.0, np.inf] )
  plt.bar(np.array([0.0, 1, 2.0])+0.2, count, width=0.2, facecolor='r', alpha=0.8)

  count, _ = np.histogram( mat_cost_data[:,2] /mat_cost_data[:,0], bins=[0.0, 1, 2.0, np.inf] )
  plt.bar(np.array([0.0, 1, 2.0])+0.4, count, width=0.2, facecolor='y', alpha=0.8)

  count, _ = np.histogram( mat_cost_data[:,3] /mat_cost_data[:,0], bins=[0.0, 1, 2.0, np.inf] )
  plt.bar(np.array([0.0, 1, 2.0])+0.6, count, width=0.2, facecolor='g', alpha=0.8)

  count, _ = np.histogram( mat_cost_data[:,4] /mat_cost_data[:,0], bins=[0.0, 1, 2.0, np.inf] )
  plt.bar(np.array([0.0, 1, 2.0])+0.8, count, width=0.2, facecolor='b', alpha=0.8)

  plt.axvline(x = 1, color = 'k')

  plt.draw()
  plt.pause(2)
  plt.savefig(configs["folder"]+"cost_ratio_hist.png", bbox_inches='tight', dpi=200)




  return


#############

def RunPwdcOnce(configs, start_state, goal_state, idx, obs_pf = []):
  """
  """
  # override the default start and goal with the input ones.
  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  solver = pwdc.PWDC(configs, obs_pf) # pass in obs_pf to avoid repeatitive computation.
  solver.Solve()
  save_file = configs["folder"]+"instance_"+str(idx)+"_pwdc_result.pickle"
  print("PWDC get", len(solver.sol), " solutions, save to ", save_file)
  misc.SavePickle(solver, save_file)
  return

def main_test_pwdc():
  """
  """
  configs = ConfigClass.configs
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  for ii in range(start_states.shape[0]):
    RunPwdcOnce(configs, start_states[ii,:], goal_states[ii,:], ii, obs_pf)
  return

#############


#############

def RunPwdcAStarOnce(configs, start_state, goal_state, idx, obs_pf = []):
  """
  """
  # override the default start and goal with the input ones.
  configs["Sinit"] = start_state
  configs["Sgoal"] = goal_state
  solver = pwdc_AStar.PWDC_AStar(configs, obs_pf) # pass in obs_pf to avoid repeatitive computation.
  solver.Solve()
  save_file = configs["folder"]+"instance_"+str(idx)+"_pwdc_AStar_result.pickle"
  print("PWDC get", len(solver.sol), " solutions, save to ", save_file)
  misc.SavePickle(solver, save_file)
  return

def main_test_pwdc_AStar():
  """
  """
  configs = ConfigClass.configs
  instance = misc.LoadPickle(configs["folder"] + mapname + ".pickle")
  obs_pf = instance["obs_pf"]
  start_states = instance["starts"]
  goal_states = instance["goals"]
  configs["map_grid"] = instance["grids"]
  for ii in range(start_states.shape[0]):
    RunPwdcAStarOnce(configs, start_states[ii,:], goal_states[ii,:], ii, obs_pf)
  return

#############




if __name__ == "__main__":

  main_test_pwdc()

  main_test_pwdc_AStar() # new implenmentation of AStar, don't use main_test_wghA() anymore
  main_test_naiveInit()
  main_test_tRRT()

  main_plot_pwdc() 
  main_plot_baseline()   # main_plot_pwdc_AStar() is combined into the main_plot_baseline()
  main_plot_cvg_iters()
  main_compare_cvg_iters()