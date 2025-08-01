#!/usr/bin/env python3
# Written by Felix Dreissig (noris network AG) in July 2012.
# Rewritten by Tobias Kaiser (noris network AG) in March 2022.
"""
Reads a CSV file from stdin and converts it to a graph in PDF format, size A4 landscape.
The resulting PDF file is then printed to stdout.
The keys for each dataset have to be date/time values,
i.e. the x-axis of the resulting graph will represent the time.
"""
from __future__ import annotations

import itertools
import sys
import csv
import argparse
from textwrap import TextWrapper
from datetime import datetime
from itertools import cycle
from typing import List, Optional, Tuple

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.artist import getp
from matplotlib.dates import date2num
from scipy.signal import savgol_filter

# Set backend of matplotlib to a non-graphical one
# old doc: https://matplotlib.org/faq/usage_faq.html#what-is-a-backend
# new doc: https://matplotlib.org/stable/users/explain/backends.html
# The current documentation recommends not using `use()` at all,
# because you have to edit this code when caning the backend
# Since we don't need a backend change, we can keep it as it is.
matplotlib.use('pdf')

A4SIZE = (11.69, 8.27)
MARKERS = itertools.cycle(['o', 's', 'D', '^', 'v', '*', 'x', '+', 'p', 'h'])


class IllegalInputError(ValueError):
    pass


def main(args: Optional[List[str]] = None):
    """
    Core function which reads the command line arguments and then triggers input
    parsing and plotting.
    """

    args = parse_arguments(args)

    if args.input:
        with open(args.input) as csvfile:
            raw_data = list(csv.reader(csvfile, dialect=csv.excel, delimiter=','))
    else:
        raw_data = list(csv.reader(sys.stdin, dialect=csv.excel, delimiter=','))

    if args.data_in_columns:
        # transpose "matrix" (https://stackoverflow.com/questions/4937491)
        raw_data = zip(*raw_data)
        # convert sets back to lists
        raw_data = list(map(list, raw_data))

    plt.figure(figsize=A4SIZE)

    if args.pie_chart:
        init_pie(raw_data, args.title)

    else:
        annotation_data = None
        if args.annotations:
            with open(args.annotations) as csvfile:
                annotation_data = list(csv.reader(csvfile, dialect=csv.excel, delimiter=','))
            if not args.data_in_columns:
                # I need the annotation data opposite of the data, which should be drawn
                # transpose "matrix" (https://stackoverflow.com/questions/4937491)
                annotation_data = list(map(list, zip(*annotation_data)))

        init_line(
            raw_data,
            args.date_format,
            args.separator,
            args.smooth,
            args.stacked_data,
            args.title,
            args.start_at_zero,
            args.threshold,
            args.emphasize,
            annotation_data,
            args.second_y_axis,
            args.markers,
        )

    if args.output:
        plt.savefig(args.output)
    else:
        plt.savefig(sys.stdout.buffer)


def parse_arguments(args: Optional[List[str]]) -> argparse.Namespace:
    """Parses the command line arguments and stores them in a Namespace.

    Args:
        args: You can store cmdline argument here for testing

    Returns:
        All arguments in a Namespace
    """

    parser = argparse.ArgumentParser(
        description="generate a PDF graph from a CSV file. More information: "
                    "https://github.com/noris-network/csv2graph/blob/main/README.md"
    )

    parser.add_argument('--smooth', '-S', action='store_true',
                        help="smooth data")
    parser.add_argument('--stacked', '-s', action='store_true', dest='stacked_data',
                        help="Stacks data on top of each other. "
                             "(Don't use with --second-y-axis.)")
    parser.add_argument('--start-at-zero', '-z', action='store_true',
                        dest='start_at_zero',
                        help="force y-axis to start at zero")
    parser.add_argument('--threshold', '-T', type=float, metavar='T', default=None,
                        help='print a threshold in the chart')
    parser.add_argument('--pie-chart', '-p', action='store_true', dest='pie_chart',
                        help="create a pie chart instead of line graph")
    parser.add_argument('--input', '-i', metavar='FILE', default=None,
                        help='read data from this file instead of stdin')
    parser.add_argument('--output', '-o', metavar='FILE', default=None,
                        help='print chart to this file instead of stdout')
    parser.add_argument('--data-in-columns', '-c', action='store_true',
                        dest='data_in_columns',
                        help="data is stored column-wise not row-wise")
    parser.add_argument('--date-format', '-d', metavar='FORMAT', default='%Y-%m',
                        dest='date_format', help='set format for dates (default: %%Y-%%m)')
    parser.add_argument('--x-label-separator', '--separator', metavar='SEPARATOR',
                        default=None, dest='separator',
                        help='set separator between date and label')
    parser.add_argument('--title', '-t', metavar='TITLE', default='',
                        help='set title')
    parser.add_argument('--emphasize', '-e', nargs='+', metavar='LABEL', default=[],
                        help='emphasize Label by printing the line wider')
    parser.add_argument('--annotations', '-a', metavar='FILE', default=None,
                        help='add annotations from file FILE')
    parser.add_argument('--second-y-axis', '--separate-y-axes', '-y',
                        nargs='?', dest='second_y_axis',
                        const='12', default=None, metavar='AXIS',
                        help="Add second y-axis with different scaling. "
                             "Specify the axis for the dataset as a sequence of '1' or '2'. "
                             "(Don't use with --stacked.)")
    parser.add_argument('--disable-markers', '--no-markers', '-m',
                        action='store_false', dest='markers',
                        help="disable markers on datapoints")

    args = parser.parse_args(args)

    if args.second_y_axis is not None and args.stacked_data:
        raise IllegalInputError('Either use --stacked or --second-y-axis')

    return args


