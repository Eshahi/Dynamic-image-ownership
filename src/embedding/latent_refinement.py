"""Bounded frozen-decoder latent refinement, not a scientific worker/approval.

Independent source-MSE projected descent candidate, not REED or GNRI reproduction.
Only owned CPU fixtures may call this without exact learned-model authorization.
No encoder, DDIM, carrier, watermark, detector, model load or package installation.
"""
from dataclasses import dataclass
import time

from .proposed import DiffusersComponents, EmbeddingError, _torch, padded_source
from .checkpointing import CheckpointedComponents
from .inversion import _latent, _real
from .inversion_path import PinnedDDIMPath, module_fingerprint


@dataclass(frozen=True)
class RefinementPolicy:
    iterations: int
    maximum_evaluations: int
    maximum_backtracks: int
    learning_rate: float
    maximum_displacement_l2: float
    latent_penalty: float
    mse_tolerance: float
    maximum_seconds: float

    def __post_init__(self):
        for name,low,high in (("iterations",1,128),("maximum_evaluations",2,1024),
                              ("maximum_backtracks",0,16)):
            if type(getattr(self,name)) is not int or not low<=getattr(self,name)<=high:
                raise EmbeddingError("invalid refinement "+name)
        for name,low,high in (("learning_rate",1e-8,100),("maximum_displacement_l2",1e-8,1000),
                ("latent_penalty",0,1000),("mse_tolerance",0,1),("maximum_seconds",1e-6,1100)):
            _real(getattr(self,name),"refinement "+name,low,high)


@dataclass(frozen=True)
class RefinementResult:
    latent: object
    native_image: object
    status: str
    mse_rgb01: float
    objective: float
    displacement_l2: float
    evaluations: int
    backward_evaluations: int
    actual_decoder_forward_starts: int
    checkpoint_recomputations: int


