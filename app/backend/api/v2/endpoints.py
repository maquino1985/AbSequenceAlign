from typing import List
from fastapi import APIRouter, HTTPException

from backend.models.models import NumberingScheme, SequenceInput
from backend.models.models_v2 import AnnotationResult as V2AnnotationResult, Sequence as V2Sequence, Chain as V2Chain, Domain as V2Domain, Region as V2Region, RegionFeature as V2RegionFeature, DomainType
from backend.annotation.AnarciResultProcessor import AnarciResultProcessor
from backend.models.requests_v2 import AnnotationRequestV2


router = APIRouter()


@router.get("/health")
async def health_check_v2():
    return {"status": "healthy"}


@router.post("/annotate", response_model=V2AnnotationResult)
async def annotate_sequences_v2(request: AnnotationRequestV2):
    try:
        # Build input for processor (reuse existing logic)
        input_dict = {}
        for seq in request.sequences:
            chains = seq.get_all_chains()
            if chains:
                input_dict[seq.name] = chains

        processor = AnarciResultProcessor(input_dict, numbering_scheme=request.numbering_scheme.value)

        v2_sequences: List[V2Sequence] = []
        for result in processor.results:
            v2_chains: List[V2Chain] = []
            for chain in result.chains:
                v2_domains: List[V2Domain] = []
                for domain in chain.domains:
                    # Map domain type
                    if getattr(domain, 'domain_type', 'V') == 'C':
                        dtype = DomainType.CONSTANT
                    elif getattr(domain, 'domain_type', 'V') == 'LINKER':
                        dtype = DomainType.LINKER
                    else:
                        dtype = DomainType.VARIABLE

                    # Absolute start/stop for domain
                    dstart = None
                    dstop = None
                    if domain.alignment_details:
                        if dtype == DomainType.LINKER:
                            dstart = domain.alignment_details.get('start')
                            dstop = domain.alignment_details.get('end')
                        else:
                            dstart = domain.alignment_details.get('query_start')
                            dstop = domain.alignment_details.get('query_end')

                    v2_regions: List[V2Region] = []
                    # Regions if present
                    if hasattr(domain, 'regions') and domain.regions:
                        for rname, r in domain.regions.items():
                            # r may be a dataclass-like object or a plain dict
                            if isinstance(r, dict):
                                start = int(r.get('start'))
                                stop = int(r.get('stop'))
                                seq_val = r.get('sequence')
                            else:
                                start = int(r.start)
                                stop = int(r.stop)
                                seq_val = r.sequence
                            features = [V2RegionFeature(kind="sequence", value=seq_val)]
                            v2_regions.append(V2Region(name=rname, start=start, stop=stop, features=features))

                    v2_domains.append(V2Domain(
                        domain_type=dtype,
                        start=dstart,
                        stop=dstop,
                        sequence=domain.sequence,
                        regions=v2_regions,
                        isotype=getattr(domain, 'isotype', None),
                        species=getattr(domain, 'species', None),
                        metadata={}
                    ))

                v2_chains.append(V2Chain(name=chain.name, sequence=chain.sequence, domains=v2_domains))

            v2_sequences.append(V2Sequence(name=result.biologic_name, original_sequence=v2_chains[0].sequence if v2_chains else "", chains=v2_chains))

        return V2AnnotationResult(
            sequences=v2_sequences,
            numbering_scheme=request.numbering_scheme.value,
            total_sequences=len(v2_sequences)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Annotation failed: {e}")


