# ROCm SMI Monitoring Plugin for CheckMK

## Overview
This plugin provides comprehensive monitoring for AMD GPUs using the `rocm-smi` command, integrated with the CheckMK monitoring system.

## Features
- GPU Utilization Tracking
- Memory Utilization Monitoring
- Temperature Tracking
- Power Consumption Monitoring (Draw)
- SCLK Clock Frequency Monitoring
- Performance Level Tracking
- Memory Usage Monitoring
- Number of Active Processes

## Components
- `agent/rocm-smi`: Agent-side script to collect GPU metrics
- `server/rocm-smi`: CheckMK server-side plugin for parsing and monitoring GPU data

## Requirements
- AMD GPU supporting ROCm
- CheckMK Monitoring System
- Python 3.x
- `rocm-smi` command-line tool

## Installation

1. **Login to CheckMK Server**
   
2. **Download the MKP**
   ```bash
   wget https://github.com/gurubert/check_mk_rocm/raw/refs/heads/cmk2.4/rocm_smi-2.0.0.mkp
   ```

3. **Install the Plugin**
   ```bash
   mkp enable $( mkp add rocm_smi-2.0.0.mkp )
   ```

4. **Copy the Agent Plugin**
   ```bash
   scp $OMD_ROOT/local/share/check_mk/agents/plugins/rocm-smi root@host:/usr/lib/check_mk_agent/plugins/rocm-smi
   ssh root@host chmod +x /usr/lib/check_mk_agent/plugins/rocm-smi
   ```

## Metrics Collected
- **GPU Utilization (`gpu_utilization`)**
  - **Description:** Percentage of GPU usage.
  - **Unit:** `%`

- **Memory Utilization (`memory_utilization`)**
  - **Description:** Percentage of VRAM allocated.
  - **Unit:** `%`

- **Temperature (`temperature`)**
  - **Description:** GPU junction temperature.
  - **Unit:** `°C`

- **Power Draw (`power_draw`)**
  - **Description:** Current power consumption in Watts.
  - **Unit:** `W`

- **SCLK Clock Frequency (`sclk_clock_freq`)**
  - **Description:** Current SCLK (System Clock) frequency.
  - **Unit:** `MHz`

- **Performance Level (`performance_level`)**
  - **Description:** Current performance state of the GPU.
  - **Unit:** *None*

- **Memory Used (`memory_used`)**
  - **Description:** Amount of VRAM used.
  - **Unit:** `MB`

- **Number of GPU Processes (`num_processes`)**
  - **Description:** Number of active processes utilizing the GPU.
  - **Unit:** *None*

## License
MIT License - See [LICENSE](LICENSE) file for details.

### **Key Changes:**

- **Title and Overview:** Changed from NVIDIA to AMD and `nvidia-smi` to `rocm-smi`.
- **Features:** Updated to include metrics relevant to `rocm-smi` and removed obsolete ones.
- **Components:** Renamed scripts and paths to reflect `rocm-smi`.
- **Installation:** Updated installation steps to use `rocm-smi` instead of `nvidia-smi`. Adjusted file paths accordingly.
- **Metrics Collected:** Updated the list to include new metrics (`sclk_clock_freq`, `performance_level`) and removed obsolete ones (`fan_speed`, `ecc_errors_single_bit`, `ecc_errors_double_bit`, `power_limit`, `max_memory`).
- **License Section:** Updated to reference the MIT License and included a link to the LICENSE file.
