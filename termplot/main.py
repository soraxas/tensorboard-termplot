import argparse
from typing import Dict

from termplot._version import __version__
from termplot.backend.base_plotter import Plotter
from termplot.data_source import FigureData


def pair_of_num(arg):
    arg = arg.split(",")
    if len(arg) != 2:
        raise ValueError("It must be in the format of a,b (e.g. 30.0,2.2)")
    return tuple(map(float, arg))


def pair_of_int(arg):
    return tuple(map(int, pair_of_num(arg)))


def pair_of_num_assign_pair_of_num(arg):
    arg = arg.split("=")
    if len(arg) != 2:
        raise ValueError("It must be in the format of a,b=c,d (e.g. 30.0,20=30.2,45)")
    return tuple(map(pair_of_num, arg))


def between_zero_and_one(arg):
    arg = float(arg)
    if not (0 <= arg <= 1):
        raise ValueError()
    return arg


parser = argparse.ArgumentParser()
parser.add_argument("folder", metavar="FOLDER", type=str, help="Source folder or file")
parser.add_argument("--version", action="version", version=f"termplot {__version__}")

# plotting generic flags
parser.add_argument(
    "--backend",
    default="plotext",
    help="Set the plotting backend",
    choices=["plotext", "matplotlib", "matplotlib-terminal"],
    type=str,
)
# plotting generic flags
parser.add_argument(
    "--data-source",
    default="tensorboard",
    help="Set the plotting data source",
    choices=["tensorboard", "csv"],
    type=str,
)
parser.add_argument(
    "-m",
    "--matplotlib",
    help="Alias of --backend matplotlib",
    action="store_true",
)
parser.add_argument(
    "--csv",
    help="Alias of --data-source csv",
    action="store_true",
)
parser.add_argument(
    "--plotsize",
    help="Manually set the size of each subplot, e.g., 50,20.",
    metavar="WIDTH,HEIGHT",
    type=pair_of_int,
)
parser.add_argument(
    "-c",
    "--consolidate",
    action="count",
    help="Consolidate based on prefix. If -cc is given, everything will consolidated "
    "regardless of prefix",
)
parser.add_argument(
    "--as-scatter",
    help="Plot as scatter (instead of line plot)",
    action="store_true",
    default=False,
)

# canvas flags
parser.add_argument(
    "--canvas-color",
    type=str,
    help="set the color of the plot canvas " "(the area where the data is plotted)",
)
parser.add_argument(
    "--axes-color",
    type=str,
    help="sets the background color of all the labels surrounding the actual plot, "
    "i.e. the axes, axes labels and ticks, title and legend, if present",
)
parser.add_argument(
    "--ticks-color",
    type=str,
    help="sets the (full-ground) color of the axes ticks and of the grid lines.",
)
parser.add_argument("--grid", action="store_true", help="Show grid.")
parser.add_argument("--colorless", action="store_true", help="Remove color.")
parser.add_argument(
    "-d",
    "--dark-theme",
    action="store_true",
    help="A collection of flags. If set, it is equivalent to setting canvas-color and "
    "axes-color to black, and setting ticks-color to red. Can be overwritten "
    "individually.",
)
parser.add_argument(
    "--no-iter-color",
    action="store_true",
    help="Stop iterating through different colors per plot.",
)
parser.add_argument(
    "--force-label",
    action="store_true",
    help="Force showing label even for plot with one series.",
)

# auto-refresh related flag
parser.add_argument(
    "-f",
    "--follow",
    action="store_true",
    help="Run in a loop to update display periodic.",
)
parser.add_argument(
    "-n",
    "--interval",
    type=float,
    metavar="secs",
    default=5,
    help="seconds to wait between updates",
)

# filtering for stats name
parser.add_argument(
    "-w",
    "--whitelist",
    type=str,
    nargs="+",
    metavar="keyword",
    help="Keyword that the stat must contain for it to be plotted, case sensitive.",
)
parser.add_argument(
    "-b",
    "--blacklist",
    type=str,
    nargs="+",
    metavar="keyword",
    help="Keyword that the stat must not contain for it to be plotted, case sensitive.",
)

# axis flag
parser.add_argument(
    "-x",
    "--xaxis-type",
    default="step",
    help="Set value type to be used for x-axis. Tensorboard only supports 'step' or "
    "'time' as x-axis.",
    # choices=["step", "time"],
    type=str,
)
parser.add_argument(
    "--xlog",
    help="Set the list of subplots to use log scale in x-axis",
    metavar="row,col",
    type=pair_of_int,
    nargs="*",
)
parser.add_argument(
    "--ylog",
    help="Set the list of subplots to use log scale in y-axis",
    metavar="row,col",
    type=pair_of_int,
    nargs="*",
)
parser.add_argument(
    "--xsymlog",
    help="Set the list of subplots to use symlog scale in x-axis",
    metavar="row,col",
    type=pair_of_int,
    nargs="*",
)
parser.add_argument(
    "--ysymlog",
    help="Set the list of subplots to use symlog scale in y-axis",
    metavar="row,col",
    type=pair_of_int,
    nargs="*",
)
parser.add_argument(
    "--xlim",
    help="Set the list of xlim for the specified subplot.",
    metavar="row,col=min,max",
    type=pair_of_num_assign_pair_of_num,
    nargs="+",
)
parser.add_argument(
    "--ylim",
    help="Set the list of ylim for the specified subplot.",
    metavar="row,col=min,max",
    type=pair_of_num_assign_pair_of_num,
    nargs="+",
)

