import m5
from m5.objects import *
from m5.stats import periodicStatDump
from m5.util import addToPath
addToPath('../')

# Import the SimObjects we will be using in our configuration
from common import SimpleOpts

# Create the system
def createSystem(options):
    system = System()

    # Set the clock frequency
    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = '3GHz'
    system.clk_domain.voltage_domain = VoltageDomain()

    # Set the memory mode
    system.mem_mode = 'timing'
    system.mem_ranges = [AddrRange('8GB')]

    # Create an X86 CPU
    system.cpu = X86TimingSimpleCPU()

    # Create L1 caches
    system.cpu.icache = L1ICache(options)
    system.cpu.dcache = L1DCache(options)

    # Create an L2 cache
    system.l2cache = L2Cache(options)

    # Connect the caches
    system.cpu.icache_port = system.l2cache.cpu_side
    system.cpu.dcache_port = system.l2cache.cpu_side

    # Create a memory bus
    system.membus = SystemXBar()

    # Connect the L2 cache to the memory bus
    system.l2cache.mem_side = system.membus.slave

    # Create a memory controller and connect it to the memory bus
    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.master

    # Connect the system ports
    system.system_port = system.membus.slave

    return system

# Configure the cache hierarchy
class L1Cache(Cache):
    assoc = 8
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 16
    tgts_per_mshr = 20

class L1ICache(L1Cache):
    size = '32kB'

class L1DCache(L1Cache):
    size = '32kB'

class L2Cache(Cache):
    size = '256kB'
    assoc = 16
    tag_latency = 10
    data_latency = 10
    response_latency = 10
    mshrs = 20
    tgts_per_mshr = 12

# Simulation configurations
configs = [
    {"name": "Baseline", "l2_size": "256kB", "l2_assoc": 16, "block_size": 64},
    {"name": "Increased L2", "l2_size": "1MB", "l2_assoc": 16, "block_size": 64},
    {"name": "Higher Assoc.", "l2_size": "256kB", "l2_assoc": 32, "block_size": 64},
    {"name": "Larger Blocks", "l2_size": "256kB", "l2_assoc": 16, "block_size": 128},
]

# Run simulations and write results
with open('output.txt', 'w') as f:
    f.write("# Experimental Results | Cache Hit Rates | Configuration | L1 I-Cache | L1 D-Cache | L2 Cache\n")

    for config in configs:
        # Set up the options
        options = SimpleOpts()
        options.l2_size = config["l2_size"]
        options.l2_assoc = config["l2_assoc"]
        options.cacheline_size = config["block_size"]

        # Create the system
        system = createSystem(options)

        # Create a process to run on the CPU
        process = Process()
        process.cmd = ['Documents/MSCS531/gem5/hello/bin/x86/linux/hello']
        system.cpu.workload = process
        system.cpu.createThreads()

        # Instantiate the system and begin execution
        root = Root(full_system=False, system=system)
        m5.instantiate()

        # Run the simulation
        print(f"Beginning simulation for {config['name']} configuration!")
        exit_event = m5.simulate()

        # Collect and write stats
        l1i_hits = system.cpu.icache.overall_hits
        l1i_accesses = system.cpu.icache.overall_accesses
        l1d_hits = system.cpu.dcache.overall_hits
        l1d_accesses = system.cpu.dcache.overall_accesses
        l2_hits = system.l2cache.overall_hits
        l2_accesses = system.l2cache.overall_accesses

        l1i_hit_rate = l1i_hits / l1i_accesses * 100 if l1i_accesses > 0 else 0
        l1d_hit_rate = l1d_hits / l1d_accesses * 100 if l1d_accesses > 0 else 0
        l2_hit_rate = l2_hits / l2_accesses * 100 if l2_accesses > 0 else 0

        f.write(f"{config['name']} | {l1i_hit_rate:.1f}% | {l1d_hit_rate:.1f}% | {l2_hit_rate:.1f}%\n")

        print(f"Simulation for {config['name']} configuration complete.")

print("All simulations complete. Results written to output.txt")