#!/bin/bash

# run all examples from readme
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o test/line.png --date-format "%Y-%m" --emphasize "own issues"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o examples/line_no_markers.png --date-format "%Y-%m" --disable-markers
./csv2graph.py --title "Issues per Month" --data-in-columns -i examples/line_columns.csv -o test/line_columns.png --date-format "%Y-%m" --emphasize "own issues"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o test/line-stacked.png --date-format "%Y-%m" --stacked --smooth
./csv2graph.py --title "Issues per Month" -i examples/line_with_label.csv -o test/line_with_label.png --date-format "%Y-%m" --x-label-separator "-"
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o test/line_annotations.png --date-format "%Y-%m" --annotations examples/annotations.csv
./csv2graph.py --title "Issues per Month" --data-in-columns -i examples/line_columns.csv -o test/line_annotations_columns.png --date-format "%Y-%m" --annotations examples/annotations_columns.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o test/line_annotations_overlap.png --date-format "%Y-%m" --annotations examples/annotations_overlap.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o test/line_annotations_offset.png --date-format "%Y-%m" --annotations examples/annotations_offset.csv
./csv2graph.py --title "Issues per Month" -i examples/line.csv -o test/line-second-y-axis.png --date-format "%Y-%m" --second-y-axis 112
./csv2graph.py --title "Most time consuming issues" -i examples/pie.csv -o test/pie.png --pie

# Compare resulting files with files in examples
all_match=true

for file in test/*.png; do
  filename=$(basename "$file")
  example_file="examples/$filename"

  if [[ ! -f "$example_file" ]]; then
    echo "❌ Missing: $example_file"
    all_match=false
  elif ! cmp -s "$file" "$example_file"; then
    echo "❌ Different: $filename"
    all_match=false
  fi
done

if ! $all_match; then
    echo "❌ Some PNG files differ or are missing."
    exit 1
fi