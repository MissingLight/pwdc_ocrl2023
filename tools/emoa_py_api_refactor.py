"""
About: python helper APIs
Author: Zhongqiang (Richard) Ren
"""

import numpy as np
import sys
import subprocess
import math

def costGrid2file(i,cg, fname, conn=4):
  """
  store the cost matrices to a file in the format required by EMOA* bin.
  cg = a numpy matrix.
  conn = 4 or 8, which means 4-connected or 8-connected.
  """
  (nyt, nxt) = cg.shape
  ntheta = 4 # four possible orientation of robot at each node

  num_nodes = nyt*nxt*ntheta
  num_edges = 2*((nyt-1)*(nxt-1)*2 + nyt-1 + nxt-1) # need to modify

  nghs = []
  if conn == 4:
    # nghs = [(0,0,1),(0,0,-1),(0,1,0,),(0,-1,0), 
    #         (np.pi/4,0,1),  (np.pi/4,0,-1), (np.pi/4,1,0),(np.pi/4,-1,0), 
    #         (-np.pi/4,0,1),(-np.pi/4,0,-1),(-np.pi/4,1,0),(-np.pi/4,-1,0)]

    # [d_theta, moving direction, direction and length]
    nghs = [(np.pi/2, np.pi/4, np.sqrt(2)), (0,0, 1), (-np.pi/2,-np.pi/4, np.sqrt(2)), 
            (np.pi/2,-np.pi/4,-np.sqrt(2)), (0,0,-1), (-np.pi/2,np.pi/4,-np.sqrt(2))]

  elif conn == 8:
    nghs = [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
  else:
    sys.exit("[ERROR] costGrid2file, neither 4- nor 8-connected!")

  with open(fname, mode="w+") as f:
    f.write("c This is a cost file for a grid world\n")
    f.write("p sp " + str(num_nodes) + " " + str(num_edges)+"\n")
    for itheta in range(ntheta):
      for iy in range(nyt):
        for ix in range(nxt):
          u = itheta*nyt*nxt + iy*nxt + ix
          for ngh in nghs:
            jtheta = itheta*np.pi/2 + ngh[0]
            jy = iy + int(ngh[2]*np.sin(itheta + ngh[1]))
            jx = ix + int(ngh[2]*np.cos(itheta + ngh[1]))
            if jy < 0 or jy >= nyt or jx < 0 or jx >= nxt:
            # if jy < 0 or jy >= nyt or jx < 0 or jx >= nxt or jtheta < 0 or jtheta >= np.pi*2:
              continue
            
            jtheta = clip_theta(jtheta)
            v = int(jtheta/(np.pi/2))*nyt*nxt + jy*nxt + jx
            
            if i ==0: # Note: Hardcoded here, cg_list[0] is always the motion cost 
              f.write("a "+str(u)+" "+str(v)+" "+str(int(cg[jy,jx]*math.ceil(abs(ngh[2]*10))))+"\n" ) # only support integer, floor the cost number.
            else:
              f.write("a "+str(u)+" "+str(v)+" "+str(int(cg[jy,jx]))+"\n" ) # only support integer, floor the cost number.
    f.close()
  return

def clip_theta(theta):
  if theta >= np.pi*2:
    theta_clip =  theta - np.pi*2
  elif theta < 0:
    theta_clip =  theta + np.pi*2
  else:
    theta_clip = theta
  return theta_clip


def getResult(res_file):
  """
  """
  res_dict = dict()
  with open(res_file, mode="r") as fres:
    lines = fres.readlines()
    temp = lines[0].split(':')
    res_dict["graph_load_time"] = float(temp[1])
    temp = lines[1].split(':')
    res_dict["n_generated"] = int(temp[1])
    temp = lines[2].split(':')
    res_dict["n_expanded"] = int(temp[1])
    temp = lines[3].split(':')
    res_dict["n_domCheck"] = int(temp[1])
    temp = lines[4].split(':')
    res_dict["rt_initHeu"] = float(temp[1])
    temp = lines[5].split(':')
    res_dict["rt_search"] = float(temp[1])
    temp = lines[6].split(":")
    res_dict['n_sol'] = int(temp[1])
    # print("-- n_sol = ", res_dict['n_sol'] )
    start_idx = 7
    res_dict["paths"] = dict()
    res_dict["costs"] = dict()
    for i in range(res_dict['n_sol']):
      # sol ID
      temp = lines[start_idx+3*i].split(":")
      solID = int(temp[1])
      # cost vector
      temp = lines[start_idx+3*i+1].split(",")
      cvec = list()
      cvec.append( int(temp[0][1:]) )
      for j in range(1,len(temp)-1):
        cvec.append(int(temp[j]))
      res_dict["costs"][solID] = np.array(cvec)
      # path
      temp = lines[start_idx+3*i+2].split(' ')
      res_dict["paths"][solID] = list(map(int, list(temp[:-1])))
  return res_dict


def runEMOA(cg_list, data_folder, exe_path, res_path, vo, vd, tlimit):
  """
  """
  print("[INFO] runEMOA (python) vo =", vo, ", vd =", vd, ", tlimit =", tlimit, ", M =", len(cg_list) )

  # generate cost files.
  fnames = list()
  for i,cg in enumerate(cg_list):
    fname = data_folder+"temp-c" + str(i+1) + ".gr"
    
    costGrid2file(i, cg, fname) # Note: Hardcoded here, cg_list[0] is always the motion cost    
    fnames.append(fname)
  print("[INFO] runEMOA (python) cost file generated..." )

  # run EMOA*.
  cmd = [exe_path, str(vo), str(vd), str(tlimit), str(len(cg_list))] + fnames
  cmd.append(res_path)
  
  process = subprocess.Popen(cmd, stdout=subprocess.PIPE)

  process.wait() # otherwise, subprocess run concurrently...
  print("[INFO] runEMOA (python) invoke c++ bin finished..." )

  out = getResult(res_path)
  print("[INFO] runEMOA (python) get result from file done..." )
  
  return out


if __name__ == "__main__":
  
  # cost grid 1
  c1 = np.ones([3,3])*3
  c1[0,2] = 1

  # cost grid 2
  c2 = np.ones([3,3])*3
  c2[1,1] = 1 
  
  # cost grid 3
  c3 = np.ones([3,3])*3
  c3[2,0] = 1

  # run EMOA
  res_dict = runEMOA([c1,c2,c3], "../data/", "../build/run_emoa", "../data/temp-res.txt", 0, 8, 60)
  print(res_dict)
