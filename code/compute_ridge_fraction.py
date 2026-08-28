import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import gc

IN_FILE = "/mnt/user-data/uploads/IS2-UMDRDA-NH-EASE2-3125m-v01-202207.nc"
OUT_NC = "/home/claude/work/ridge_fraction_derived.nc"
OUT_PNG = "/home/claude/work/ridge_fraction_map.png"

ds_in = nc.Dataset(IN_FILE)

sic = np.ma.filled(ds_in.variables["sea_ice_conc"][0], np.nan).astype("float32")
x = np.array(ds_in.variables["x_proj"][:], dtype="float32")
y = np.array(ds_in.variables["y_proj"][:], dtype="float32")
lat = np.array(ds_in.variables["latitude"][:], dtype="float32")
lon = np.array(ds_in.variables["longitude"][:], dtype="float32")

def ridge_fraction(w_name, d_name):
    W = np.ma.filled(ds_in.variables[w_name][0], np.nan).astype("float32")
    D = np.ma.filled(ds_in.variables[d_name][0], np.nan).astype("float32")
    with np.errstate(invalid="ignore", divide="ignore"):
        frac = W / D
    frac = np.where((D <= 0) | np.isnan(D) | np.isnan(W), np.nan, frac)
    frac = np.clip(frac, 0, 1)
    frac = np.where(sic >= 15, frac, np.nan)
    del W, D
    return frac.astype("float32")

frac60 = ridge_fraction("sail_W_T60", "sail_D_T60")
frac20 = ridge_fraction("sail_W_T20", "sail_D_T20")
ds_in.close()
gc.collect()

print("Ridge fraction (>0.6 m threshold): mean=%.4f median=%.4f n_valid=%d"
      % (np.nanmean(frac60), np.nanmedian(frac60), np.sum(~np.isnan(frac60))))
print("Ridge fraction (>0.2 m threshold): mean=%.4f median=%.4f n_valid=%d"
      % (np.nanmean(frac20), np.nanmedian(frac20), np.sum(~np.isnan(frac20))))

# ---- write a compact derived-variables NetCDF ----
ds_out = nc.Dataset(OUT_NC, "w", format="NETCDF4")
ds_out.createDimension("y", frac60.shape[0])
ds_out.createDimension("x", frac60.shape[1])
ds_out.createDimension("Time", 1)

v = ds_out.createVariable("x_proj", "f4", ("x",), zlib=True); v[:] = x; v.units = "km"
v = ds_out.createVariable("y_proj", "f4", ("y",), zlib=True); v[:] = y; v.units = "km"
v = ds_out.createVariable("latitude", "f4", ("y", "x"), zlib=True); v[:] = lat
v = ds_out.createVariable("longitude", "f4", ("y", "x"), zlib=True); v[:] = lon
v = ds_out.createVariable("sea_ice_conc", "f4", ("y", "x"), zlib=True, fill_value=np.nan); v[:] = sic; v.units = "%"

for varname, data, thresh_cm in [("ridge_fraction_T60", frac60, 60), ("ridge_fraction_T20", frac20, 20)]:
    v = ds_out.createVariable(varname, "f4", ("y", "x"), zlib=True, fill_value=np.nan)
    v[:] = data
    v.long_name = f"Linear (along-track) ridge fraction using {thresh_cm} cm sail-height threshold"
    v.units = "1"
    v.description = (f"sail_W_T{thresh_cm} / sail_D_T{thresh_cm} from the source file, "
                      f"clipped to [0,1], masked where sea_ice_conc < 15%. This is an "
                      f"along-track linear fraction (fraction of ICESat-2 ground-track length "
                      f"within a ridge sail), not a true 2-D areal fraction.")

ds_out.source_file = IN_FILE
ds_out.description = "Derived ridge-fraction variables computed from IS2-UMDRDA monthly gridded product, July 2022."
ds_out.close()
print("Wrote", OUT_NC)

# ---- plot ----
fig, axes = plt.subplots(1, 2, figsize=(13, 6))
cmap = plt.cm.inferno.copy()
cmap.set_bad("#dddddd")

for ax, frac, title in zip(axes, [frac60, frac20],
                             ["Ridge fraction (sail > 0.6 m)", "Ridge fraction (sail > 0.2 m)"]):
    im = ax.pcolormesh(x, y, frac, cmap=cmap, norm=mcolors.Normalize(vmin=0, vmax=0.3), shading="auto")
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.set_xlabel("x_proj (km)")
    ax.set_ylabel("y_proj (km)")
    fig.colorbar(im, ax=ax, label="along-track ridge fraction", shrink=0.75)

fig.suptitle("ICESat-2 UMD-RDA linear ridge fraction, July 2022 (sail_W / sail_D)")
fig.tight_layout()
fig.savefig(OUT_PNG, dpi=150)
print("Wrote", OUT_PNG)
