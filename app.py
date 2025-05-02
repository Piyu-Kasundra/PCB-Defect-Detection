import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image
import tempfile
from datetime import datetime
import io
from ultralytics import YOLO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image as ReportImage
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
import base64
import time

# Set page configuration
st.set_page_config(
    page_title="PCB Defect Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# PCB-inspired dark theme CSS
st.markdown("""
<style>
    /* Global Styles with PCB-inspired dark theme */
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    .main-header {
        font-size: 2.8rem;
        background: linear-gradient(90deg, #00ff9d, #00b377);
        -webkit-background-clip: text;
        text-align: center;
        margin-bottom: 1.5rem;
        font-weight: 800;
        text-shadow: 0px 0px 10px rgba(0, 255, 157, 0.3);
    }
    
    .sub-header {
        font-size: 1.8rem;
        color: #00cc7a;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #00cc7a;
        padding-bottom: 0.5rem;
        font-weight: 600;
    }
    

    
    /* Text and Highlight Styles */
    .info-text {
        font-size: 1.05rem;
        color: #c0c0c0;
        line-height: 1.6;
    }
    
    .highlight {
        background-color: #2a2a2a;
        padding: 1rem;
        border-radius: 10px;
        border-left: 3px solid #00cc7a;
        margin: 1rem 0;
    }
    
    
    .metric-card h4 {
        font-size: 1.2rem;
        font-weight: 600;
        color: #c0c0c0;
        text-transform: capitalize;
    }
    
    /* Messages */
    .success-message {
        color: #00cc7a;
        font-weight: bold;
        padding: 10px;
        background-color: rgba(0, 204, 122, 0.1);
        border-radius: 5px;
        border-left: 3px solid #00cc7a;
    }
    
    .error-message {
        color: #ff5252;
        font-weight: bold;
        padding: 10px;
        background-color: rgba(255, 82, 82, 0.1);
        border-radius: 5px;
        border-left: 3px solid #ff5252;
    }
    
    /* Buttons - PCB-inspired buttons */
    .stButton button {
        background: linear-gradient(90deg, #006644, #00cc7a);
        color: white;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.6rem 1.2rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 10px rgba(0, 204, 122, 0.2);
    }
    
    .stButton button:hover {
        background: linear-gradient(90deg, #00cc7a, #006644);
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3), 0 0 15px rgba(0, 204, 122, 0.4);
        transform: translateY(-2px);
    }
    
    /* Download Button */
    .download-btn {
        display: inline-block;
        background: linear-gradient(90deg, #00994d, #00cc7a);
        color: white;
        font-weight: bold;
        padding: 12px 20px;
        border-radius: 8px;
        text-decoration: none;
        text-align: center;
        margin-top: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2), 0 0 10px rgba(0, 204, 122, 0.2);
        transition: all 0.3s ease;
    }
    
    .download-btn:hover {
        box-shadow: 0 6px 10px rgba(0, 0, 0, 0.3), 0 0 15px rgba(0, 204, 122, 0.4);
        transform: translateY(-2px);
    }
    
    # /* Progress Bar - PCB trace-like */
    # .progress-bar-container {
    #     width: 100%;
    #     background-color: #2a2a2a;
    #     border-radius: 10px;
    #     margin-bottom: 15px;
    #     overflow: hidden;
    #     box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3);
    #     border: 1px solid #333;
    # }
    
    .progress-bar {
        height: 20px;
        border-radius: 10px;
        text-align: center;
        line-height: 20px;
        color: white;
        font-weight: 600;
        transition: width 0.5s ease;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #333;
        color: #888;
        font-size: 0.9rem;
        background-color: #1a1a1a;
        padding: 15px;
        border-radius: 10px;
    }
    
    /* File Uploader - PCB slot-like */
    .css-1upf8sy {
        border: 2px dashed #00cc7a;
        border-radius: 10px;
        padding: 20px;
        background-color: rgba(0, 204, 122, 0.05);
    }
    
    /* Image Display */
    .stImage img {
        border-radius: 10px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        border: 1px solid #333;
    }
    
    /* Table Styling - PCB circuit board style */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        border: 1px solid #333;
    }
    
    .dataframe thead {
        background: linear-gradient(90deg, #006644, #00cc7a);
        color: white;
    }
    
    .dataframe tbody tr:nth-child(even) {
        background-color: #2a2a2a;
    }
    
    .dataframe tbody tr:nth-child(odd) {
        background-color: #242424;
    }
    
    /* Sidebar - Circuit board pattern */
    .css-1d391kg, .css-163ttbj, .css-1wrcr25 {
        background-color: #1a1a1a;
        background-image: 
            linear-gradient(rgba(0, 204, 122, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 204, 122, 0.1) 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    /* Adjust text colors for better readability */
    label, p, .stMarkdown, .stText {
        color: #e0e0e0 !important;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #00cc7a !important;
    }
    
    /* Make links PCB green */
    a {
        color: #00ff9d !important;
    }
    
    /* Override default Streamlit elements */
    .stSelectbox label, .stSlider label {
        color: #e0e0e0 !important;
    }
    
    .stTextInput > div > div {
        background-color: #2a2a2a !important;
        color: #e0e0e0 !important;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1a1a1a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00cc7a;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00994d;
    }
</style>
""", unsafe_allow_html=True)

# Function to load the YOLO model
@st.cache_resource
def load_model(model_path="model.pt"):
    """Load the YOLO model and cache it to prevent reloading on each interaction"""
    try:
        model = YOLO(model_path)
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Function to perform prediction
def predict(model, image):
    """Run prediction on the image using the loaded model"""
    try:
        results = model(image)
        return results
    except Exception as e:
        st.error(f"Error during prediction: {e}")
        return None

# Function to visualize results
def visualize_results(results, image):
    """Draw bounding boxes and labels on the image"""
    try:
        # Convert PIL image to numpy array if needed
        if isinstance(image, Image.Image):
            img = np.array(image)
        else:
            img = image.copy()
        
        # Define colors for different defect types - PCB-inspired colors
        color_map = {
            'mouse_bite': (255, 50, 50),      # Red
            'spur': (0, 204, 122),            # PCB Green
            'missing_hole': (66, 135, 245),   # Blue
            'short': (255, 204, 0),           # Yellow
            'open_circuit': (204, 51, 204),   # Magenta
            'spurious_copper': (102, 204, 204) # Teal
        }
        
        # Plot results on the image
        for result in results:
            boxes = result.boxes
            
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                # Get class and confidence
                cls = int(box.cls[0])
                conf = float(box.conf[0])

                # Get class name
                class_name = result.names[cls]
                
                # Get color for this defect type
                color = color_map.get(class_name, (0, 204, 122))  # Default to PCB green if not in map
                
                # Convert BGR to RGB if needed
                if len(img.shape) == 3 and img.shape[2] == 3:
                    color = (color[2], color[1], color[0])  # Convert RGB to BGR for OpenCV
                
                # Draw bounding box
                cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
                
                # Draw background for text
                text_size = cv2.getTextSize(f"{class_name}: {conf:.2f}", cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(img, (x1, y1 - 20), (x1 + text_size[0], y1), color, -1)
                
                # Add label
                cv2.putText(img, f"{class_name}: {conf:.2f}", (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return img
    except Exception as e:
        st.error(f"Error visualizing results: {e}")
        return image

# Function to create PDF report
def create_pdf_report(image, results):
    """Generate a PDF report with detection results"""
    try:
        # Create a BytesIO object for the PDF
        pdf_buffer = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Add title with custom style
        title_style = styles["Heading1"]
        title_style.alignment = 1  # Center alignment
        title = Paragraph("PCB Defect Detection Report", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Add date and time
        date_style = styles["Normal"]
        date_style.alignment = 1  # Center alignment
        date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_paragraph = Paragraph(f"Report generated on: {date_time}", date_style)
        elements.append(date_paragraph)
        elements.append(Spacer(1, 0.5*inch))
        
        # Add detection results
        if results:
            # Count defects by type
            defect_counts = {}
            defect_data = []
            
            for result in results:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    x1, y1, x2, y2 = [int(coord) for coord in box.xyxy[0]]
                    
                    class_name = result.names[cls]
                    if class_name in defect_counts:
                        defect_counts[class_name] += 1
                    else:
                        defect_counts[class_name] = 1
                    
                    defect_data.append([
                        class_name,
                        f"{conf:.2f}",
                        f"({x1}, {y1}), ({x2}, {y2})"
                    ])
            
            # Add summary section
            summary_title = Paragraph("Defect Summary", styles["Heading2"])
            elements.append(summary_title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Create summary table
            summary_data = [["Defect Type", "Count"]]
            for defect_type, count in defect_counts.items():
                summary_data.append([defect_type, str(count)])
            
            if len(summary_data) > 1:
                summary_table = Table(summary_data, colWidths=[3*inch, 3*inch])
                summary_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(summary_table)
                elements.append(Spacer(1, 0.4*inch))
            
            # Add detailed results section
            details_title = Paragraph("Detailed Defects", styles["Heading2"])
            elements.append(details_title)
            elements.append(Spacer(1, 0.2*inch))
            
            # Create detailed table
            data = [["Defect Type", "Confidence", "Location"]]
            data.extend(defect_data)
            
            if len(data) > 1:
                table = Table(data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(table)
            else:
                no_defects = Paragraph("No defects detected.", styles["Normal"])
                elements.append(no_defects)
            
            # Add conclusion
            elements.append(Spacer(1, 0.4*inch))
            conclusion_style = styles["Normal"]
            total_defects = sum(defect_counts.values())
            conclusion_text = f"A total of {total_defects} defect{'s' if total_defects != 1 else ''} were detected in the PCB image."
            conclusion = Paragraph(conclusion_text, conclusion_style)
            elements.append(conclusion)
        else:
            no_results = Paragraph("No detection results available.", styles["Normal"])
            elements.append(no_results)
        
        # Add footer
        elements.append(Spacer(1, 0.5*inch))
        footer_style = styles["Normal"]
        footer_style.alignment = 1  # Center alignment
        footer_style.fontSize = 8
        footer = Paragraph("PCB Defect Detection System - Generated Report", footer_style)
        elements.append(footer)
        
        # Build PDF
        doc.build(elements)
        
        # Save to a temporary file for download
        pdf_buffer.seek(0)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(pdf_buffer.read())
            return tmp_file.name
            
    except Exception as e:
        st.error(f"Error generating PDF report: {e}")
        return None

# Function to get binary file data for download
def get_binary_file_downloader_html(bin_file, file_label='File'):
    """Create a download link for the generated PDF"""
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        bin_str = base64.b64encode(data).decode()
        href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(file_label)}" class="download-btn">Download {file_label}</a>'
        return href
    except Exception as e:
        st.error(f"Error creating download link: {e}")
        return None

# Function to display defect metrics
def display_defect_metrics(defect_counts):
    """Display visual metrics for defect counts"""
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; font-weight: 600; margin-bottom: 20px;">Defect Distribution</h3>', unsafe_allow_html=True)
    
    # Calculate total defects for percentage calculation
    total_defects = sum(defect_counts.values())
    
    # Create a row of metrics
    cols = st.columns(len(defect_counts) if len(defect_counts) > 0 else 1)
    
    if len(defect_counts) > 0:   
        for i, (defect_type, count) in enumerate(defect_counts.items()):
            percentage = (count / total_defects) * 100
            
            # Determine color based on defect type - PCB-inspired colors
            color_map = {
                'mouse_bite': 'linear-gradient(135deg, #ff5050, #cc0000)',
                'spur': 'linear-gradient(135deg, #00cc7a, #006644)',
                'missing_hole': 'linear-gradient(135deg, #4287f5, #1c56b3)',
                'short': 'linear-gradient(135deg, #ffcc00, #cc9900)',
                'open_circuit': 'linear-gradient(135deg, #cc33cc, #990099)',
                'spurious_copper': 'linear-gradient(135deg, #66cccc, #339999)'
            }
            color = color_map.get(defect_type, 'linear-gradient(135deg, #00cc7a, #006644)')
            
            with cols[i]:
                st.markdown(f'<div class="metric-card">', unsafe_allow_html=True)
                st.markdown(f'<h4>{defect_type.replace("_", " ").title()}</h4>', unsafe_allow_html=True)
                st.markdown(f'<h2>{count}</h2>', unsafe_allow_html=True)
                
                # Add progress bar
                st.markdown(
                    f'<div class="progress-bar-container">'
                    f'<div class="progress-bar" style="width: {percentage}%; background: {color};">'
                    f'{percentage:.1f}%'
                    f'</div></div>',
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        with cols[0]:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.markdown('<h4>No Defects</h4>', unsafe_allow_html=True)
            st.markdown('<h2>0</h2>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main Streamlit app
def main():
    # Header with logo
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<h1 class="main-header">PCB Defect Detection</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; margin-top: -15px; color: #888;">Advanced AI-powered PCB inspection</p>', unsafe_allow_html=True)
    
    # Sidebar for model loading and information
    with st.sidebar:
        st.markdown('<h3 style="color: #00cc7a; border-bottom: 2px solid #00cc7a; padding-bottom: 8px;">Model Information</h3>', unsafe_allow_html=True)
        
        
        # Load model
        with st.spinner("Loading model..."):
            model = load_model()
        
        if model is None:
            st.markdown('<p class="error-message">❌ Failed to load model. Please check if the model file exists.</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="success-message">✅ Model loaded successfully!</p>', unsafe_allow_html=True)
            st.markdown('<p><b>Model:</b> YOLO11m</p>', unsafe_allow_html=True)
            st.markdown('<p><b>Type:</b> Object Detection</p>', unsafe_allow_html=True)
            st.markdown('<p><b>Status:</b> Ready</p>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # About section
        st.markdown('<h3 style="color: #00cc7a; border-bottom: 2px solid #00cc7a; padding-bottom: 8px;">About</h3>', unsafe_allow_html=True)
        st.markdown("""
        This application uses AI to detect defects in Printed Circuit Boards (PCBs) with high accuracy and real-time performance.
        
        <div class="highlight">
        <strong>🔍 Defect types detected:</strong>
        <ul style="padding-left: 20px;">
            <li>🔴 Mouse Bite - Eroded copper near traces</li>
            <li>🟢 Spur - Unwanted copper extension</li>
            <li>🔵 Missing Hole - Absence of expected hole</li>
            <li>🟡 Short - Unintended connection between traces</li>
            <li>🟣 Open Circuit - Break in trace connectivity</li>
            <li>🔷 Spurious Copper - Extra copper deposits</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Main content area
    st.markdown('<h2 class="sub-header">Upload PCB Image</h2>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a PCB image file", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Create columns for original image
        st.markdown('<h2 class="sub-header">Original Image</h2>', unsafe_allow_html=True)
        
        # Read image
        image = Image.open(uploaded_file).convert("RGB")
        
        # Display original image
        st.image(image, caption="Uploaded PCB Image", use_column_width=True)
        
        # Add a button to perform detection
        detect_col1, detect_col2, detect_col3 = st.columns([1, 2, 1])
        with detect_col2:
            detect_btn = st.button("🔍 Detect Defects", key="detect_btn")
        
        if detect_btn:
            # Create a progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Update progress
            status_text.text("⚙️ Loading model...")
            progress_bar.progress(10)
            time.sleep(0.5)
            
            # Check if model is loaded
            if model is None:
                st.error("Model is not loaded. Please check the model file.")
                return
            
            # Update progress
            status_text.text("🔄 Processing image...")
            progress_bar.progress(30)
            time.sleep(0.5)
            
            # Perform prediction
            results = predict(model, image)
            
            # Update progress
            status_text.text("🧠 Analyzing defects...")
            progress_bar.progress(60)
            time.sleep(0.5)
            
            if results:
                # Visualize results
                vis_img = visualize_results(results, image)
                
                # Update progress
                status_text.text("📊 Generating results...")
                progress_bar.progress(90)
                time.sleep(0.5)
                
                # Complete progress
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                time.sleep(0.5)
                
                # Clear progress indicators
                status_text.empty()
                
                # Display results
                st.markdown('<h2 class="sub-header">Detection Results</h2>', unsafe_allow_html=True)
                st.image(vis_img, caption="PCB with detected defects", use_column_width=True)
                
                # Extract and display detection details
                defect_data = []
                defect_counts = {}
                
                for result in results:
                    for box in result.boxes:
                        cls = int(box.cls[0])
                        conf = float(box.conf[0])
                        class_name = result.names[cls]
                        
                        # Count defects by type
                        if class_name in defect_counts:
                            defect_counts[class_name] += 1
                        else:
                            defect_counts[class_name] = 1
                        
                        defect_data.append({
                            "Type": class_name.replace("_", " ").title(),
                            "Confidence": f"{conf:.2f}",
                            "Coordinates": f"({int(box.xyxy[0][0])}, {int(box.xyxy[0][1])}) to ({int(box.xyxy[0][2])}, {int(box.xyxy[0][3])})"
                        })
                
                if defect_data:
                    # Display defect metrics
                    display_defect_metrics(defect_counts)
                    
                    # Display detailed table
                    st.markdown('<h2 class="sub-header">Detailed Defects</h2>', unsafe_allow_html=True)
                    st.table(defect_data)
                else:
                    st.success("✓ No defects detected in the image. The PCB appears to be in good condition.")
                
                # Generate PDF report
                with st.spinner("Generating PDF report..."):
                    try:
                        pdf_path = create_pdf_report(image, results)
                        
                        # Provide download link if PDF was generated successfully
                        if pdf_path:
                            st.markdown('<h2 class="sub-header">Download Report</h2>', unsafe_allow_html=True)
                            download_link = get_binary_file_downloader_html(pdf_path, 'pcb_defect_report.pdf')
                            if download_link:
                                st.markdown(download_link, unsafe_allow_html=True)
                            else:
                                st.error("Failed to create download link.")
                        else:
                            st.error("Failed to generate PDF report.")
                    except Exception as e:
                        st.error(f"Error in PDF generation process: {e}")
            else:
                # Clear progress indicators
                progress_bar.progress(100)
                status_text.empty()
                st.error("Failed to perform detection. Please try with a different image.")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">PCB Defect Detection System © 2025 | Powered by YOLO & Streamlit</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()

# from ultralytics import YOLO
# model = YOLO("yolo11m.pt")
# model.train(data= "/LAB/PCB_defect_SGP/pcb_defect_dataset/data.yaml",
#             epochs=100,workers=4, batch=16)
# model.save('model.pt')