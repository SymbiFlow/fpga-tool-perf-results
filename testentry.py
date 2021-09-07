from collections import defaultdict
import re

class Clk:
    actual: float
    hold_violation: float
    met: bool
    requested: float
    setup_violation: float

class Resources:
    bram: int
    carry: int
    dff: int
    glb: int
    iob: int
    lut: int
    pll: int

class Runtime:
    bitstream: 'float | None'
    checkpoint: 'float | None'
    fasm: 'float | None'
    fasm2bels: 'float | None'
    link_design: 'float | None'
    optimization: 'float | None'
    overhead: 'float | None'
    packing: 'float | None'
    phys_opt_deing: 'float | None'
    placement: 'float | None'
    prepare: 'float | None'
    repots: 'float | None'
    routing: 'float | None'
    synthesis: 'float | None'
    total: 'float | None'

class TestEntry:
    maxfreq: 'dict[str, Clk]'
    maximum_memory_use: float
    resources: Resources
    runtime: Runtime
    wirelength: 'int | None'

def get_configs(json_data: dict):
    zipped = zip(json_data['results']['board'], json_data['results']['toolchain'])
    for board, toolchain_dict in zipped:
        toolchain, _ = next(iter(toolchain_dict.items()))
        yield board, toolchain

def null_generator():
    while True:
        yield None

def get_entries(json_data: dict):
    results = json_data['results']

    def make_clks(clkdef: 'dict | float'):
        clks = {}
        if type(clkdef) is dict:
            for clkname, clkvals in clkdef.items():
                clk = Clk()
                for k, v in clkvals.items():
                    setattr(clk, k, v)
                clks[clkname] = clk
        elif type(clkdef) is float:
            clk = Clk()
            clk.actual = clkdef
            clk.hold_violation = 0.0
            clk.met = False
            clk.requested = 0.0
            clk.setup_violation = 0.0
            clks['clk'] = clk
        else:
            raise Exception('Wrong type for clock definition')
        return clks
    
    def make_runtime(runtimedef: dict):
        runtime = Runtime()
        for k, v in runtimedef.items():
            k = k.replace(' ', '_')
            setattr(runtime, k, v)
        return runtime
    
    def make_resources(resourcesdef: dict):
        resources = Resources()
        for k, v in resourcesdef.items():
            k = k.lower()
            if v is None:
                v = 'null'
            setattr(resources, k, v)
        return resources
    
    wirelength = results.get('wirelength')
    if not wirelength:
        wirelength = null_generator()

    zipped = zip(
        results['board'],
        results['toolchain'],
        results['max_freq'],
        results['maximum_memory_use'],
        results['resources'],
        results['runtime'],
        wirelength
    )
    for board, toolchain_dict, max_freq, max_mem_use, resources, runtime, \
            wirelength in zipped:
        toolchain, _ = next(iter(toolchain_dict.items()))
        
        # Some platforms are cursed and the tests return just a single float
        # instead of a dict
        clk_config = max_freq
        entry = TestEntry()
        entry.maximum_memory_use =\
            max_mem_use if max_mem_use is not None else 'null'
        entry.wirelength = wirelength if wirelength is not None else 'null'
        entry.maxfreq = make_clks(clk_config)
        entry.runtime = make_runtime(runtime)
        entry.resources = make_resources(resources)

        yield board, toolchain, entry