def init_pie(data: List[List[str]], title: str):
    """Create a pie chart

    Args:
        data: The data
        title: Title of chart
    """

    # "unzip" data
    labels, sizes = zip(*data)

    plt.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.title(title)


def init_line(
        raw_data: List[List[str]],
        date_format: str,
        separator: str,
        smooth: bool,
        stacked_data: bool,
        title: str,
        start_at_zero: bool,
        threshold: Optional[float],
        emphasize: List[str],
        annotation_data: List[List[str]] | None,
        second_y_axis: str | None,
        markers: bool,
):
    """parse data and trigger plotting

    Args:
        raw_data: unprocessed data
        date_format: format for dates
        separator: separator between date and label
        smooth: if true, data is smoothed
        stacked_data: if true, data is stacked
        title: title of chart
        start_at_zero: if true, y-axis is forced to start at 0
        threshold: if not None, print a threshold line
        emphasize: emphasize these data lines by printing them wider
        annotation_data: annotations
        second_y_axis: which axis to use for wich dataset
        markers: print markers on datapoints
    """
    # check size
    if len(raw_data) < 2:
        raise IllegalInputError('The input has to have at least 2 rows!')
    for row in raw_data:
        if len(row) < 2:
            raise IllegalInputError('The input has to have at least 2 columns!')
        if len(row) != len(raw_data[0]):
            raise IllegalInputError('The size for each row has to be the same!')
    if second_y_axis is not None and len(second_y_axis) != len(raw_data) - 1:
        raise IllegalInputError(
            'You have to specify to which axis the datasets belong, when using --second-y-axis'
        )

    x_label = raw_data[0][0]
    y_labels = [row[0] for row in raw_data[1:]]
    x, ticks = parse_dates(raw_data[0][1:], date_format, separator)
    y = parse_data([row[1:] for row in raw_data[1:]], smooth, stacked_data)

    plot_line(
        x_label,
        y_labels,
        x,
        y,
        stacked_data,
        title,
        start_at_zero,
        threshold,
        emphasize,
        ticks,
        date_format,
        annotation_data,
        second_y_axis,
        markers,
    )


def parse_dates(
        dates: List[str],
        date_fmt: str,
        separator: str,
) -> Tuple[List[np.float64], List[str]]:
    """Convert the dates to matplotlib readable dates

    Args:
        dates: the dates in form of strings (can also contain ticks)
        date_fmt: The date format
        separator: separator between date and label

    Returns:
        data_rows: the converted dates
        ticks: the ticks for x-axis
    """

    ticks = []

    # get explicit labels for x-values if given
    if separator:
        for i, entry in enumerate(dates[:]):
            # find first position where splitting does not produce an error from parsing the date
            date = None
            tick = None
            index = entry.find(separator)
            while index != -1:
                try:
                    date = entry[:index]
                    date = datetime.strptime(date, date_fmt)
                    tick = entry[index + len(separator):]
                    break
                except ValueError:
                    pass
                index = entry.find(separator, index + 1)

            if ticks is None:
                raise ValueError(
                    f"cell '{entry}' can't be split in date and label "
                    f"with separator '{separator}'"
                )

            ticks.append(tick)
            dates[i] = date2num(date)
    else:
        # Convert top row to Python datetime format and then to matplotlib format
        dates = [date2num(datetime.strptime(date, date_fmt)) for date in dates]

    return dates, ticks


def parse_data(
        data: List[List[str]],
        smooth: bool,
        stacked_data: bool,
) -> List[List[float]]:
    """Convert data to numbers.

    Args:
        data: The data in a 2d-List
        smooth: if true, smooth data
        stacked_data: if true, add up data values

    Returns:
        The parsed numbers
    """

    # convert data from str to float
    data = [list(map(float, row)) for row in data]

    if smooth:
        data = smooth_data(data)

    if stacked_data:
        # add up data
        for i in range(1, len(data)):
            for j in range(len(data[i])):
                data[i][j] += data[i - 1][j]

    return data


def smooth_data(rows: List[List[float]], window_length: int = None) -> List[List[float]]:
    """smooth out data using a savgol filter

    https://stackoverflow.com/a/63511395

    Args:
        rows: Data in 2d list
        window_length: window_length for savgol_filter

    Returns:
        smoothed data
    """
    if not window_length:
        window_length = len(rows[0]) // 2 - 1

    for i in range(len(rows)):
        rows[i] = savgol_filter(rows[i], window_length, 2)

    return rows


