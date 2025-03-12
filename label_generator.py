import pandas as pd
import qrcode
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing, Polygon
from reportlab.graphics import renderPDF
from PIL import Image
import io
import os

class LabelGenerator:
    def __init__(self, config=None):
        # Default configuration
        self.config = {
            # US Letter size
            'page_width': 8.5 * inch,
            'page_height': 11 * inch,
            # Label dimensions (1 inch by 2 and 5/8 inches)
            'label_width': 2.625 * inch,
            'label_height': 1 * inch,
            # Layout
            'columns': 3,
            'rows': 10,
            # Margins
            'top_margin': 0.5 * inch,
            'left_margin': 0.19 * inch,  # Adjusted for more precise alignment
            # Gaps
            'h_gap': 0.125 * inch,
            'v_gap': 0.0 * inch,
            # Fonts
            'header_font': 'Helvetica-Bold',
            'header_size': 12,
            'content_font': 'Helvetica-Bold',
            'content_size': 20,
            # Section ratios (left:middle:right)
            'section_ratios': [1, 2, 1]
        }
        
        # Update with user config if provided
        if config:
            self.config.update(config)
        
        # Calculate section widths
        total_ratio = sum(self.config['section_ratios'])
        self.section_widths = [
            ratio / total_ratio * self.config['label_width'] 
            for ratio in self.config['section_ratios']
        ]
    
    def read_data(self, file_path):
        """Read data from CSV or Excel file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format. Please use CSV or Excel.")
    
    def create_qr_code(self, data, size=1.5):
        """Generate QR code image"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Create image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert PIL Image to bytes for ReportLab
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        
        # Return PIL Image object directly
        return img
    
    def draw_up_arrow(self, canvas, x, y, width, height):
        """Draw an up arrow"""
        arrow_width = width * 0.6
        arrow_height = height * 0.3
        
        # Arrow coordinates - flattened list of coordinates for ReportLab
        points = [
            x - arrow_width/2, y,           # bottom left
            x, y + arrow_height,            # top
            x + arrow_width/2, y,           # bottom right
        ]
        
        # Create polygon for arrow
        arrow = Polygon(points)
        arrow.fillColor = colors.black
        
        # Create drawing and add arrow
        drawing = Drawing(width, arrow_height)
        drawing.add(arrow)
        
        # Render drawing on canvas
        renderPDF.draw(drawing, canvas, x - width/2, y)
    
    def get_background_color(self, color_name):
        """Convert color name to ReportLab color object"""
        # Dictionary of common colors
        color_dict = {
            'red': colors.red,
            'green': colors.green,
            'blue': colors.blue,
            'yellow': colors.yellow,
            'orange': colors.orange,
            'purple': colors.purple,
            'pink': colors.pink,
            'gray': colors.gray,
            'lightgray': colors.lightgrey,
            'white': colors.white
        }
        
        # Return color or default to white if not found
        return color_dict.get(color_name.lower(), colors.white)
    
    def draw_label(self, canvas, x, y, data):
        """Draw a single label with the specified data"""
        aisle, ambient, bg_color, qr_value = data
        
        # Get positions
        label_width = self.config['label_width']
        label_height = self.config['label_height']
        
        # Starting positions for each section
        section_start_x = [
            x,
            x + self.section_widths[0],
            x + self.section_widths[0] + self.section_widths[1]
        ]
        
        # Draw a rounded border around the label
        canvas.setStrokeColor(colors.lightgrey)
        canvas.setLineWidth(0.5)
        canvas.roundRect(x, y, label_width, label_height, 10, stroke=1, fill=0)
        
        # 2. Set background color for middle section
        canvas.setFillColor(self.get_background_color(bg_color))
        canvas.roundRect(section_start_x[1], y, self.section_widths[1], label_height, 0, fill=1, stroke=0)
        canvas.setFillColor(colors.black)
        
        # 3. Draw section contents
        # Section 1: Aisle
        canvas.setFont(self.config['header_font'], self.config['header_size'])
        canvas.drawCentredString(
            section_start_x[0] + self.section_widths[0]/2, 
            y + label_height - self.config['header_size'] - 4,
            "AISLE"
        )
        
        canvas.setFont(self.config['content_font'], self.config['content_size'])
        canvas.drawCentredString(
            section_start_x[0] + self.section_widths[0]/2, 
            y + label_height/2 - self.config['content_size']/2,
            str(aisle)
        )
        
        # Section 2: Determine header based on qr_value
        # Default header
        header_text = "AMBIENT"
        
        # Check qr_value to determine appropriate header
        if "STOWAGE" in qr_value:
            header_text = "AMBIENT"
        elif "CHILLER" in qr_value:
            header_text = "CHILLED"
        elif "FROZEN" in qr_value:
            header_text = "FREEZER"
        
        canvas.setFont(self.config['header_font'], self.config['header_size'])
        canvas.drawCentredString(
            section_start_x[1] + self.section_widths[1]/2, 
            y + label_height - self.config['header_size'] - 4,
            header_text
        )
        
        canvas.setFont(self.config['content_font'], self.config['content_size'])
        canvas.drawCentredString(
            section_start_x[1] + self.section_widths[1]/2, 
            y + label_height/2 - self.config['content_size']/2,
            str(ambient)
        )
        
        # Section 3: QR Code and simple up arrow character
        section_center_x = section_start_x[2] + self.section_widths[2]/2
        
        # Draw up arrow character
        canvas.setFont(self.config['content_font'], 14)
        canvas.drawCentredString(
            section_center_x,
            y + label_height - 20,  # Position arrow near the top
            "↑"  # Unicode up arrow character
        )
        
        # Generate and place QR code
        qr_data = f"{qr_value}"
        print(qr_data)
        qr_img = self.create_qr_code(qr_data)
        
        # Calculate QR code size and position
        qr_size = min(self.section_widths[2] * 0.8, label_height * 0.6)  # Slightly smaller to make room for arrow
        qr_x = section_center_x - qr_size/2
        
        # Position QR code centered but with space for arrow above
        qr_y = y + (label_height - qr_size)/2 - 5  # Shift down slightly to make room for arrow
        
        # Save QR code to a temporary file
        temp_qr_file = f"temp_qr_{aisle}_{ambient}.png"
        qr_img.save(temp_qr_file)
        
        # Place QR code on canvas using the file
        canvas.drawImage(
            temp_qr_file, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto'
        )
        
        # Clean up the temporary file
        if os.path.exists(temp_qr_file):
            os.remove(temp_qr_file)
            
    # def draw_rounded_rect(self, canvas, x, y, width, height, radius, fill_color, line_width=1):
    #     """Draw a rounded rectangle on the canvas"""
    #     # Save the graphics state
    #     canvas.saveState()
        
    #     # Set fill color
    #     canvas.setFillColor(fill_color)
        
    #     # Set border color and width
    #     if line_width > 0:
    #         canvas.setStrokeColor(colors.black)
    #         canvas.setLineWidth(line_width)
        
    #     # Create the path for a rounded rectangle
    #     p = canvas.beginPath()
    #     p.moveTo(x + radius, y)
    #     p.lineTo(x + width - radius, y)
    #     p.curveTo(x + width, y, x + width, y, x + width, y + radius)
    #     p.lineTo(x + width, y + height - radius)
    #     p.curveTo(x + width, y + height, x + width, y + height, x + width - radius, y + height)
    #     p.lineTo(x + radius, y + height)
    #     p.curveTo(x, y + height, x, y + height, x, y + height - radius)
    #     p.lineTo(x, y + radius)
    #     p.curveTo(x, y, x, y, x + radius, y)
    #     p.close()
        
    #     # Draw the path
    #     if line_width > 0:
    #         canvas.drawPath(p, stroke=1, fill=1)
    #     else:
    #         canvas.drawPath(p, stroke=0, fill=1)
        
    #     # Restore the graphics state
    #     canvas.restoreState()
    
    def generate_labels(self, data_file, output_pdf):
        """Generate PDF with labels from data file"""
        # Read data
        df = self.read_data(data_file)
        total_labels = len(df)
        
        # Create canvas
        c = canvas.Canvas(output_pdf, pagesize=letter)
        c.setTitle("Generated Labels")
        
        # Get configuration values
        labels_per_page = self.config['columns'] * self.config['rows']
        label_width = self.config['label_width']
        label_height = self.config['label_height']
        left_margin = self.config['left_margin']
        top_margin = self.config['top_margin']
        h_gap = self.config['h_gap']
        v_gap = self.config['v_gap']
        
        # Process each label
        for idx, row in df.iterrows():
            # Calculate page number and position on page
            position_on_page = idx % labels_per_page
            
            # Calculate row and column on current page
            row_num = position_on_page // self.config['columns']
            col_num = position_on_page % self.config['columns']
            
            # If this is a new page, create it
            if position_on_page == 0 and idx > 0:
                c.showPage()
            
            # Calculate label position
            x = left_margin + col_num * (label_width + h_gap)
            y = (self.config['page_height'] - top_margin - 
                 (row_num + 1) * label_height - row_num * v_gap)
            
            # Access columns by name instead of position to avoid deprecation warning
            aisle = row['aisle']
            ambient = row['ambient']
            color = row['color']
            qr_value = row['qr_value']

            # Draw the label
            self.draw_label(c, x, y, [aisle, ambient, color, qr_value])
        
        # Save the PDF
        c.save()
        print(f"Generated {output_pdf} with {total_labels} labels on {(total_labels-1)//labels_per_page + 1} pages")

def main():
    
    # Create label generator
    generator = LabelGenerator()
    
    # Get input and output file paths
    data_file = input("Enter path to CSV or Excel file: ")
    output_pdf = input("Enter output PDF filename (default: labels.pdf): ") or "labels.pdf"
    
    # Generate labels
    generator.generate_labels(data_file, output_pdf)

if __name__ == "__main__":
    main() 