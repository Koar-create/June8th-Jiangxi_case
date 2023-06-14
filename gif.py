import imageio, glob, os
       
dirpath = 'D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_wrfout (scheme 1, terrain contrast)'
dim1s, dim2s, dim3s = [ 'd01',  'd02'  ,         ],  \
                      [    '',  'nan, ',         ],  \
                      ['RAIN',  'RAINC', 'RAINNC']
'''
↑ code unneeded to change
-----------------------------
code that need modification ↓
'''
dim1 = dim1s[0] # 0 is d01,             1 is d02.
dim2 = dim2s[0] # 0 is blue_background, 1 is nan_operation.
dim3 = dim3s[0] # 0 is rainc+rainnc,    1 is rainc,             2 is rainnc.
dirpath = dirpath
'''
code that need modification ↑
-----------------------------
↓ code unneeded to change
'''
if dim2 == '':
    if dim3 == 'RAIN':
        picpath = os.path.join(dirpath, dim1)
    else:
        picpath = os.path.join(dirpath, dim1, dim3)
else:
    if dim3 == 'RAIN':
        picpath = os.path.join(dirpath, dim2 + dim1)
    else:
        picpath = os.path.join(dirpath, dim2 + dim1, dim3)
# picpath = "D:\\Repositories\\June11th-Jiangxi_case_figures\\fig_era5\\" for era5
savepath = os.path.join(dirpath, 'Scheme 1, ' + dim3.lower() + '24h, ' + dim2 + dim1) if dim2 == 'nan, ' else \
           os.path.join(dirpath, 'Scheme 1, ' + dim3.lower() + '24h, ' + dim1)  # or savepath = dirpath + 'tp'
if dirpath[-2:] == 't)' or dirpath[-1] == 'c':
    if dim2 == '':
        picpath = os.path.join(dirpath, dim1)
    elif dim2 == 'nan, ':
        picpath = os.path.join(dirpath, dim2 + dim1)
    savepath = os.path.join(dirpath, 'Scheme 1, ' + 'rain24h, ' + dim2 + dim1) if dim2 == 'nan, ' else \
           os.path.join(dirpath, 'Scheme 1, ' + 'rain24h, ' + dim1)

print(os.path.join(picpath, "rain24h_*"))  # print paths of the directory where pictures are
im_paths = glob.glob(os.path.join(picpath, "rain24h_*"))  # obtain all images' paths, or im_paths = glob.glob(picpath + "tp_*")
print(im_paths)  # print grasped paths
frames = [imageio.imread(i) for i in im_paths]  # read all images
imageio.mimsave(savepath + ".gif", frames, fps=10)
imageio.mimsave(savepath + ".mp4", frames, fps=10, macro_block_size=None, codec="libx264", quality=10)
