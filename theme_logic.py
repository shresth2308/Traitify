import colorsys

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color string"""
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def get_color_from_traits(traits, ancestry):
    """Generate a color based on personality traits and ancestry"""
    # Base color generation from extroversion and creativity
    extroversion = traits.get('extroversion', 0.5)
    creativity = traits.get('creativity', 0.5)
    analytical = traits.get('analytical', 0.5)
    
    # HSV color model: Hue (0-360), Saturation (0-100), Value (0-100)
    
    # Use extroversion to influence hue (color)
    # Higher extroversion -> warmer colors (reds, oranges)
    # Lower extroversion -> cooler colors (blues, greens)
    base_hue = 0.6 - (extroversion * 0.4)  # Maps 0-1 to 0.6-0.2 (blue to red-orange)
    
    # Use creativity to influence saturation
    # More creative -> more saturated colors
    saturation = 0.5 + (creativity * 0.5)  # Maps 0-1 to 0.5-1.0
    
    # Use analytical to influence brightness
    # More analytical -> sharper, clearer colors
    value = 0.7 + (analytical * 0.3)  # Maps 0-1 to 0.7-1.0
    
    # Convert HSV to RGB
    rgb = colorsys.hsv_to_rgb(base_hue, saturation, value)
    # Scale to 0-255
    rgb = tuple(int(c * 255) for c in rgb)
    
    # Ancestry influence for accent color
    accent_color = generate_accent_color(rgb, ancestry)
    
    return {
        'primary': rgb_to_hex(rgb),
        'accent': accent_color
    }

def generate_accent_color(primary_rgb, ancestry):
    """Generate accent color based on primary color and ancestry"""
    # Convert primary RGB to HSV
    r, g, b = primary_rgb[0]/255, primary_rgb[1]/255, primary_rgb[2]/255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    # Adjust hue based on ancestry - move around the color wheel
    ancestry_hue_shifts = {
        'european': 0.5,  # Opposite on color wheel
        'eastern_european': 0.45,
        'mediterranean': 0.4,
        'asian': 0.33,
        'south_asian': 0.25,
        'african': 0.15,
        'middle_eastern': 0.2,
        'native_american': 0.3,
        'pacific_islander': 0.35,
        'nordic': 0.55,
        'central_asian': 0.28
    }
    
    # Find dominant ancestry
    dominant_ancestry = max(ancestry.items(), key=lambda x: x[1])[0] if ancestry else 'european'
    hue_shift = ancestry_hue_shifts.get(dominant_ancestry, 0.5)
    
    # Apply shift to hue (wrap around if exceeds 1)
    new_hue = (h + hue_shift) % 1.0
    
    # Convert back to RGB
    new_rgb = colorsys.hsv_to_rgb(new_hue, s, v)
    # Scale to 0-255
    new_rgb = tuple(int(c * 255) for c in new_rgb)
    
    return rgb_to_hex(new_rgb)

def get_font_from_traits(traits):
    """Select a font based on personality traits"""
    extroversion = traits.get('extroversion', 0.5)
    creativity = traits.get('creativity', 0.5)
    analytical = traits.get('analytical', 0.5)
    
    # Font selection logic
    # Balancing between serif and sans-serif based on analytical vs creative traits
    
    fonts = {
        'creative_extrovert': {
            'name': 'Playfair Display',
            'description': 'Bold, expressive serif font reflecting creativity and confidence'
        },
        'creative_introvert': {
            'name': 'Cormorant Garamond',
            'description': 'Elegant, delicate serif font with artistic sensibility'
        },
        'analytical_extrovert': {
            'name': 'Montserrat',
            'description': 'Clean, strong sans-serif with precise character'
        },
        'analytical_introvert': {
            'name': 'Inter',
            'description': 'Focused, refined sans-serif designed for clarity'
        },
        'balanced': {
            'name': 'Nunito',
            'description': 'Balanced, versatile sans-serif with rounded terminals'
        }
    }
    
    # Determine which category to use
    if creativity > 0.6 and extroversion > 0.6:
        font_type = 'creative_extrovert'
    elif creativity > 0.6 and extroversion <= 0.6:
        font_type = 'creative_introvert'
    elif analytical > 0.6 and extroversion > 0.6:
        font_type = 'analytical_extrovert'
    elif analytical > 0.6 and extroversion <= 0.6:
        font_type = 'analytical_introvert'
    else:
        font_type = 'balanced'
    
    return fonts[font_type]

def get_layout_from_traits(traits):
    """Determine layout style based on personality traits"""
    extroversion = traits.get('extroversion', 0.5)
    risk_taking = traits.get('risk_taking', 0.5)
    empathy = traits.get('empathy', 0.5)
    
    layouts = {
        'bold': {
            'name': 'Bold & Dynamic',
            'description': 'Strong visual elements with high contrast and dynamic spacing'
        },
        'minimal': {
            'name': 'Clean & Minimal',
            'description': 'Elegant minimalism with focused content and precise spacing'
        },
        'balanced': {
            'name': 'Harmonious & Balanced',
            'description': 'Well-balanced layout with thoughtful spacing and moderation'
        },
        'warm': {
            'name': 'Warm & Inviting',
            'description': 'Welcoming layout with soft elements and approachable design'
        },
        'structured': {
            'name': 'Structured & Organized',
            'description': 'Structured layout with clear hierarchy and organization'
        }
    }
    
    # Determine layout based on trait combinations
    if extroversion > 0.7 and risk_taking > 0.7:
        layout = 'bold'
    elif extroversion < 0.4 and risk_taking < 0.4:
        layout = 'minimal'
    elif empathy > 0.7:
        layout = 'warm'
    elif risk_taking < 0.4 and extroversion > 0.6:
        layout = 'structured'
    else:
        layout = 'balanced'
    
    return layouts[layout]

def generate_theme_explanation(theme, traits, ancestry):
    """Create a human-readable explanation of the theme and why it was chosen"""
    # Get dominant ancestry
    dominant_ancestry = max(ancestry.items(), key=lambda x: x[1])[0] if ancestry else 'mixed'
    ancestry_readable = dominant_ancestry.replace('_', ' ').title()
    
    # Personality descriptions
    if traits.get('extroversion', 0.5) > 0.7:
        personality = "highly extroverted"
    elif traits.get('extroversion', 0.5) < 0.3:
        personality = "more introverted"
    else:
        personality = "balanced"
        
    if traits.get('creativity', 0.5) > 0.7:
        creativity = "very creative"
    elif traits.get('creativity', 0.5) < 0.3:
        creativity = "practical"
    else:
        creativity = "moderately creative"
        
    if traits.get('analytical', 0.5) > 0.7:
        analytical = "analytical"
    else:
        analytical = "intuitive"
    
    # Put together explanation
    explanation = f"""Your theme reflects your {personality} and {creativity} nature, with {ancestry_readable} 
    ancestry influences. The {theme['colors']['primary']} primary color represents your {personality} 
    tendencies, while the {theme['font']['name']} font was selected to complement your 
    {creativity} and {analytical} traits. The {theme['layout']['name']} layout style 
    brings everything together in a way that resonates with your unique personality profile."""
    
    return explanation

def generate_theme(dna_data):
    """Generate a theme based on the DNA data"""
    try:
        # Extract relevant data
        traits = dna_data.get('personality_traits', {})
        ancestry = dna_data.get('ancestry', {})
        
        # Generate colors
        colors = get_color_from_traits(traits, ancestry)
        
        # Select font
        font = get_font_from_traits(traits)
        
        # Determine layout style
        layout = get_layout_from_traits(traits)
        
        # Prepare theme data
        theme = {
            'colors': colors,
            'font': font,
            'layout': layout,
            'bg_color': colors['primary'],
            'accent_color': colors['accent'],
            'font_name': font['name'],
            'layout_style': layout['name']
        }
        
        # Generate text explanation
        explanation = generate_theme_explanation(theme, traits, ancestry)
        
        return theme, explanation
        
    except Exception as e:
        print(f"Error generating theme: {e}")
        return None, None