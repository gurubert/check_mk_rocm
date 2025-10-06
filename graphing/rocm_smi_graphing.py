#!/usr/bin/env python3

from cmk.graphing.v1 import Title, graphs, metrics

UNIT_COUNTER = metrics.Unit(metrics.DecimalNotation(''), metrics.StrictPrecision(2))
UNIT_ELECTRICAL_POWER = metrics.Unit(metrics.DecimalNotation('W'), metrics.AutoPrecision(3))
UNIT_HERTZ = metrics.Unit(metrics.DecimalNotation('Hz'))
UNIT_PERCENTAGE = metrics.Unit(metrics.DecimalNotation('%'))

metric_memory_utilization = metrics.Metric(
    name='memory_utilization',
    title=Title("Memory Utilization"),
    unit=UNIT_PERCENTAGE,
    color=metrics.Color.DARK_YELLOW,
)
metric_num_processes = metrics.Metric(
    name='num_processes',
    title=Title("Number of GPU Processes"),
    unit=UNIT_COUNTER,
    color=metrics.Color.BLUE,
)
metric_power_draw = metrics.Metric(
    name='power_draw',
    title=Title("Power Draw"),
    unit=UNIT_ELECTRICAL_POWER,
    color=metrics.Color.DARK_BLUE,
)
metric_sclk_clock_freq = metrics.Metric(
    name='sclk_clock_freq',
    title=Title("SCLK Clock Frequency"),
    unit=UNIT_HERTZ,
    color=metrics.Color.BLUE,
)

graph_gpu_utilization = graphs.Graph(
    name='gpu_utilization',
    title=Title("GPU Utilization"),
    compound_lines=['gpu_utilization'],
    simple_lines=['memory_utilization'],
)
