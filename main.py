import coilCalculator
import numpy
import matplotlib.pyplot as plt
# import convexApprox
# import splinify
import datastore
import solver
import convexApprox
import splinify


def discrete_fprime(f, z):
    pas = z[1] - z[0]
    f1 = numpy.roll(f, -1)
    f0 = numpy.roll(f, 1)
    return (f1 - f0) / (2 * pas)


def coil_construct(coil):
    # Mu impact
    Lp = coil["Lp"]
    Rp = coil["Rp"]
    Lb = coil["Lb"]
    Rbi = coil["Rbi"]
    Rbo = coil["Rbo"]
    mu = coil["mu"]
    test = coilCalculator.coilCalculator(True, meshsize=10)
    test.defineCoil(Lb, Rbi, Rbo)
    test.drawCoil()
    test.defineProjectile(Lp, Rp, mu=mu)
    test.drawProjectile()
    test.setSpace()
    test.computeL0()
    test.computedLz()
    # convex = convexApprox.Convex_approx(test.dLz_z, test.dLz)
    # lz = splinify.splinify(test.dLz_z, convex.run_approx(), test.L0)
    coil['L0'] = test.L0
    coil['dLz'] = test.dLz
    coil['dLz_z'] = test.dLz_z
    coil['n_points'] = len(test.dLz_z)
    # coil['splinify'] = lz
    coil['resistance'] = test.resistance


def build_some_coils(n=10):
    i = 0
    for index, coil in datastore.coils[datastore.coils['dLz'].isnull()].iterrows():
        print(index)
        coil_construct(coil)
        datastore.update_coil(coil)
        # datastore.save_all()
        i += 1
        if i == n:
            break


def build_a_coil(iloc):
    coil = datastore.coils.iloc[iloc]
    coil_construct(coil)
    datastore.update_coil(coil)


def find_optimal_launch(loc, C, R, E, plot=False, plot3d=False):
    coil = datastore.coils.iloc[loc]
    m = numpy.pi * coil.Rp**2 * coil.Lp * 7860 * 10 ** (-9)
    convex = convexApprox.Convex_approx(coil.dLz_z, coil.dLz, order=2)
    lz = splinify.splinify(convex.dLz_z, coil.L0, d2L=convex.run_approx())
    if plot:
        plot_l_b(coil, lz, convex)
    test = solver.gaussSolver(lz, C=C, R=R + coil.resistance, E=E, m=m)
    res = test._linear_opt(-(10 * coil.Lb) / 2000, plot=plot, plot3d=plot3d, epsilon=0.00005)
    # print(res)
    if plot:
        test.plot_single(res[1])
    print(test.computeMaxEc(res[1]), str(int(test.computeTau(res[1]) * 100)) + "%")
    return (test.computeMaxEc(res[1]), str(int(test.computeTau(res[1]) * 100)) + "%")


def plot_l_b(coil, spline, convex):
    print(coil.dLz_z, coil.dLz)
    # plt.plot(convex._d2Lz)
    # plt.plot(convex.run_approx())
    # plt.show()

    z = numpy.linspace(2 * spline.z[0], 2 * spline.z[-1], 10000)

    ax1 = plt.subplot(311)
    plt.plot(z, spline.Lz()(z), color=(0, 0, 1))
    plt.setp(ax1.get_xticklabels())

    ax2 = plt.subplot(312, sharex=ax1)
    plt.plot(spline.z, coil.dLz, color=(1, 0, 0))
    plt.plot(z, spline.dLz()(z), color=(0, 0, 1))
    plt.setp(ax2.get_xticklabels(), visible=False)

    plt.subplot(313, sharex=ax1)
    plt.plot(spline.z, convex.run_approx(), color=(0, 1, 0))
    plt.plot(spline.z, discrete_fprime(coil.dLz, coil.dLz_z), color=(1, 0, 0))
    plt.plot(z, spline.d2Lz()(z), color=(0, 0, 1))
    plt.show()


# build_some_coils(30)
build_a_coil(800)
find_optimal_launch(800, C=0.0024, E=400, R=0.07, plot=True, plot3d=True)
# find_optimal_launch(10, C=0.0024, E=400, R=0.07, plot=True, plot3d=True)