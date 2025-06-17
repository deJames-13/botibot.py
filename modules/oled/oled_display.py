import board
import busio
from adafruit_ssd1306 import SSD1306_I2C
from PIL import Image, ImageDraw, ImageFont
import time


class OLEDDisplay:
    """
    A reusable OLED display controller class for SSD1306-based displays.
    
    This class provides easy control of I2C OLED displays with text rendering,
    graphics drawing, and various display effects.
    """
    
    def __init__(self, width=128, height=64, i2c_address=0x3C):
        """
        Initialize the OLED display.
        
        Args:
            width (int): Display width in pixels (default: 128)
            height (int): Display height in pixels (default: 64)
            i2c_address (int): I2C address of the display (default: 0x3C)
        """
        self.width = width
        self.height = height
        self.i2c_address = i2c_address
        
        # I2C setup
        self.i2c = busio.I2C(board.SCL, board.SDA)
        
        # OLED display setup
        self.display = SSD1306_I2C(width, height, self.i2c, addr=i2c_address)
        
        # Create image buffer
        self.image = Image.new("1", (width, height))
        self.draw = ImageDraw.Draw(self.image)
        
        # Default font
        self.font = ImageFont.load_default()
        
        # Clear display initially
        self.clear()
    
    def clear(self, show=True):
        """
        Clear the display.
        
        Args:
            show (bool): Whether to immediately update the display
        """
        self.display.fill(0)
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)
        if show:
            self.show()
    
    def show(self):
        """Update the physical display with the current image buffer."""
        self.display.image(self.image)
        self.display.show()
    
    def write_text(self, text, x=0, y=0, font=None, fill=255, show=True):
        """
        Write text to the display.
        
        Args:
            text (str): Text to display
            x (int): X coordinate
            y (int): Y coordinate
            font: Font object (uses default if None)
            fill (int): Fill color (255 for white, 0 for black)
            show (bool): Whether to immediately update the display
        """
        if font is None:
            font = self.font
        
        self.draw.text((x, y), text, font=font, fill=fill)
        if show:
            self.show()
    
    def write_multiline(self, lines, x=0, y=0, line_height=10, font=None, fill=255, show=True):
        """
        Write multiple lines of text.
        
        Args:
            lines (list): List of text lines
            x (int): X coordinate for first line
            y (int): Y coordinate for first line
            line_height (int): Height between lines
            font: Font object (uses default if None)
            fill (int): Fill color
            show (bool): Whether to immediately update the display
        """
        if font is None:
            font = self.font
        
        for i, line in enumerate(lines):
            self.draw.text((x, y + i * line_height), str(line), font=font, fill=fill)
        
        if show:
            self.show()
    
    def draw_rectangle(self, x, y, width, height, outline=255, fill=None, show=True):
        """
        Draw a rectangle.
        
        Args:
            x, y (int): Top-left corner coordinates
            width, height (int): Rectangle dimensions
            outline (int): Outline color
            fill (int): Fill color (None for no fill)
            show (bool): Whether to immediately update the display
        """
        self.draw.rectangle((x, y, x + width, y + height), outline=outline, fill=fill)
        if show:
            self.show()
    
    def draw_circle(self, x, y, radius, outline=255, fill=None, show=True):
        """
        Draw a circle.
        
        Args:
            x, y (int): Center coordinates
            radius (int): Circle radius
            outline (int): Outline color
            fill (int): Fill color (None for no fill)
            show (bool): Whether to immediately update the display
        """
        self.draw.ellipse((x - radius, y - radius, x + radius, y + radius), 
                         outline=outline, fill=fill)
        if show:
            self.show()
    
    def draw_line(self, x1, y1, x2, y2, fill=255, width=1, show=True):
        """
        Draw a line.
        
        Args:
            x1, y1 (int): Start coordinates
            x2, y2 (int): End coordinates
            fill (int): Line color
            width (int): Line width
            show (bool): Whether to immediately update the display
        """
        self.draw.line((x1, y1, x2, y2), fill=fill, width=width)
        if show:
            self.show()
    
    def draw_pixel(self, x, y, fill=255, show=True):
        """
        Draw a single pixel.
        
        Args:
            x, y (int): Pixel coordinates
            fill (int): Pixel color
            show (bool): Whether to immediately update the display
        """
        self.draw.point((x, y), fill=fill)
        if show:
            self.show()
    
    def scroll_text(self, text, y=0, delay=0.1, cycles=1, font=None, fill=255):
        """
        Scroll text horizontally across the display.
        
        Args:
            text (str): Text to scroll
            y (int): Y coordinate
            delay (float): Delay between scroll steps
            cycles (int): Number of scroll cycles
            font: Font object
            fill (int): Text color
        """
        if font is None:
            font = self.font
        
        # Get text width
        text_width = self.draw.textlength(text, font=font)
        
        for _ in range(cycles):
            # Scroll from right to left
            for x in range(self.width, -text_width, -2):
                self.clear(show=False)
                self.write_text(text, x, y, font=font, fill=fill, show=True)
                time.sleep(delay)
    
    def blink_text(self, text, x=0, y=0, blinks=3, delay=0.5, font=None, fill=255):
        """
        Blink text on the display.
        
        Args:
            text (str): Text to blink
            x, y (int): Text coordinates
            blinks (int): Number of blinks
            delay (float): Delay between blinks
            font: Font object
            fill (int): Text color
        """
        if font is None:
            font = self.font
        
        for _ in range(blinks):
            # Show text
            self.clear(show=False)
            self.write_text(text, x, y, font=font, fill=fill, show=True)
            time.sleep(delay)
            
            # Clear text
            self.clear(show=True)
            time.sleep(delay)
    
    def display_status(self, title, status_items, show_time=True):
        """
        Display a status screen with title and multiple status items.
        
        Args:
            title (str): Screen title
            status_items (dict): Dictionary of status items {label: value}
            show_time (bool): Whether to show current time
        """
        self.clear(show=False)
        
        # Display title
        self.write_text(title, 0, 0, show=False)
        self.draw_line(0, 10, self.width, 10, show=False)
        
        # Display status items
        y_offset = 15
        for label, value in status_items.items():
            status_text = f"{label}: {value}"
            self.write_text(status_text, 0, y_offset, show=False)
            y_offset += 10
        
        # Display time if requested
        if show_time:
            current_time = time.strftime("%H:%M:%S")
            time_width = self.draw.textlength(current_time, font=self.font)
            self.write_text(current_time, self.width - time_width, self.height - 10, show=False)
        
        self.show()
    
    def progress_bar(self, progress, x=0, y=30, width=100, height=10, show=True):
        """
        Draw a progress bar.
        
        Args:
            progress (float): Progress percentage (0-100)
            x, y (int): Progress bar coordinates
            width, height (int): Progress bar dimensions
            show (bool): Whether to immediately update the display
        """
        # Clamp progress to 0-100
        progress = max(0, min(100, progress))
        
        # Draw outer rectangle
        self.draw_rectangle(x, y, width, height, outline=255, fill=0, show=False)
        
        # Draw filled portion
        fill_width = int((progress / 100) * (width - 2))
        if fill_width > 0:
            self.draw_rectangle(x + 1, y + 1, fill_width, height - 2, 
                              outline=255, fill=255, show=False)
        
        # Draw percentage text
        progress_text = f"{progress:.0f}%"
        text_width = self.draw.textlength(progress_text, font=self.font)
        text_x = x + (width - text_width) // 2
        text_y = y + height + 2
        self.write_text(progress_text, text_x, text_y, show=False)
        
        if show:
            self.show()
    
    def cleanup(self):
        """Clean up resources."""
        self.clear()


