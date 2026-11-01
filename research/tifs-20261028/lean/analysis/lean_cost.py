"""Cost of a lean F6 study on the RTX 4090 at USD .5512/h. Low and high use the anchored ranges; every input is printed."""
RATE=.5512
r=.52;fix=16 # reader gradient and per-write fixed seconds, from F5 118.7 s/write (Stage 2a), v5 6 s/write
def writers(R1g,R0g,R1u,R0u):
    noise=350*r+fix+100*R1g+50*R0g
    return dict(f5=120,render=125,generic=350*r+fix+3,noise=noise,x0=noise+100*R1u+50*R0u)
W={"low":writers(2.5,.4,.7,.2),"high":writers(6,.8,1.5,.5)}
nat,rowt,qual,load=1.5,1.0,.5,{"low":30,"high":60}
out={}
for c in ("low","high"):
    w=W[c];L=load[c]
    s1_w=4*(w["f5"]*3+w["generic"]*3+w["render"]*2+w["noise"]*3+w["x0"])
    s1=s1_w+52*4*nat+260*rowt+260*qual+15*L
    best=w["generic"] if c=="low" else w["x0"]
    s2_w=12*(2*best+w["f5"]*2)
    s2=s2_w+5*12*12*nat+5*12*13*rowt+5*12*13*qual+10*L
    s3_w=18*(best+w["f5"]*2+6.4)
    s3=s3_w+7*18*12*nat+3600+10*L
    setup={"low":1.5,"high":3.0}[c]*3600;probe=.75*3600;ret=3600
    out[c]=dict(setup=setup,probe=probe,stage1=s1,stage2=s2,stage3=s3,retrieval=ret)
    print(c,{k:round(v) for k,v in w.items()})
    tot=sum(out[c].values())
    for k,v in out[c].items(): print(f"  {k:9s} {v/3600:5.2f} h  USD {v/3600*RATE:5.2f}")
    print(f"  total     {tot/3600:5.2f} h  USD {tot/3600*RATE:5.2f}; stop after stage 1: {(setup+probe+s1+ret)/3600:.2f} h USD {(setup+probe+s1+ret)/3600*RATE:.2f}")
hi=sum(out['high'].values())/3600
print("high plus 25%% on compute: %.1f h USD %.2f"%(hi*1.25,hi*1.25*RATE))
print("USD 20 buys %.1f h"%(20/RATE))
