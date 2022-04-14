
import numpy as np
import cyipopt
import sys

import context
import dirCol as dc
import obstacle as obs
import dynamics as dyn

import matplotlib.pyplot as plt

def main1():
  
  # xo = np.array([3, 1, 0, 0, 0])
  # xf = np.array([3, 5, -np.pi, 0, 0])
  
  np.set_printoptions(precision=3, suppress=True)

  N = 11
  xo = np.array([1, 3, 0, 0, 0])
  Uinit = np.array([[1,1],[1,0],[1,0],[1,0],[1,0],[-1,0],[-1,-1],[-1,0],[-1,0],[-1,0]])
  Xinit = np.zeros([11,5])
  Xinit[0,:] = xo
  dt = 0.1
  for k in range(len(Uinit)):
    u = Uinit[k]
    Xinit[k+1,:] = dyn.fd_ddc2(Xinit[k,:],u,dt)
  xf = Xinit[N-1,:]
  print("Xinit = ",Xinit)

  Ulb = np.array([-2,-2])
  Uub = np.array([ 2, 2])
  
  # Xinit = np.zeros([N,5])
  # for k in range(5):
  #   Xinit[:,k] = np.linspace(xo[k],xf[k],N)
  # Xinit[:,3] = 4.0/100
  # Xinit[:,4] = 0
  # Uinit = np.ones([N-1,2])

  # obs_pos_array = np.array([[1,2],[2,2],[3,2],[3,4],[4,4],[5,4]])
  obs_pos_array = np.array([[1,1],[1,5]])
  obss = obs.ObstSet( obs_pos_array )

  nlp_prob = dc.NLP_ddc2(xo, xf, N, dt, Ulb, Uub, Xinit, Uinit, obss, w=100.0)

  Zinit = nlp_prob.toZ(nlp_prob.Xinit, nlp_prob.Uinit)

  print(" constr eval = ", nlp_prob.constraints(Zinit) )
  print(" obj eval = ", nlp_prob.objective(Zinit) )

  print("Zinit = ", Zinit)
  print("grad = ", nlp_prob.gradient(Zinit))
  jac = nlp_prob.jacobian(Zinit)
  print("jac = ", jac.shape)

  nlp = cyipopt.Problem(
     n=nlp_prob.lenZ,
     m=nlp_prob.lenC,
     problem_obj=nlp_prob,
     lb=nlp_prob.Zlb(),
     ub=nlp_prob.Zub(),
     cl=np.ones(nlp_prob.lenC)*(-0.5),
     cu=np.ones(nlp_prob.lenC)*(0.5),
  )


  # nlp.add_option('mu_strategy', 'adaptive')
  # nlp.add_option('tol', 1e-3)
  nlp.add_option('max_iter', 10)

  x, info = nlp.solve(nlp_prob.toZ(nlp_prob.Xinit, nlp_prob.Uinit))

  print(x)
  print(info)

  # fig = plt.figure(figsize=(3,3))
  fig = plt.figure()

  xy_tj = nlp_prob.getTrajXY(Zinit)
  plt.plot(xy_tj[:,0],xy_tj[:,1],"ro--")

  xy_tj = nlp_prob.getTrajXY(x)
  plt.plot(xy_tj[:,0],xy_tj[:,1],"bo--")

  plt.show()


  return

if __name__ == "__main__":
  main1() 