# Example usage
if __name__ == "__main__":
    try:
        # Create OLED display controller
        oled = OLEDDisplay(width=128, height=64)
        
        # Basic text display
        oled.write_text("Hello, Pi OLED!", 0, 0)
        time.sleep(2)
        
        # Multi-line text
        lines = ["Line 1", "Line 2", "Line 3"]
        oled.clear(show=False)
        oled.write_multiline(lines, 0, 0, line_height=12)
        time.sleep(2)
        
        # Graphics demo
        oled.clear(show=False)
        oled.draw_rectangle(10, 10, 50, 30, outline=255)
        oled.draw_circle(100, 25, 15, outline=255)
        oled.draw_line(0, 50, 128, 50)
        oled.show()
        time.sleep(2)
        
        # Status display
        status = {
            "CPU": "45%",
            "RAM": "2.1GB",
            "Temp": "42°C"
        }
        oled.display_status("System Status", status)
        time.sleep(3)
        
        # Progress bar demo
        oled.clear(show=False)
        oled.write_text("Loading...", 0, 0, show=False)
        for i in range(0, 101, 10):
            oled.progress_bar(i, 10, 20, 100, 15)
            time.sleep(0.2)
        
        time.sleep(1)
        
        # Scrolling text
        oled.clear()
        oled.scroll_text("This is a scrolling message!", y=25, delay=0.05, cycles=2)
        
        # Blinking text
        oled.blink_text("ALERT!", 40, 25, blinks=5, delay=0.3)
        
    except KeyboardInterrupt:
        print("Demo stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'oled' in locals():
            oled.cleanup()
        print("OLED demo completed")
