#!/bin/bash

set -x

# run all examples from readme
# png
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line.png --date-format "%Y-%m" --emphasize "own issues"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_no_markers.png --date-format "%Y-%m" --disable-markers
./csv2graph.py --title "Issues per Month" --data-in-columns -i examples/line_columns.csv -o examples/line_columns.png --date-format "%Y-%m" --emphasize "own issues"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line-stacked.png --date-format "%Y-%m" --stacked --smooth
./csv2graph.py --title "Issues per Month" -i examples/line_with_label.csv -o examples/line_with_label.png --date-format "%Y-%m" --x-label-separator "-"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_annotations.png --date-format "%Y-%m" --annotations examples/annotations.csv
./csv2graph.py --title "Issues per Month" --data-in-columns -i examples/line_columns.csv -o examples/line_annotations_columns.png --date-format "%Y-%m" --annotations examples/annotations_columns.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_annotations_overlap.png --date-format "%Y-%m" --annotations examples/annotations_overlap.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_annotations_offset.png --date-format "%Y-%m" --annotations examples/annotations_offset.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line-second-y-axis.png --date-format "%Y-%m" --second-y-axis 112
./csv2graph.py --title "Most time consuming issues" -i examples/pie.csv -o examples/pie.png --pie

# pdf
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line.pdf --date-format "%Y-%m" --emphasize "own issues"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_no_markers.pdf --date-format "%Y-%m" --disable-markers
./csv2graph.py --title "Issues per Month" --data-in-columns -i examples/line_columns.csv -o examples/line_columns.pdf --date-format "%Y-%m" --emphasize "own issues"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line-stacked.pdf --date-format "%Y-%m" --stacked --smooth
./csv2graph.py --title "Issues per Month" -i examples/line_with_label.csv -o examples/line_with_label.pdf --date-format "%Y-%m" --x-label-separator "-"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_annotations.pdf --date-format "%Y-%m" --annotations examples/annotations.csv
./csv2graph.py --title "Issues per Month" --data-in-columns -i examples/line_columns.csv -o examples/line_annotations_columns.pdf --date-format "%Y-%m" --annotations examples/annotations_columns.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_annotations_overlap.pdf --date-format "%Y-%m" --annotations examples/annotations_overlap.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_annotations_offset.pdf --date-format "%Y-%m" --annotations examples/annotations_offset.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line-second-y-axis.pdf --date-format "%Y-%m" --second-y-axis 112
./csv2graph.py --title "Most time consuming issues" -i examples/pie.csv -o examples/pie.pdf --pie