def refine(backend, source, initial_latent, policy, *, progress, save_state):
    """Fixed normalized-gradient descent, projected L2 trust ball, monotone trials.

    All evaluated latents (including rejected trials) require durable caller saves.
    Normal budget/zero-gradient/line-search stops return explicit diagnostic states,
    never a quality-success claim. Exceptions abort without a false terminal result.
    Runtime bound is cooperative; exact worker must enforce external timeout/VRAM.
    """
    torch=_torch()
    if type(backend) not in (DiffusersComponents,CheckpointedComponents) or type(policy) is not RefinementPolicy:
        raise EmbeddingError("typed fixed components/refinement policy required")
    if not callable(progress) or not callable(save_state):
        raise EmbeddingError("refinement journal and state persistence required")
    padded=padded_source(source,backend.settings.maximum_side)
    _latent(initial_latent,"refinement initial")
    shape=(1,4,padded.shape[-2]//8,padded.shape[-1]//8)
    if (tuple(initial_latent.shape)!=shape or source.device!=initial_latent.device
            or source.device!=backend.condition.device):
        raise EmbeddingError("refinement grid/device mismatch")
    path=PinnedDDIMPath(backend)
    vae=backend.vae
    if not isinstance(vae,torch.nn.Module) or not isinstance(getattr(vae,"decoder",None),torch.nn.Module):
        raise EmbeddingError("fixed VAE with explicit decoder module required")
    binding=module_fingerprint(vae)
    retained=tuple(vae.modules())+tuple(vae.parameters())+tuple(vae.buffers())
    decoder=vae.decoder
    decode_function=getattr(backend._decode,"__func__",None)
    vae_decode_function=getattr(vae.decode,"__func__",None)
    def guard():
        path._validate()
        if (backend.vae is not vae or module_fingerprint(vae)!=binding
                or any(module.training for module in vae.modules())
                or float(vae.config.scaling_factor)!=backend.settings.vae_scale
                or getattr(backend._decode,"__self__",None) is not backend
                or getattr(backend._decode,"__func__",None) is not decode_function
                or getattr(vae.decode,"__self__",None) is not vae
                or getattr(vae.decode,"__func__",None) is not vae_decode_function):
            raise EmbeddingError("frozen decoder identity/method/profile drift")
        for value in tuple(vae.parameters())+tuple(vae.buffers()):
            if (value.device!=source.device or value.requires_grad
                    or (value.is_floating_point() and value.dtype!=torch.float32)):
                raise EmbeddingError("frozen decoder tensor profile drift")
    guard()
    target=source.detach().clone(); initial=initial_latent.detach().clone()
    current=initial.clone(); native_hw=tuple(target.shape[-2:])
    deadline=time.monotonic()+policy.maximum_seconds
    evaluations=backwards=starts=recomputations=0
    mode="forward"

    def emit(row):
        progress(dict(row))
    def check_time():
        if time.monotonic()>=deadline:
            emit({"phase":"refinement_time_limit","evaluations":evaluations})
            raise EmbeddingError("refinement cooperative time limit")
    def started(module,args):
        nonlocal starts,recomputations
        check_time()
        if starts>=2*policy.maximum_evaluations:
            emit({"phase":"decoder_forward_ceiling","actual_decoder_forward_starts":starts})
            raise EmbeddingError("actual decoder forward ceiling exceeded")
        starts+=1
        if mode=="backward":recomputations+=1
        emit({"phase":"decoder_forward_started","context":mode,
              "actual_decoder_forward_starts":starts,"checkpoint_recomputations":recomputations})

    def evaluate(state, *, gradient, role, iteration):
        nonlocal evaluations,mode
        check_time();guard()
        if evaluations>=policy.maximum_evaluations:
            raise EmbeddingError("internal refinement evaluation budget breach")
        evaluations+=1;mode="forward"
        row={"evaluation":evaluations,"iteration":iteration,"role":role}
        emit(dict(row,phase="refinement_evaluation_started",gradient_enabled=gradient))
        check_time();guard()
        with torch.set_grad_enabled(gradient):
            decoded=backend._decode(state.clone()/backend.settings.vae_scale)
            guard()
            if (not isinstance(decoded,torch.Tensor) or tuple(decoded.shape)!=tuple(padded.shape)
                    or decoded.dtype!=torch.float32 or decoded.device!=target.device
                    or not bool(torch.isfinite(decoded).all())):
                raise EmbeddingError("invalid refinement decoder output")
            native=((decoded+1)/2).clamp(0,1)[:,:,:native_hw[0],:native_hw[1]]
            mse=(native-target).square().mean()
            objective=mse+policy.latent_penalty*(state-initial).square().mean()
            if not bool(torch.isfinite(objective)):
                raise EmbeddingError("nonfinite refinement objective")
            metrics={"mse_rgb01":float(mse.detach()),"objective":float(objective.detach()),
                     "displacement_l2":float(torch.linalg.vector_norm((state-initial).detach().double()))}
        save_state(dict(row,phase="refinement_evaluated_state",**metrics),state.detach().clone())
        guard()
        emit(dict(row,phase="refinement_evaluated",**metrics))
        check_time()
        return objective,native,metrics

    handle=decoder.register_forward_pre_hook(started)
    try:
        emit({"phase":"refinement_started","profile":"native-mse-normalized-projected-descent-v1",
              "checkpoint_profile":path.checkpoint_profile,"maximum_evaluations":policy.maximum_evaluations})
        _,image,metrics=evaluate(current,gradient=False,role="initial",iteration=0)
        image=image.detach().clone()
        status="iteration_budget"
        for iteration in range(1,policy.iterations+1):
            if metrics["mse_rgb01"]<=policy.mse_tolerance:
                status="mse_tolerance_met";break
            # Reserve at least one trial before spending on a gradient evaluation.
            if evaluations+2>policy.maximum_evaluations:
                status="evaluation_budget";break
            state=current.detach().clone().requires_grad_(True)
            objective,gradient_image,gradient_metrics=evaluate(state,gradient=True,role="gradient",iteration=iteration)
            # Even a zero-weight latent penalty creates an autograd edge. Do
            # not mistake that edge for a differentiable decoder output.
            if not objective.requires_grad or not gradient_image.requires_grad:
                raise EmbeddingError("detached refinement decoder graph")
            mode="backward";backwards+=1
            emit({"phase":"refinement_backward_started","iteration":iteration,"backward_evaluations":backwards})
            check_time();guard()
            gradient=torch.autograd.grad(objective,state,create_graph=False)[0].detach()
            guard();check_time();mode="forward"
            if not bool(torch.isfinite(gradient).all()):raise EmbeddingError("nonfinite refinement gradient")
            norm=float(torch.linalg.vector_norm(gradient.double()))
            emit({"phase":"refinement_gradient","iteration":iteration,"gradient_l2":norm})
            del state,objective,gradient_image
            if norm<=1e-12:status="zero_gradient";break
            accepted=False
            for backtrack in range(policy.maximum_backtracks+1):
                if evaluations>=policy.maximum_evaluations:break
                trial=current-policy.learning_rate*(.5**backtrack)*gradient/norm
                delta=trial-initial;length=float(torch.linalg.vector_norm(delta.double()))
                if length>policy.maximum_displacement_l2:
                    trial=initial+delta*(policy.maximum_displacement_l2/length)
                _latent(trial,"refinement trial")
                # Mathematical projection is not a bound on the rounded fp32
                # tensor, especially around a nonzero initial latent. Refuse
                # the actual candidate before decoding, retaining the failure.
                displacement=float(torch.linalg.vector_norm((trial-initial).double()))
                if displacement>policy.maximum_displacement_l2:
                    row={"phase":"refinement_projection_refused","iteration":iteration,
                         "backtrack":backtrack,"displacement_l2":displacement,
                         "maximum_displacement_l2":policy.maximum_displacement_l2,
                         "decoder_evaluated":False}
                    save_state(dict(row),trial.detach().clone());guard();check_time()
                    emit(dict(row))
                    raise EmbeddingError("rounded refinement projection exceeds trust radius")
                _,candidate,observed=evaluate(trial,gradient=False,role="trial",iteration=iteration)
                # A grad-enabled reevaluation is not permission to increase the
                # last actually accepted objective if execution paths differ.
                accepted=observed["objective"]<min(gradient_metrics["objective"],metrics["objective"])
                emit({"phase":"refinement_trial","evaluation":evaluations,"iteration":iteration,
                      "backtrack":backtrack,"accepted":accepted,**observed})
                if accepted:
                    current=trial.detach().clone();image=candidate.detach().clone();metrics=observed
                    break
            del gradient
            if not accepted:
                status="evaluation_budget" if evaluations>=policy.maximum_evaluations else "line_search_failed"
                break
        if metrics["mse_rgb01"]<=policy.mse_tolerance:status="mse_tolerance_met"
        guard();check_time()
        row={"phase":"refinement_final_state","status":status,**metrics}
        save_state(dict(row),current.clone());guard();check_time()
        emit(dict(row,phase="refinement_terminated",evaluations=evaluations,backward_evaluations=backwards,
                  actual_decoder_forward_starts=starts,checkpoint_recomputations=recomputations,
                  scientific_acceptance=False,saved_png_quality="NOT_RUN",safety="NOT_RUN"))
        return RefinementResult(current.clone(),image.clone(),status,metrics["mse_rgb01"],metrics["objective"],
                                metrics["displacement_l2"],evaluations,backwards,starts,recomputations)
    finally:
        handle.remove()
        del retained
