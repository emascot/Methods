import time
import datetime
from numpy import prod, ndindex


try:
    get_ipython
except NameError:
    notebook = False
else:
    notebook = True


class ProgressBar(object):
    def __init__(self, N=100, smoothing=0.1, interval=1):
        """Progress bar for an integer number of steps.

        Parameters
        ----------
        N : int
            Number of steps.
        smoothing : float
            Smoothing factor used for estimating time.
            A smaller value averages more steps.
        interval : float
            Time interval in seconds to update display.

        Example
        -------
        >>> bar = ProgressBar(100)
        >>> for i in range(100):
        ...     print(i)
        ...     bar.update()
        ...
        ... del bar

        Methods
        -------
        update
            Increment progress.
        """
        self.value = 0
        self.max = N
        self.alpha = max(0, min(1, smoothing))
        self.interval = interval

        t = time.time()
        self.start_time = t
        self.last_update = t
        self.t0 = t
        self.t = 0.
        
        if notebook:
            from ipywidgets import IntProgress, HTML
            from IPython.display import display
            self.bar = IntProgress(max=N)
            self.html = HTML(value=self._repr_html_())
            display(self.bar, self.html)

            
    def __str__(self):
        # Time remaining
        rem = max(0, self.max - self.value)
        t_rem = datetime.timedelta(seconds=self.t * rem)
        t_avg = datetime.timedelta(seconds=self.t)
        t_tot = datetime.timedelta(seconds=self.t0 - self.start_time)
        
        p = min(20, int(20 * self.value / self.max))
        bar = '[' + p*'=' + (20-p)*' ' + ']'
        return f'{bar} {self.value}/{self.max} {t_rem} {t_avg} {t_tot}'
    
    
    def _repr_html_(self):
        # Time remaining
        rem = max(0., self.max - self.value)
        t_rem = datetime.timedelta(seconds=self.t * rem)
        t_avg = datetime.timedelta(seconds=self.t)
        t_tot = datetime.timedelta(seconds=self.t0 - self.start_time)
        return f"""
            <table>
                <tr>
                    <th>Progress:</th>
                    <td>{self.value}/{self.max}</td>
                </tr>
                <tr>
                    <th>Remaining time:</th>
                    <td>{t_rem}</td></tr>
                <tr>
                    <th>Average time:</th>
                    <td>{t_avg}</td>
                </tr>
                <tr>
                    <th>Total time:</th>
                    <td>{t_tot}</td>
                </tr>
            </table>
        """


    def update(self):
        """Increment progress."""
        self.value += 1

        # Time since last update
        t = time.time()
        t, self.t0 = t - self.t0, t

        # Time per update
        if self.value < 10:
            # Average
            self.t = (t + (self.value-1) * self.t) / self.value
        else:
            # Exponential smoothing
            self.t = self.alpha * t + (1-self.alpha) * self.t
        self.display()


    def display(self):
        if self.t0 - self.last_update > self.interval:
            if notebook:
                self.html.value = self._repr_html_()
                self.bar.value = self.value
                self.last_update = self.t0
            else:
                print(self, flush=True)


    def __del__(self):
        """Close progress bar."""
        if notebook:
            self.bar.close()
            self.html.close()

    close = __del__


def pindex(*shape, smoothing=0.1, interval=1):
    """numpy.ndindex iterator with progress bar.

    Parameters
    ----------
    *shape : ints
        The size of each dimension of the array.
    smoothing : float
        Smoothing factor used for estimating time.
    interval : float
        Time interval in seconds to update display.

    Example
    -------
    >>> for i in pindex(100):
    ...     print(i)
    """
    bar = ProgressBar(prod(shape), smoothing=smoothing, interval=interval)
    for i in ndindex(*shape):
        yield i
        bar.update()
    del bar
