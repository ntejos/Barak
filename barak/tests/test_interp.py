from ..interp import trilinear_interp, interp_Akima
import numpy as np
from math import pi

def test_trilinear_interp():
    Nx, Ny, Nz = 10., 12., 14.
    X,Y,Z = np.mgrid[0:Nx, 0:Ny, 0:Nz]
    vals = np.cos(pi/Nx*(X-Z)) - np.sin(pi/Ny*(Y+Z))
    x0 = np.arange(Nx)
    y0 = np.arange(Ny)
    z0 = np.arange(Nz)

    N2x, N2y, N2z = 100., 101., 102.
    x1 = np.arange(N2x)* float(Nx-1) / N2x
    y1 = np.arange(N2y)* float(Ny-1) / N2y
    z1 = np.arange(N2z)* float(Nz-1) / N2z
    
    out = trilinear_interp(x1,y1,z1, x0,y0,z0,vals)

    # from ..plot import arrplot
    #arrplot(x0, y0, vals[:, :, 0])
    #arrplot(x1, y1, out[:, :, 0])

    #arrplot(y0, z0, vals[0, :, :])
    #arrplot(y1, z1, out[0, :, :])
    #pl.show()

def test_interp_Akima():
    x = np.sort(np.random.random(10) * 10)
    y = np.random.normal(0.0, 0.1, size=len(x))
    assert np.allclose(y, interp_Akima(x, x, y))


def test_CloughTocher2d_interp():
    try:
        from scipy.integrate import CloughTocher2DInterpolator
    except ImportError:
        return
    x = np.linspace(0, 2 * pi, 6)
    y = np.linspace(0, pi, 4)
    X,Y = np.meshgrid(x,y)
    z = np.sin(X) + np.cos(Y)
    x1 = np.linspace(0, 2 * pi, 12)
    y1 = np.linspace(0, pi, 10)

    assert np.allclose(
        CloughTocher2d_interp(x1, y1, x, y, z), np.array(
            [[ 1.        ,  1.5215599 ,  1.90364872,  1.99084836,  1.75011297,
               1.28734726,  0.71939825,  0.24766336,  0.0167194 ,  0.09080309,
               0.46637207,  1.        ],
             [ 0.87740392,  1.4045457 ,  1.76246431,  1.85869493,  1.6185309 ,
               1.16957749,  0.62038763,  0.1431984 , -0.08402454, -0.02057646,
               0.36745225,  0.88367502],
             [ 0.7217549 ,  1.21393963,  1.61416709,  1.69945015,  1.4670031 ,
               1.01511741,  0.46701045, -0.01473415, -0.25070581, -0.173784  ,
               0.18585168,  0.72925964],
             [ 0.5       ,  1.02063291,  1.40804276,  1.48261709,  1.25020998,
               0.78476714,  0.21752332, -0.2521541 , -0.48652123, -0.40716994,
               -0.02960837,  0.5       ],
             [ 0.1856543 ,  0.72636528,  1.10453004,  1.14548865,  0.93926275,
               0.44108854, -0.09930619, -0.57357923, -0.80707464, -0.72319726,
               -0.36861784,  0.17782309],
             [-0.17369664,  0.38446642,  0.74900715,  0.80089122,  0.58438927,
              0.09525943, -0.46315632, -0.94162957, -1.14291494, -1.08220286,
            -0.68206764, -0.18062066],
             [-0.5       ,  0.05884093,  0.41532324,  0.47179067,  0.24847643,
              -0.2174264 , -0.78753284, -1.24445443, -1.46435759, -1.41627677,
              -1.03114154, -0.5       ],
             [-0.73171961, -0.19236726,  0.1698433 ,  0.23136135,  0.01212243,
              -0.45443118, -0.9957497 , -1.45214212, -1.67089437, -1.63208693,
              -1.2198297 , -0.72670558],
             [-0.88537569, -0.34348997,  0.00451646,  0.07561483, -0.14296704,
              -0.60878044, -1.14091833, -1.61177504, -1.83034179, -1.76790773,
              -1.41537875, -0.88136446],
             [-1.        , -0.46419073, -0.09011717, -0.01572792, -0.24470446,
              -0.72220197, -1.28618495, -1.75012757, -1.98059722, -1.90994539,
              -1.53595225, -1.        ]])
        )
