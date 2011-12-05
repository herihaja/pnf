import matplotlib.pyplot as plt

def graph(request):
    plt.plot([1,2,3,4], [1,4,9,16], 'ro')
    plt.axis([0, 6, 0, 20])

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    fig.set_size_inches(8.,16.)
    plt.savefig('matplotlib-1.png', dpi=72, bbox_inches='tight', pad_inches=0.3)
    plt.clf()
    