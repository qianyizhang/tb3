import skrf as rf


def compose(left,right):
    f=rf.Frequency.from_f(left['frequency_hz'],unit='hz')
    networks=[]
    for data in [left,right]:
        n=rf.Network(frequency=f,s=data['s'],z0=data['z0'],s_def=data['wave_definition'])
        n.renormalize(50,s_def='power')
        networks.append(n)
    return (networks[0]**networks[1]).s
