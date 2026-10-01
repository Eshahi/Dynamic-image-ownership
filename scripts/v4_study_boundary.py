"""Model-free orchestration boundaries; never substitutes source for suspect features."""
import time


def prepare_marked(source_rgb,source_vector,embed,save,read,feature,record):
    """Keep returned failure pixels; fresh features come only from saved/reopened RGB."""
    started=time.perf_counter()
    pixels,report=embed(source_rgb,semantic_features=source_vector,strict=False)
    record(report,time.perf_counter()-started)
    save(pixels)
    observed=read()
    vector=feature(observed)
    return observed,vector
