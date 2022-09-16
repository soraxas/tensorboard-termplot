from argparse import ArgumentParser
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
from pandas._typing import FilePath, ReadCsvBuffer

from termplot.data_source import DataSource, FigureData
from termplot.etc import EmptyEventFileError


class CsvDataSource(DataSource):
    def __init__(self, input_file: Path, args: ArgumentParser):
        super().__init__(input_file, args)
        self.figures = []

        if self.input.is_file():
            if self.input.name.endswith(".csv"):
                # the given 'input' is the actual csv file
                self.figures.append(CsvFigureData(self.input))
        else:  # is a folder
            # the given 'input' is a folder that contains csv file
            for csv_file in self.input.glob("*.csv"):
                self.figures.append(CsvFigureData(csv_file))

        if len(self.figures) == 0:
            raise ValueError(f"Unable to find csv files within '{self.input}'.")

    def __len__(self):
        return len(self.figures)

    def __getitem__(self, item):
        figure_data = self.figures[item]
        figure_data.refresh()
        return figure_data


class CsvFigureData(FigureData):
    def __init__(
        self,
        path: FilePath | ReadCsvBuffer[bytes] | ReadCsvBuffer[str] | StringIO,
        remove_nan: bool = True,
    ):
        # decide whether we should try to clean up nan values
        self.remove_nan = remove_nan
        self.path = path
        self.df = pd.read_csv(path)
        self.refresh()
        if len(self.scalar_names) == 0:
            raise EmptyEventFileError(
                f"Cannot find any scalars within the csv file '{self.path}'"
            )

    def refresh(self):
        pass

    @staticmethod
    def remove_nan_values(x_values, y_values, reference_values):
        try:
            _mapping = np.isfinite(reference_values)
        except TypeError:
            pass
        else:
            x_values = x_values[_mapping]
            y_values = y_values[_mapping]
        return x_values, y_values

    @staticmethod
    def try_obj_to_datetime(series: pd.Series):
        if series.dtype == np.object:
            # try to convert to datetime
            series = pd.to_datetime(series)
        return series

    def get_series(self, *, x: str, y: str):
        y_values = self.df[y]
        if x == "step":
            x_values = np.arange(len(y_values))
        else:
            x_values = self.df[x]
        if self.remove_nan:
            # remove nan values in x
            self.remove_nan_values(x_values, y_values, reference_values=x_values)
            # remove nan values in y
            self.remove_nan_values(x_values, y_values, reference_values=y_values)

        x_values = self.try_obj_to_datetime(x_values)
        y_values = self.try_obj_to_datetime(y_values)

        return x_values, y_values

    @property
    def title(self):
        return self.path

    @property
    def scalar_names(self):
        return list(self.df.columns)

    def __repr__(self):
        return f"{self.__class__.__name__}<path={self.path}|df={self.df}>"
