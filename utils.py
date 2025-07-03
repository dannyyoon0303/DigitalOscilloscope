import numpy as np
import redpitaya_scpi as scpi 
import time
import plotly.graph_objects as go

# Red Pitaya configuration
IP = '192.168.3.2'
rp = scpi.scpi(IP)

# Acquisition constants
DEC = 1
DLY = 8192
LEV = 0.01
BASE_RATE = 125_000_000  # 125 MS/s
fs = BASE_RATE / DEC
TOTAL_SAMPLES = 16384
decimation_values = [
    1, 2, 4, 8, 16, 32, 64, 128, 256, 512,
    1024, 2048, 4096, 8192, 16384, 32768, 65536
]
decimation_options = [
    {
        'label': f"{(d / 125_000_000) * 16384 * 1000:.4f} ms",
        'value': d
    }
    for d in decimation_values
]


def acquire_data(decimation, delay, level, trigger_channel, trigger_edge):
    fs = BASE_RATE / decimation
    rp.tx_txt('ACQ:RST')
    rp.tx_txt(f'ACQ:DEC {decimation}')
    rp.tx_txt('ACQ:AVG OFF')
    rp.tx_txt(f'ACQ:TRIG:LEV {level}')
    rp.tx_txt(f'ACQ:TRIG:DLY {delay}')

    rp.tx_txt('ACQ:START')
    time.sleep(0.1)
    if trigger_edge == 'NOW':
        trigger_cmd = f'ACQ:TRIG {trigger_edge}'
    else:  trigger_cmd = f'ACQ:TRIG {trigger_channel}_{trigger_edge}'
    rp.tx_txt(trigger_cmd)
    #rp.tx_txt('ACQ: TRIG NOW')
    #rp.tx_txt('ACQ:TRIG CH2_PE')

    while True:
        rp.tx_txt('ACQ:TRIG:STAT?')
        if rp.rx_txt().strip() == 'TD':
            break

    start = time.time()
    while True:
        rp.tx_txt('ACQ:TRIG:FILL?')
        result = rp.rx_txt().strip()
        if result == '1' or time.time() - start > 2.0:
            break
        time.sleep(0.01)

    rp.tx_txt('ACQ:SOUR1:DATA?')
    data1 = np.array(list(map(float, rp.rx_txt().strip('{}\n\r').replace('  ', '').split(','))))

    rp.tx_txt('ACQ:SOUR2:DATA?')
    data2 = np.array(list(map(float, rp.rx_txt().strip('{}\n\r').replace('  ', '').split(','))))

    dt = 1 / fs
    time_axis = np.arange(len(data1)) * dt * 1000
    print(time_axis)
    t_trigger = (8192 - delay) * dt * 1000  # in ms
    return time_axis, data1, data2, t_trigger

