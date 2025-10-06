#!/usr/bin/env python3

from cmk.agent_based.v2.render import (
    percent,
)

from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    get_value_store,
    check_levels,
    Result,
    State,
    Service,
)

from cmk.plugins.lib.temperature import check_temperature, TempParamDict

import json

def parse_rocm_smi(string_table):
    parsed = {}
    data = json.loads(string_table[0][0])
    
    for gpu_key, gpu_info in data.items():
        if gpu_key.startswith('card'):
            gpu_id = int(gpu_key.replace('card', ''))
            parsed[gpu_id] = {
                'name': gpu_info.get('Device Name', 'Unnamed').replace(' ', '_'),
                'gpu_util': float(gpu_info.get('GPU use (%)', '0.0')),
                'mem_util': float(gpu_info.get('GPU Memory Allocated (VRAM%)', '0.0')),
                'temperature': float(gpu_info.get('Temperature (Sensor junction) (C)', '0.0')),
                'power_draw': float(gpu_info.get('Current Socket Graphics Package Power (W)', '0.0')),
                'current_memory_usage': float(gpu_info.get('GPU Memory Allocated (VRAM%)', '0.0')),
                'num_processes': int(gpu_info.get('num_processes', '0')),
                'sclk_clock_level': gpu_info.get('sclk_clock_level', 'N/A'),
                'performance_level': gpu_info.get('performance_level', 'N/A'),
                'pci_bus': gpu_info.get('pci_bus', 'N/A'),
            }
    # Handle system section for PIDs
    system_info = data.get('system', {})
    for key, value in system_info.items():
        if key.startswith("PID"):
            parts = value.split(",")
            if len(parts) >= 5:
                gpu_index = parts[4].strip()
                if gpu_index.isdigit():
                    gpu_id = int(gpu_index)
                    if gpu_id in parsed:
                        parsed[gpu_id]['num_processes'] = int(parsed[gpu_id]['num_processes']) + 1
                    else:
                        parsed[gpu_id] = {
                            'num_processes': 1,
                            'name': 'Unnamed',
                            'gpu_util': 0.0,
                            'mem_util': 0.0,
                            'temperature': 0.0,
                            'power_draw': 0.0,
                            'current_memory_usage': 0.0,
                            'sclk_clock_level': 'N/A',
                            'performance_level': 'N/A',
                            'pci_bus': 'N/A',
                        }
    return parsed

agent_section_rocm_smi = AgentSection(
    name="rocm_smi",
    parse_function=parse_rocm_smi,
)

def discover_rocm_smi_metrics(section) -> DiscoveryResult:
    for gpu_id, data in section.items():
        yield Service(item=f'GPU{gpu_id}')