# matplotlib backend specific
parser.add_argument(
    "--as-raw-bytes",
    action="store_true",
    help="Writes the raw image bytes to stdout.",
)
parser.add_argument(
    "-s",
    "--smooth",
    metavar="0-1",
    const=0.05,
    nargs="?",
    type=between_zero_and_one,
    help="A value from 0 to 1 as a smoothing factor.",
)
parser.add_argument(
    "--smooth-poly-order",
    metavar="poly-order",
    default=3,
    type=int,
    help="Polynomial order for the savgol smoothing algorithm.",
)

# plotext backend specific
parser.add_argument(
    "--terminal-width",
    type=int,
    help="Manually set the terminal width.",
)
parser.add_argument(
    "--terminal-height",
    type=int,
    help="Manually set the terminal height.",
)


class EmptyEventFileError(Exception):
    pass


def ensure_odd(x: int, roundup: bool):
    if x % 2 == 0:
        if roundup:
            return x + 1
        else:
            return x - 1
    return x


def apply_smoothing(y_vals, smoothing_factor: float, poly_order: int):
    from scipy.signal import savgol_filter

    # factor controls the window size, with factor 0 being the min and 1
    # being the max
    # window size must be odd, and greater than the polynomial order
    min_win_size = poly_order + 1
    max_win_size = len(y_vals)

    min_win_size = ensure_odd(min_win_size, roundup=True)
    max_win_size = ensure_odd(max_win_size, roundup=False)
    assert min_win_size < max_win_size

    # apply the user-supplied factor
    win_size = int(min_win_size + smoothing_factor * (max_win_size - min_win_size))

    win_size = ensure_odd(win_size, roundup=False)

    return savgol_filter(y_vals, win_size, poly_order)


def _plot_for_one_run(
    plotter: Plotter, figure_data: FigureData, consolidated_stats: Dict, col_num: int
):
    title = f"'{figure_data.title}'"

    if plotter.args.follow:
        title += f" [refresh every {plotter.args.interval}s]"

    colors = plotter.get_colors()

    for i, (prefix, scalar_names) in enumerate(consolidated_stats.items()):
        cur_row, cur_col = i + 1, col_num + 1
        plotter.target_subplot(cur_row, cur_col)
        # setup the title for the current top subplot
        if i == 0:
            plotter.set_title(title)
        ###############################

        for scalar_name, color in zip(scalar_names, colors):
            x_val, y_val = figure_data.get_series(
                x=plotter.args.xaxis_type, y=scalar_name
            )
            if plotter.args.smooth:
                y_val = apply_smoothing(
                    y_val, plotter.args.smooth, plotter.args.smooth_poly_order
                )

            # only label the line if we are consolidating stats. (because otherwise it
            # will always be the only line)
            label = (
                scalar_name
                if (plotter.args.consolidate or plotter.args.force_label)
                else None
            )
            _plot_func = plotter.scatter if plotter.args.as_scatter else plotter.plot
            _plot_func(
                x_val,
                y_val,
                label=label,
                color=color,
            )
            plotter.post_setup(
                xlabel=plotter.args.xaxis_type,
                ylabel=scalar_name,
                cur_row=cur_row,
                cur_col=cur_col,
            )


def main(args):
    # set backend
    if args.backend == "plotext":
        from termplot.backend.terminal_plot import TerminalPlot

        plotter = TerminalPlot(args)
    elif args.backend == "matplotlib":
        from termplot.backend.matplotlib_plot import (
            MatplotlibPlot,
            MatplotlibPlotTerminal,
        )

        if MatplotlibPlotTerminal.get_supported_backend() is not None:
            # automatically use terminal version of matplotlib, if supported.
            plotter = MatplotlibPlotTerminal(args)
        else:
            plotter = MatplotlibPlot(args)
    elif args.backend == "matplotlib-terminal":
        from termplot.backend.matplotlib_plot import MatplotlibPlotTerminal

        plotter = MatplotlibPlotTerminal(args)
    else:
        raise NotImplementedError()
    # set data source
    if args.data_source == "tensorboard":
        from termplot.data_source.tensorboard_source import (
            TensorboardDataSource,
        )

        DataSourceClass = TensorboardDataSource
    elif args.data_source == "csv":
        from termplot.data_source.csv_source import (
            CsvDataSource,
        )

        DataSourceClass = CsvDataSource
    else:
        raise NotImplementedError()

    ##################################################

    while True:
        plotter.clear_current_figure()

        # First loop through and find the maximum number of subplots across all folder
        # first, in case some folders have more subplots than others, will take the max
        max_plots = 1

        data_source = DataSourceClass(args)

        max_plots = max(max_plots, len(data_source.get_consolidated_stats()))

        # create the master plot of all folders
        plotter.create_subplot(max_plots, len(data_source))

        # do the actual plotting
        for i, figure_data in enumerate(data_source):
            # plot the column of subplots for this folder
            _plot_for_one_run(
                plotter, figure_data, data_source.get_consolidated_stats(), i
            )

        plotter.clear_terminal_printed_lines()
        if args.as_raw_bytes:
            plotter.as_image_raw_bytes()
        else:
            plotter.show()
        if not args.follow:
            break
        plotter.sleep()


def run():
    try:
        _args = parser.parse_args()
        # handles alias of options
        if _args.dark_theme:
            # only set values when unset, such that they can be overridden
            if _args.canvas_color is None:
                _args.canvas_color = "black"
            if _args.axes_color is None:
                _args.axes_color = "black"
            if _args.ticks_color is None:
                _args.ticks_color = "white"
        if _args.matplotlib:
            _args.backend = "matplotlib"
        if _args.csv:
            _args.data_source = "csv"
        main(_args)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