def DMA(decimation, delay, level, trigger_channel, trigger_edge, factor):
    fs = 125000000/decimation
    rp.tx_txt('ACQ:RST')
    DATA_SIZE = 1024*16*factor          # ((1024 * 1024 * 128) / 2)        ## for 128 MB ##
    READ_DATA_SIZE = 1024 * 16*factor     # (1024 * 256)                     ## for 128 MB ##
    delay+=DATA_SIZE/2
    print(f'delay is {delay} samples')
    # Get Memory region
    start_address = int(rp.txrx_txt('ACQ:AXI:START?'))
    print(f'start address: {start_address}')
    size = int(rp.txrx_txt('ACQ:AXI:SIZE?'))
    print(f'size of the memory: {size}')
    start_address2 = round(start_address + size/2)
    #start_address2 = round(start_address + DATA_SIZE)
    # Set decimation
    rp.tx_txt(f"ACQ:AXI:DEC {decimation}")

    # Set units
    rp.tx_txt('ACQ:AXI:DATA:Units VOLTS')

    # Set trigger delay for both channels
    rp.tx_txt(f"ACQ:AXI:SOUR1:Trig:Dly {delay}")
    rp.tx_txt(f"ACQ:AXI:SOUR2:Trig:Dly {delay}")

    # Set-up the Channel 1 and channel 2 buffers to each work with half the available memory space.
    rp.tx_txt(f"ACQ:AXI:SOUR1:SET:Buffer {start_address},{size/2}")
    rp.tx_txt(f"ACQ:AXI:SOUR2:SET:Buffer {start_address2},{size/2}")

    # Enable DMA
    rp.tx_txt('ACQ:AXI:SOUR1:ENable ON')
    rp.tx_txt('ACQ:AXI:SOUR2:ENable ON')
    print('Enable CHA and CHB\n')

    # Specify the acquisition trigger
    rp.tx_txt(f"ACQ:TRig:LEV {level}")

    ## ACQUISITION

    rp.tx_txt('ACQ:START')
    #time.sleep(0.01)
    if trigger_edge == 'NOW':
        trigger_cmd = f'ACQ:TRIG {trigger_edge}'
    else:  trigger_cmd = f'ACQ:TRIG {trigger_channel}_{trigger_edge}'

    rp.tx_txt(trigger_cmd)

    #rp.tx_txt('ACQ:TRig CH1_PE')

    print("Waiting for trigger\n")

    # Wait for trigger
    while 1:
        rp.tx_txt("ACQ:TRig:STAT?")
        if rp.rx_txt() == 'TD':
            print("Triggered")
            time.sleep(1)
            break

    # wait for fill adc buffer
    while 1:
        rp.tx_txt('ACQ:AXI:SOUR1:TRig:FILL?')
        if rp.rx_txt() == '1':
            print('DMA buffer full\n')
            break
    time.sleep(0.01)

    # Stop Acquisition
    rp.tx_txt('ACQ:STOP')

    ## Get write pointer at trigger location
    posChA = int(rp.txrx_txt('ACQ:AXI:SOUR1:Trig:Pos?'))
    posChB = int(rp.txrx_txt('ACQ:AXI:SOUR2:Trig:Pos?'))
    start_address = int(rp.txrx_txt('ACQ:AXI:START?'))
    print(start_address, posChA, posChB)

    offset = DATA_SIZE - delay 
    print(f'offset is {offset}')
    start_indexA = (posChA-offset)%DATA_SIZE
    start_indexB = (posChB-offset)%DATA_SIZE
    print(start_indexA, start_indexB)

    if offset > posChA: 
        rp.tx_txt(f"ACQ:AXI:SOUR1:DATA:Start:N? {start_indexA},{READ_DATA_SIZE-posChA}")
        part1A = rp.rx_txt()
        rp.tx_txt(f"ACQ:AXI:SOUR1:DATA:Start:N? {0},{posChA}")
        part2A = rp.rx_txt()
        signal_str = part1A.strip('{}\n\r') + ',' + part2A.strip('{}\n\r')
    else: 
        rp.tx_txt(f"ACQ:AXI:SOUR1:DATA:Start:N? {start_indexA},{READ_DATA_SIZE}")
        signal_str = rp.rx_txt()
    
    if offset > posChB: 
        rp.tx_txt(f"ACQ:AXI:SOUR2:DATA:Start:N? {start_indexB},{READ_DATA_SIZE-posChB}")
        part1B = rp.rx_txt()
        rp.tx_txt(f"ACQ:AXI:SOUR2:DATA:Start:N? {0},{posChB}")
        part2B = rp.rx_txt()
        signal_str2 = part1B.strip('{}\n\r') + ',' + part2B.strip('{}\n\r')
    else: 
        rp.tx_txt(f"ACQ:AXI:SOUR2:DATA:Start:N? {start_indexB},{READ_DATA_SIZE}")
        signal_str2 = rp.rx_txt()

    ## Read & plot

    '''rp.tx_txt(f"ACQ:AXI:SOUR1:DATA:Start:N? {start_indexA},{READ_DATA_SIZE}")
    signal_str = rp.rx_txt()
    rp.tx_txt(f"ACQ:AXI:SOUR2:DATA:Start:N? {start_indexB},{READ_DATA_SIZE}")
    signal_str2 = rp.rx_txt()'''

    print("Data Acquired\n")

    buff1 = list(map(float, signal_str.strip('{}\n\r').replace("  ", "").split(',')))
    buff2 = list(map(float, signal_str2.strip('{}\n\r').replace("  ", "").split(',')))

    dt = 1 / fs
    time_axis = np.arange(len(buff1)) * dt * 1000
    t_trigger = offset * dt * 1000  # in ms

    #t_trigger = 0
    return time_axis, buff1, buff2, t_trigger
