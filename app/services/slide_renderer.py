from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from typing import Tuple, List
from app.agents.planner_agent import SlideLayout, ThemeConfig
from app.utils.logger import logger


class SlideRenderer:
    """
    Service for rendering slides as PNG images.
    
    Current: Simple solid backgrounds with basic text
    UPGRADE_LATER: Add gradient backgrounds, icons, shadows, effects
    """
    
    # Standard slide dimensions (1080p)
    WIDTH = 1920
    HEIGHT = 1080
    
    # Layout constants
    MARGIN = 100
    TITLE_Y_POSITION = 150
    CONTENT_START_Y = 350
    LINE_SPACING = 80
    BULLET_SYMBOL = "•"  # UPGRADE_LATER: Replace with icon images
    
    def __init__(self):
        """Initialize the renderer"""
        self.font_cache = {}
    
    def _get_font(self, font_family: str, size: int) -> ImageFont.FreeTypeFont:
        """
        Get or create a font object with caching.
        
        UPGRADE_LATER: Add support for custom font files
        """
        cache_key = f"{font_family}_{size}"
        
        if cache_key not in self.font_cache:
            try:
                # Try to use system fonts
                # Common font paths for different OS
                font_paths = [
                    f"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
                    f"/System/Library/Fonts/Helvetica.ttc",  # macOS
                    f"C:\\Windows\\Fonts\\arial.ttf",  # Windows
                ]
                
                font = None
                for path in font_paths:
                    try:
                        font = ImageFont.truetype(path, size)
                        break
                    except:
                        continue
                
                if font is None:
                    # Fallback to default
                    logger.warning(f"Could not load font {font_family}, using default")
                    font = ImageFont.load_default()
                
                self.font_cache[cache_key] = font
                
            except Exception as e:
                logger.warning(f"Font loading error: {e}, using default")
                self.font_cache[cache_key] = ImageFont.load_default()
        
        return self.font_cache[cache_key]
    
    def _create_background(self, theme: ThemeConfig) -> Image.Image:
        """
        Create background canvas.
        
        Current: Solid color
        UPGRADE_LATER: Add gradient backgrounds, patterns, images
        """
        # Convert hex color to RGB
        bg_color = self._hex_to_rgb(theme.background_color)
        
        # Create solid color background
        canvas = Image.new('RGB', (self.WIDTH, self.HEIGHT), bg_color)
        
        # UPGRADE_LATER: Add gradient
        # Example upgrade:
        # canvas = self._create_gradient_background(theme.background_color, theme.accent_color)
        
        return canvas
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> List[str]:
        """
        Wrap text to fit within max_width.
        
        Returns list of lines.
        """
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            # Get text width using textbbox
            bbox = font.getbbox(test_line)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def _render_title(
        self,
        draw: ImageDraw.Draw,
        title: str,
        font_size: int,
        theme: ThemeConfig
    ) -> int:
        """
        Render title text.
        
        Returns: Y position where title ends
        
        UPGRADE_LATER: Add text shadows, outlines, effects
        """
        font = self._get_font(theme.font_family, font_size)
        text_color = self._hex_to_rgb(theme.text_color)
        
        # Wrap text if needed
        max_width = self.WIDTH - (2 * self.MARGIN)
        lines = self._wrap_text(title, font, max_width)
        
        y_position = self.TITLE_Y_POSITION
        
        for line in lines:
            # Center the text
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x_position = (self.WIDTH - text_width) // 2
            
            # UPGRADE_LATER: Add shadow effect
            # draw.text((x_position + 3, y_position + 3), line, font=font, fill=(0, 0, 0, 128))
            
            draw.text((x_position, y_position), line, font=font, fill=text_color)
            y_position += font_size + 20
        
        return y_position
    
    def _render_bullet_points(
        self,
        draw: ImageDraw.Draw,
        content: List[str],
        start_y: int,
        font_size: int,
        theme: ThemeConfig
    ):
        """
        Render bullet points.
        
        UPGRADE_LATER: Add icon bullets, custom symbols, indentation
        """
        font = self._get_font(theme.font_family, font_size)
        text_color = self._hex_to_rgb(theme.text_color)
        accent_color = self._hex_to_rgb(theme.accent_color)
        
        y_position = start_y
        bullet_x = self.MARGIN
        text_x = self.MARGIN + 50
        max_text_width = self.WIDTH - text_x - self.MARGIN
        
        for bullet_text in content:
            # Wrap bullet text if needed
            lines = self._wrap_text(bullet_text, font, max_text_width)
            
            for idx, line in enumerate(lines):
                if idx == 0:
                    # First line: draw bullet symbol
                    # UPGRADE_LATER: Replace with icon image
                    draw.text(
                        (bullet_x, y_position),
                        self.BULLET_SYMBOL,
                        font=font,
                        fill=accent_color
                    )
                
                # Draw text
                draw.text((text_x, y_position), line, font=font, fill=text_color)
                y_position += self.LINE_SPACING
            
            # Extra space between bullets
            y_position += 20
    
    def render_slide(
        self,
        layout: SlideLayout,
        theme: ThemeConfig,
        output_path: Path
    ) -> Path:
        """
        Render a single slide to PNG file.
        
        Args:
            layout: Slide layout configuration
            theme: Theme configuration
            output_path: Path where PNG should be saved
            
        Returns:
            Path to saved PNG file
        """
        logger.info(f"Rendering slide {layout.slide_number}: '{layout.title}'")
        
        # Create background
        canvas = self._create_background(theme)
        draw = ImageDraw.Draw(canvas)
        
        # Render title
        title_end_y = self._render_title(
            draw,
            layout.title,
            layout.font_size_title,
            theme
        )
        
        # Render content/bullets
        content_start_y = max(title_end_y + 80, self.CONTENT_START_Y)
        self._render_bullet_points(
            draw,
            layout.content,
            content_start_y,
            layout.font_size_content,
            theme
        )
        
        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output_path, 'PNG', quality=95)
        
        logger.info(f"Slide saved to: {output_path}")
        return output_path
    
    def render_multiple_slides(
        self,
        layouts: List[SlideLayout],
        theme: ThemeConfig,
        output_dir: Path
    ) -> List[Path]:
        """
        Render multiple slides.
        
        Args:
            layouts: List of slide layouts
            theme: Theme configuration
            output_dir: Directory where PNGs should be saved
            
        Returns:
            List of paths to saved PNG files
        """
        logger.info(f"Rendering {len(layouts)} slides to {output_dir}")
        
        output_paths = []
        
        for layout in layouts:
            # Generate filename: slide_001.png, slide_002.png, etc.
            filename = f"slide_{layout.slide_number:03d}.png"
            output_path = output_dir / filename
            
            self.render_slide(layout, theme, output_path)
            output_paths.append(output_path)
        
        logger.info(f"Successfully rendered {len(output_paths)} slides")
        return output_paths


# UPGRADE_LATER: Create advanced renderers
# 
# class GradientRenderer(SlideRenderer):
#     """Renderer with gradient backgrounds"""
#     
#     def _create_background(self, theme: ThemeConfig) -> Image.Image:
#         # Create gradient from background_color to accent_color
#         pass
#
# class PremiumRenderer(SlideRenderer):
#     """Renderer with all advanced features"""
#     
#     def _create_background(self, theme: ThemeConfig) -> Image.Image:
#         # Gradient backgrounds
#         pass
#     
#     def _render_title(self, ...):
#         # Add shadows, outlines
#         pass
#     
#     def _render_bullet_points(self, ...):
#         # Use icon images instead of bullet symbols
#         pass
