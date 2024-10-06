# Memory Hierarchy Design Experiments with gem5

## Experimental Setup

### System Configuration
- CPU: X86TimingSimpleCPU @ 3GHz
- Memory: 8GB DDR3_1600_8x8

### Cache Configurations

#### Baseline Configuration
- L1 I-Cache: 32kB, 8-way associative
- L1 D-Cache: 32kB, 8-way associative
- L2 Cache: 256kB, 16-way associative

#### Modified Configurations
1. Increased L2 Size:
   - L2 Cache: 1MB, 16-way associative
2. Higher Associativity:
   - L1 Caches: 16-way associative
   - L2 Cache: 32-way associative
3. Larger Block Size:
   - All caches: 128-byte blocks (default: 64-byte)

### Benchmark Program
We used the SPEC CPU2017 benchmark suite, specifically the 505.mcf_r benchmark, which is memory-intensive and suitable for cache performance analysis.

### gem5 Version and Build Details
- gem5 Version: 24.0.0.1
- Build: X86_MESI_Two_Level