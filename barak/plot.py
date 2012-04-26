""" Plotting routines. """
from __future__ import division

import numpy as np
import matplotlib.pyplot as pl
from matplotlib.collections import PolyCollection, LineCollection
import matplotlib.transforms as mtransforms

A4LANDSCAPE = 11.7, 8.3
A4PORTRAIT = 8.3, 11.7

def correct_marker_size(fmt):
    """ Find a default marker size such that different marker types
    look roughly the same size.
    """
    temp = fmt.replace('.-', '')
    if '.' in temp:
        ms = 10
    elif 'D' in temp:
        ms = 7
    elif set(temp).intersection('<>^vd'):
        ms = 9
    else:
        ms = 8
    return ms

def axvfill(xvals, ax=None, color='k', alpha=0.1, edgecolor='none', **kwargs):
    """ Fill vertical regions defined by a sequence of (left, right)
    positions.

    Parameters::
    
     xvals: sequence of pairs specifying the left and right extent of
            each region. e.g. (3,4) or [(0,1),(3,4)]
     ax=None: the axis to plot regions on.  default is the current axis.
     color='g': color of the regions.
     alpha=0.3: the opacity of the regions (1=opaque)

    Other keywords arguments are passed to PolyCollection.
    """
    if ax is None:
        ax = pl.gca()
    xvals = np.asanyarray(xvals)
    if xvals.ndim == 1:
        xvals = xvals[None, :]
    if xvals.shape[-1] != 2:
        raise ValueError('Invalid input')

    coords = [[(x0,0), (x0,1), (x1,1), (x1,0)] for x0,x1 in xvals]
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    kwargs.update(facecolor=color, edgecolor=edgecolor, transform=trans, alpha=alpha)

    p = PolyCollection(coords, **kwargs)
    ax.add_collection(p)
    ax.autoscale_view()
    return p

def axvlines(xvals, ymin=0, ymax=1, ax=None, ls='-', color='0.7', **kwargs):
    """ Plot a set of vertical lines at the given positions.
    """
    if ax is None:
        ax = pl.gca()

    coords = [[(x,ymin), (x,ymax)] for x in xvals]
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    kwargs.update(linestyle=ls, colors=color, transform=trans)

    l = LineCollection(coords, **kwargs)
    ax.add_collection(l)
    ax.autoscale_view()
    return l


def puttext(x,y,text,ax, xcoord='ax', ycoord='ax', **kwargs):
    """ Convenience function for printing text on an axis using axes
    coords."""
    if xcoord == 'data' and ycoord == 'ax':
        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    elif xcoord == 'ax' and ycoord == 'data':
        trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
    elif xcoord == 'ax' and ycoord == 'ax':
        trans = ax.transAxes
    else:
        raise ValueError("Bad keyword combination: %s, %s "%(xcoord,ycoord))
    return ax.text(x, y, str(text), transform=trans, **kwargs)


