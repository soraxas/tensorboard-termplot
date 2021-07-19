import argparse
import inspect
import time
from abc import ABCMeta, abstractmethod


class UnsupportedOption(NotImplementedError):
    pass


class Plotter(metaclass=ABCMeta):
    def __init__(self, args: argparse.ArgumentParser):
        self.args = args
        for opt in self.unsupported_options:
            if opt in args and getattr(args, opt) not in [None, False]:
                self.raise_not_supported_option(f"--{opt}")

    @property
    @abstractmethod
    def unsupported_options(self):
        pass

    @abstractmethod
    def plot(self, *args, **kwargs):
        pass

    def post_setup(self, ylabel, cur_row, cur_col):
        def match_subplot(subplots_to_apply):
            # empty list denotes wildcard
            if subplots_to_apply is not None:
                if (
                    len(subplots_to_apply) == 0
                    or (cur_row, cur_col) in subplots_to_apply
                ):
                    return True
            return False

        self.ylabel(ylabel)
        if self.args.canvas_color:
            self.canvas_color()
        if self.args.axes_color:
            self.axes_color()
        if self.args.ticks_color:
            self.ticks_color()
        if self.args.grid:
            self.grid()
        if self.args.plotsize:
            self.plotsize()
        if self.args.colorless:
            self.colorless()
        if match_subplot(self.args.xlog):
            self.xlog()
        if match_subplot(self.args.ylog):
            self.ylog()
        if match_subplot(self.args.xsymlog):
            self.xsymlog()
        if match_subplot(self.args.ysymlog):
            self.ysymlog()

    @abstractmethod
    def ylabel(self, ylabel):
        pass

    def xsymlog(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def ysymlog(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def xlog(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def ylog(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def as_image_raw_bytes(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def canvas_color(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def canvas_color(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def axes_color(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def ticks_color(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def grid(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def plotsize(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    def colorless(self):
        raise UnsupportedOption(inspect.currentframe().f_code.co_name)

    @abstractmethod
    def target_subplot(self, row, col):
        pass

    @abstractmethod
    def create_subplot(self, row, col):
        pass

    @abstractmethod
    def set_title(self, title):
        pass

    @abstractmethod
    def clear_current_figure(self):
        pass

    @abstractmethod
    def clear_terminal_printed_lines(self):
        pass

    @abstractmethod
    def show(self):
        pass

    @property
    @abstractmethod
    def fixed_color_seq(self):
        pass

    @property
    @abstractmethod
    def generator_color_seq(self):
        pass

    def get_colors(self):
        if self.args.no_iter_color:
            return self.fixed_color_seq
        else:
            return self.generator_color_seq

    def sleep(self):
        time.sleep(self.args.interval)

    def raise_not_supported_option(self, option_str):
        print(
            f"ERROR: Plotter backend '{self.__class__.__name__}' does not "
            f"support option '{option_str}'"
        )
        exit(1)
