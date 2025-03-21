# Label Generator

This Python script generates custom labels with dynamic data from a CSV or Excel file. The labels are arranged on US Letter size paper (8.5" x 11") in a 3x10 grid (30 labels per page).

## Features

- Generate labels with customizable dimensions and spacing
- Read data from CSV or Excel files
- Generate QR codes based on input data
- Support for colored label backgrounds
- Automatic pagination for large datasets
- Customizable layout and formatting

## Requirements

- Python 3.12 or higher
- Dependencies listed in `requirements.txt`

## Installation

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Preparing Your Data

Create a CSV or Excel file with three columns:
1. AISLE (number)
2. AMBIENT (alphanumeric)
3. COLOR (color name)

Example CSV format:
```
aisle,ambient,color
1,C140,green
2,B220,blue
3,A110,red
```

Available colors: red, green, blue, yellow, orange, purple, pink, gray, lightgray, white

### Running the Script

Run the script using Python:

```bash
python label_generator.py
```

When prompted:
1. Enter the path to your CSV or Excel file
2. Enter the output PDF filename (or press Enter to use the default "labels.pdf")

### Label Layout

Each label is divided into three sections in a 1:2:1 ratio:

1. Left section: Displays "AISLE" header with the aisle value below
2. Middle section: Displays "AMBIENT" header with the ambient value below, with background color based on the color value
3. Right section: Displays an up arrow (↑) and a QR code containing "aisle_ambient"

### Customization

You can customize the label layout by modifying the configuration parameters in the `__init__()` function at the top of the file:

```python
config = {
    'label_width': 2.625 * inch,
    'label_height': 1 * inch,
    'columns': 3,
    'rows': 10,
    'h_gap': 0.125 * inch,
    'v_gap': 0.0 * inch,
    'top_margin': 0.5 * inch,
    'left_margin': 0.3 * inch
}
```

## Sample Data

A sample data file (`sample_data.csv`) is included for testing purposes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