def distplot(vals, xvals=None, perc=(68, 95), showmean=False,
             showoutliers=True, color='forestgreen',  ax=None,
             logx=False, logy=False, negval=None, **kwargs):
    """
    Make a top-down histogram plot for an array of
    distributions. Shows the median, 68%, 95% ranges and outliers.

    Similar to a boxplot.

    Parameters::
    
     vals: sequence of arrays
         2-d array or a sequence of 1-d arrays.
     xvals: array of floats
         x positions.
     perc: array of floats  (68, 95)
         The percentile levels to use for area shading. Defaults show
         the 68% and 95% percentile levels; roughly 1 and 2
         sigma ranges for a Gaussian distribution.
     showmean: boolean  (False)
         Whether to show the means as a dashed black line.
     showoutliers: boolean (False)
         Whether to show outliers past the highest percentile range.
     color: mpl color ('forestgreen')
     ax: mpl Axes object
         Plot to this mpl Axes instance.
     logx, logy: bool (False)
         Whether to use a log x or y axis.
     negval: float (None)
         If using a log y axis, replace negative plotting values with
         this value (by default it chooses a suitable value based on
         the data values).
    """
    if any(not hasattr(a, '__iter__') for a in vals):
        raise ValueError('Input must be a 2-d array or sequence of arrays')

    assert len(perc) == 2
    perc = sorted(perc)
    temp = 0.5*(100 - perc[0])
    p1, p3 = temp, 100 - temp
    temp = 0.5*(100 - perc[1])
    p0, p4 = temp, 100 - temp
    percentiles = p0, p1, 50, p3, p4

    if ax is None:
        fig = pl.figure()
        ax = fig.add_subplot(111)

    if xvals is None:
        xvals = np.arange(len(vals), dtype=float)


    # loop through columns, finding values to plot
    x = []
    levels = []
    outliers = []
    means = []
    for i in range(len(vals)):
        d = np.asanyarray(vals[i])
        # remove nans
        d = d[~np.isnan(d)]
        if len(d) == 0:
            # no data, skip this position
            continue
        # get percentile levels
        levels.append(scoreatpercentile(d, percentiles))
        if showmean:
            means.append(d.mean())
        # get outliers
        if showoutliers:
            outliers.append(d[(d < levels[-1][0]) | (levels[-1][4] < d)])
        x.append(xvals[i])

    levels = np.array(levels)
    if logx and logy:
        ax.loglog([],[])
    elif logx:
        ax.semilogx([],[])
    elif logy:
        ax.semilogy([],[])

    if logy:
        # replace negative values with a small number, negval
        if negval is None:
            # guess number, falling back on 1e-5
            temp = levels[:,0][levels[:,0] > 0]
            if len(temp) > 0:
                negval = np.min(temp)
            else:
                negval = 1e-5

        levels[~(levels > 0)] = negval
        for i in range(len(outliers)):
            outliers[i][outliers[i] < 0] = negval
            if showmean:
                if means[i] < 0:
                    means[i] = negval

    ax.fill_between(x,levels[:,0], levels[:,1], color=color, alpha=0.2, edgecolor='none')
    ax.fill_between(x,levels[:,3], levels[:,4], color=color, alpha=0.2, edgecolor='none')
    ax.fill_between(x,levels[:,1], levels[:,3], color=color, alpha=0.5, edgecolor='none')
    if showoutliers:
        x1 = np.concatenate([[x[i]]*len(out) for i,out in enumerate(outliers)])
        out1 = np.concatenate(outliers)
        ax.plot(x1, out1, '.', ms=1, color='0.3')
    if showmean:
        ax.plot(x, means, 'k--')
    ax.plot(x, levels[:,2], 'k-', **kwargs)
    ax.set_xlim(xvals[0],xvals[-1])
    try:
        ax.minorticks_on()
    except AttributeError:
        pass

    return ax

def errplot(x, y, yerrs, xerrs=None, fmt='.b', ax=None, ms=None, mew=0.5,
            ecolor=None, elw=None, zorder=None, nonposval=None, **kwargs):
    """ Plot a graph with y errors.

    Parameters::

     x, y: arrays of shape (N,)
         Data.
     yerrs: array of shape (N,) or shape(N,2)
         Either an array with the same length y, or a list of two such
         arrays, giving lower and upper limits to plot.
     xerrs:
         Optional x errors.
     fmt: str
         Passed to the plot command for the x,y points.
     ms, mew: floats
         Plotting marker size and edge width.
     ecolor: matplotlib color (None)
         Color of the error bars. By default this will be the same color
         as the markers.
     elw: matplotlib line width (None)
     nonposval: float (None)
         If given, replace any non-positive values of y with this
    """
    yerrs = np.array(yerrs)
    if yerrs.ndim > 1:
        lo = yerrs[0]
        hi = yerrs[1]
    else:
        lo = y - yerrs
        hi = y + yerrs

    if ax is None:
        fig = pl.figure()
        ax = fig.add_subplot(111)
    if nonposval is not None:
        y = np.where(y <= 0, nonposval, y)

    if ms is None:
        ms = correct_marker_size(fmt)

    l, = ax.plot(x, y, fmt, ms=ms, mew=mew, **kwargs)
    # find the error colour
    if ecolor is None:
        ecolor = l.get_mfc()
        if ecolor == 'none':
            ecolor = l.get_mec()
    if nonposval is not None:
        lo[lo <= 0] = nonposval
        hi[hi <= 0] = nonposval

    if 'lw' in kwargs and elw is None:
        elw = kwargs['lw']
    col = ax.vlines(x, lo, hi, color=ecolor, lw=elw, label='__nolabel__')

    if xerrs is not None:
        xerrs = np.array(xerrs)
        if xerrs.ndim > 1:
            lo = xerrs[0]
            hi = xerrs[1]
        else:
            lo = x - xerrs
            hi = x + xerrs
        col2 = ax.hlines(y, lo, hi, color=ecolor, lw=elw, label='__nolabel__')

    if zorder is not None:
        col.set_zorder(zorder)
        l.set_zorder(zorder)
        if xerrs is not None:
            col2.set_zorder(zorder)

    return ax