def render_annotations(annotation_data: List[List[str]], date_format: str) -> None:
    """Render annotations"""
    ax = plt.gca()
    color_iter = cycle(['red', 'blue', 'green', 'magenta'])
    y = plt.ylim()[1]
    wrapper = TextWrapper(width=45, replace_whitespace=False)
    for row in annotation_data:
        row.extend(['0', '0'])  # make sure there are at least 4 elements

        date, text, offset_x, offset_y = row[:4]
        offset_x = float(offset_x if offset_x else 0)
        offset_y = float(offset_y if offset_y else 0)

        x = date2num(datetime.strptime(date, date_format))
        color = next(color_iter)
        ax.axvline(x=x, color=color, linestyle='--')
        text = wrapper.fill(text)
        ax.text(
            x + offset_x,
            y + offset_y,
            text,
            color=color,
            ha='left',
            fontsize=10,
            rotation=10,
            ma='left',
        )


def plot_line(
        x_label: str,
        y_labels: List[str],
        x: List[np.float64],
        y: List[List[float]],
        stacked: bool,
        title: str,
        start_at_zero: bool,
        threshold: Optional[float],
        emphasize: List[str],
        ticks: List[str],
        date_format: str,
        annotation_data: List[List[str]] | None,
        second_y_axis: str | None,
        markers: bool,
) -> None:
    """Plot the data.

    Plots each row of y values using the dates values from x.
    The output is a PDF file, which is printed to stdout.
    The first element of each row is used as description for the legend.
    If 'stacked' is set to 'True', the area between the single graphs will be filled out.

    Args:
        x_label: descriptive label for x-axis
        y_labels: descriptive label for data
        x: Timestamps of data-points
        y: data-points
        stacked: true, if data is stacked
        title: title of the chart
        start_at_zero: if true, y-axis is forced to start at zero
        threshold: if not None, print a threshold line at its value
        emphasize: print the line according to this data wider
        ticks: ticks for x-axis
        date_format: format for dates
        annotation_data: annotations
        second_y_axis: which axis to use for wich dataset
        markers: print markers on datapoints
    """

    if second_y_axis is not None:
        ax1 = plt.gca()
        ax2 = ax1.twinx()
        ax1.tick_params(axis='y', labelcolor='blue')
        ax2.tick_params(axis='y', labelcolor='red')

        for i, dataset in enumerate(y):
            match second_y_axis[i]:
                case '1':
                    axis = ax1
                    color = 'blue'
                case '2':
                    axis = ax2
                    color = 'red'
                case _:
                    raise ValueError(
                        f'--second-y-axis contains illegal character: {second_y_axis[i]}'
                    )

            width = 4 if y_labels[i] in emphasize else 1.5
            marker_args = {}
            if markers:
                marker_args['marker_size'] = 10 if y_labels[i] in emphasize else 4
                marker_args['marker'] = next(MARKERS)
            axis.plot(x, dataset, color=color, label=y_labels[i], lw=width, **marker_args)

        # Make the drawing area only as big as the plotted data requires
        plt.axis('tight')

        if start_at_zero:
            ax1.set_ylim(ymin=0)
            ax2.set_ylim(ymin=0)

        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        # Combine and show the legend on ax1
        plt.legend(
            lines1 + lines2,
            labels1 + labels2,
            loc=0,
            title=x_label,
            prop={'size': 'small'}
        )

    else:
        for i, dataset in enumerate(y):
            label = y_labels[i]
            width = 4 if label in emphasize else 1.5
            marker_args = {}
            if markers:
                marker_args['marker_size'] = 10 if y_labels[i] in emphasize else 4
                marker_args['marker'] = next(MARKERS)

            # plot() returns a list of lines, we unpack the first element by using ','
            line, = plt.plot(x, dataset, label=label, lw=width, **marker_args)

            if stacked:
                if i == 0:
                    plt.fill_between(x, dataset, 0, color=getp(line, 'color'))
                else:
                    plt.fill_between(x, dataset, y[i - 1], color=getp(line, 'color'))

        # Make the drawing area only as big as the plotted data requires
        plt.axis('tight')

        if start_at_zero:
            plt.gca().set_ylim(ymin=0)

        # Add a legend at the best possible location with a font size of 11
        plt.legend(loc=0, title=x_label, prop={'size': 'small'})

    # plot a horizontal Line if requested
    if threshold:
        plt.axhline(y=threshold, color='r', linestyle='-')

    plt.title(title, pad=70)
    # plot_date() for whatever reason didn't automatically use appropriate line styles
    # and colors, so we did a normal plot() and now call xaxis_date() by hand
    plt.gca().xaxis_date()

    # set labels for x-values if given
    if ticks:
        plt.xticks(x, ticks)

    # Rotate the x-axis label so that they won't overlap each other
    plt.gcf().autofmt_xdate()

    if annotation_data:
        render_annotations(annotation_data, date_format)

    plt.tight_layout()


# Program body
if __name__ == '__main__':
    main()