def check_rocm_smi_gpuutil(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id in section:
        yield from check_levels(
            section[gpu_id]['gpu_util'],
            metric_name='gpu_utilization',
            levels_upper=("fixed", (90.0, 100.0)),
            label=f"{section[gpu_id]['name']} utilization",
            render_func=percent,
        )

check_plugin_rocm_smi_gpuutil = CheckPlugin(
    name="rocm_smi_gpuutil",
    service_name="GPU %s Utilization",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_metrics,
    check_function=check_rocm_smi_gpuutil,
)

def check_rocm_smi_memory(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id in section:
        yield from check_levels(
            section[gpu_id]['mem_util'],
            metric_name='memory_utilization',
            levels_upper=("fixed", (95.0, 99.0)),
            label=f"{section[gpu_id]['name']} memory utilization",
            render_func=percent,
        )

check_plugin_rocm_smi_memory_util = CheckPlugin(
    name="rocm_smi_memory_util",
    service_name="GPU %s Memory Utilization",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_metrics,
    check_function=check_rocm_smi_memory,
)

def check_rocm_smi_temperature(item: str, params: TempParamDict, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id in section:
        yield from check_temperature(
            section[gpu_id]['temperature'],
            params,
            unique_name=f"rocm_smi.temp.{item}",
            value_store=get_value_store(),
        )

check_plugin_rocm_smi_temperature = CheckPlugin(
    name="rocm_smi_temperature",
    service_name="GPU %s Temperature",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_metrics,
    check_function=check_rocm_smi_temperature,
    check_default_parameters={
        'levels': (80.0, 90.0),
    },
    check_ruleset_name="temperature",
)

def check_rocm_smi_power_draw(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id in section:
        yield from check_levels(
            section[gpu_id]['power_draw'],
            metric_name='power_draw',
            levels_upper=("fixed", (300.0, 350.0)),
            label=f"{section[gpu_id]['name']} power draw",
            render_func=lambda x: "%.2fW" % x,
        )

check_plugin_rocm_smi_power_draw = CheckPlugin(
    name="rocm_smi_power_draw",
    service_name="GPU %s Power Draw",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_metrics,
    check_function=check_rocm_smi_power_draw,
)

def check_rocm_smi_num_processes(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id in section:
        yield from check_levels(
            section[gpu_id]['num_processes'],
            metric_name='num_processes',
            levels_upper=("fixed", (10.0, 20.0)),
            label=f"{section[gpu_id]['name']} running processes",
        )

check_plugin_rocm_smi_num_processes = CheckPlugin(
    name="rocm_smi_num_processes",
    service_name="GPU %s Processes",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_metrics,
    check_function=check_rocm_smi_num_processes,
)

def discover_rocm_smi_sclk_clock_freq(section) -> DiscoveryResult:
    for gpu_id, data in section.items():
        if data.get('sclk_clock_level', 'N/A') != 'N/A':
            yield Service(item=f'GPU{gpu_id}')

def check_rocm_smi_sclk_clock_freq(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id in section:
        sclk_clock_level = section[gpu_id].get('sclk_clock_level', 'N/A')
        if sclk_clock_level != 'N/A':
            yield from check_levels(
                float(sclk_clock_level) * 1000.0,
                metric_name='sclk_clock_freq',
                levels_upper=("fixed", (1500000.0, 2000000.0)),
                label=f"{section[gpu_id]['name']} SCLK frequency",
            )

check_plugin_rocm_smi_sclk_clock_freq = CheckPlugin(
    name="rocm_smi_sclk_clock_freq",
    service_name="GPU %s SCLK Clock Frequency",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_sclk_clock_freq,
    check_function=check_rocm_smi_sclk_clock_freq,
)

def discover_rocm_smi_performance_level(section) -> DiscoveryResult:
    for gpu_id, data in section.items():
        if data.get('performance_level', 'N/A') != 'N/A':
            yield Service(item=f'GPU{gpu_id}')

def check_rocm_smi_performance_level(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id not in section:
        return
    
    data = section[gpu_id]
    performance_level = data.get('performance_level', 'N/A').lower()
    
    if performance_level == 'auto':
        yield Result(state=State.OK, summary=f"{data['name']} performance level is auto")
    else:
        yield Result(state=State.WARN, summary=f"{data['name']} performance level is {performance_level}")

check_plugin_rocm_smi_performance_level = CheckPlugin(
    name="rocm_smi_performance_level",
    service_name="GPU %s Performance Level",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_performance_level,
    check_function=check_rocm_smi_performance_level,
)

def discover_rocm_smi_pci_bus(section) -> DiscoveryResult:
    for gpu_id, data in section.items():
        if data.get('pci_bus', 'N/A') != 'N/A':
            yield Service(item=f'GPU{gpu_id}')

def check_rocm_smi_pci_bus(item: str, section) -> CheckResult:
    gpu_id = int(item.replace('GPU', ''))
    if gpu_id not in section:
        return
    
    data = section[gpu_id]
    pci_bus = data.get('pci_bus', 'N/A')
    
    # Typically, PCI Bus ID is an identifier and not a metric to monitor. 
    # You can display it as a label or handle it as a static information.
    yield Result(state=State.OK, summary=f"{data['name']} PCI Bus ID is {pci_bus}")

check_plugin_rocm_smi_pci_bus = CheckPlugin(
    name="rocm_smi_pci_bus",
    service_name="GPU %s PCI Bus ID",
    sections=["rocm_smi"],
    discovery_function=discover_rocm_smi_pci_bus,
    check_function=check_rocm_smi_pci_bus,
)
