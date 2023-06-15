import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs, cartopy.feature as cfeature
from cartopy.mpl.ticker import (LongitudeFormatter, LatitudeFormatter)

def add_cfeature(ax, linewidth=0.8):
    china_provinces = cfeature.NaturalEarthFeature(
        category='cultural', name='admin_1_states_provinces_lines',
        scale='50m',         facecolor='none',
        edgecolor='black',   linewidth=linewidth)
    ax.add_feature(cfeature.BORDERS, linewidth=linewidth)
    ax.add_feature(cfeature.COASTLINE, linewidth=linewidth)
    # ax.add_feature(cfeature.STATES, linewidth=linewidth)  # ruler
    ax.add_feature(china_provinces)

def add_gridlines(ax, linewidth=1, color='gray', linestyle='--', alpha=0.5, fontsize=18, fontname='Consolas'):
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, x_inline=False, y_inline=False, \
        linewidth=linewidth, color=color, linestyle=linestyle, alpha=alpha)
    gl.xformatter = LongitudeFormatter()
    gl.yformatter = LatitudeFormatter()
    gl.xlabel_style = {'fontsize': fontsize, 'fontname': fontname}
    gl.ylabel_style = {'fontsize': fontsize, 'fontname': fontname}
    gl.top_labels    = False
    gl.bottom_labels = True
    gl.left_labels = True
    gl.right_labels = False
    gl.rotate_labels = False

def add_colorbar(im, ax, cax, fig, title='units: m', levels=np.linspace(0, 1000, 11), extend='max', orientation='vertical', labelsize=18, fontsize=26, fontname='Consolas', x_axis=0.95, y_axis=0.5):
    cbar = plt.colorbar(im, ax=ax, cax=cax, extend=extend, orientation=orientation)
    cbar.ax.tick_params(labelsize=labelsize)
    cbar.set_ticks(levels)
    if orientation == 'vertical':
        fig.text(x_axis, y_axis, title, va='center', ha='center', rotation='vertical', fontdict={'size': fontsize, 'family': fontname})  # cbar title
    elif orientation == 'horizontal':
        fig.text(x_axis, y_axis, title,              ha='center',                      fontdict={'size': fontsize, 'family': fontname})  # cbar title