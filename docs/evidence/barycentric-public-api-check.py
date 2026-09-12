import importlib.util, json, time, warnings, hashlib
import numpy as np
import scipy
from pathlib import Path
started=time.monotonic()
results={"python": __import__("platform").python_version(), "numpy":np.__version__,"scipy_helpers":scipy.__version__,"scope":"Unmodified full historical polyint module and public class API, using wheel-provided SciPy helpers; not a historical full-package build.","cases":[]}
for name in ("parent","patch"):
    path=Path(name+"_polyint.py")
    spec=importlib.util.spec_from_file_location(name,path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    C=mod.BarycentricInterpolator
    record={"source":name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    incremental=C([0.,1.],[0.,1.]); incremental.add_xi([2.],[2.])
    fresh=C([0.,1.,2.],[0.,1.,2.])
    record["linear_after_append"]=float(incremental(.5))
    record["linear_fresh"]=float(fresh(.5))
    deferred=C([0.,1.]); deferred.add_xi([2.]); deferred.set_yi([0.,1.,2.])
    record["deferred_y_after_append"]=float(deferred(.5))
    vector=C([0.,1.],np.array([[0.,1.],[0.,2.]]),axis=1)
    vector.add_xi([2.],np.array([[2.],[4.]]))
    record["axis1_vector_after_append"]=vector([.5]).tolist()
    np.random.seed(0); x=np.cos(np.linspace(0,np.pi,1098))
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        high=C(x, x*x+2*x+1)
        values=high(np.array([-.75,-.1,.1,.75]))
    record["degree1097_finite_weights"]=int(np.isfinite(high.wi).sum())
    record["degree1097_max_polynomial_error"]=float(np.max(np.abs(values-(np.array([-.75,-.1,.1,.75])**2+2*np.array([-.75,-.1,.1,.75])+1)))) if np.all(np.isfinite(values)) else None
    record["warnings"]=sorted({str(w.message) for w in caught})
    results["cases"].append(record)
results["elapsed_seconds"]=time.monotonic()-started
print(json.dumps(results,indent=2,allow_nan=False))