def test_distplot(n=100):
    a = [np.random.randn(n) for i in range(10)]
    x = range(len(a))
    ax = distplot(x,a, showoutliers=1)
    ax = distplot(x,a, color='r')
    ax = distplot(x,a, label='points', color='b', showmean=1)
    ax.legend()



def dhist(xvals, yvals, xbins=20, ybins=20, ax=None, c='b', fmt='.', ms=1,
          label=None, loc='right,bottom', xhistmax=None, yhistmax=None,
          histlw=1, xtop=0.2, ytop=0.2, chist=None, **kwargs):
    """ Given two set of values, plot two histograms and the
    distribution.

    xvals,yvals are the two properties to plot.  xbins, ybins give the
    number of bins or the bin edges. c is the color.
    """

    if chist is None:
        chist = c
    if ax is None:
        ax = pl.gca()

    loc = [l.strip().lower() for l in loc.split(',')]

    if ms is None:
        ms = correct_marker_size(fmt)

    ax.plot(xvals, yvals, fmt, color=c, ms=ms, label=label, **kwargs)
    x0,x1,y0,y1 = ax.axis()

    if np.__version__ < '1.5':
        x,xbins = np.histogram(xvals, bins=xbins, new=True)
        y,ybins = np.histogram(yvals, bins=ybins, new=True)
    else:
        x,xbins = np.histogram(xvals, bins=xbins)
        y,ybins = np.histogram(yvals, bins=ybins)

    b = np.repeat(xbins, 2)
    X = np.concatenate([[0], np.repeat(x,2), [0]])
    Xmax = xhistmax or X.max()
    X = xtop * X / Xmax
    if 'top' in loc:
        X = 1 - X
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    ax.plot(b, X, color=chist, transform=trans, lw=histlw)

    b = np.repeat(ybins, 2)
    Y = np.concatenate([[0], np.repeat(y,2), [0]])
    Ymax = yhistmax or Y.max()
    Y = ytop * Y / Ymax
    if 'right' in loc:
        Y = 1 - Y
    trans = mtransforms.blended_transform_factory(ax.transAxes, ax.transData)
    ax.plot(Y, b, color=chist, transform=trans, lw=histlw)

    ax.set_xlim(xbins[0], xbins[-1])
    ax.set_ylim(ybins[0], ybins[-1])

    return ax, dict(x=x, y=y, xbinedges=xbins, ybinedges=ybins)

def histo(a, fmt='b', bins=10, ax=None, lw=2, log=False, **kwargs):
    """ Plot a histogram, without all the unnecessary stuff
    matplotlib's hist() function does."""

    if ax is None:
        pl.figure()
        ax = pl.gca()

    vals,bins = np.histogram(np.asarray(a).ravel(), bins=bins)
    if log:
        vals = np.where(vals > 0, np.log10(vals), vals)
    b = np.repeat(bins, 2)
    V = np.concatenate([[0], np.repeat(vals,2), [0]])
    ax.plot(b, V, fmt, lw=lw, **kwargs)
    if pl.isinteractive():
        pl.show()
    return vals,bins
