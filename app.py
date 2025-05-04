import json
import os
import colorsys
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename

# Create the Flask application instance
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'json'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create uploads folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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

    # Adjust color based on ancestry if significantly present
    # This can be adjusted with more detailed rules

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
    dominant_ancestry = max(ancestry.items(), key=lambda x: x[1])[0]
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
    dominant_ancestry = max(ancestry.items(), key=lambda x: x[1])[0]
    ancestry_readable = dominant_ancestry.replace('_', ' ').title()

    if traits['extroversion'] > 0.7:
        personality = "highly extroverted"
    elif traits['extroversion'] < 0.3:
        personality = "more introverted"
    else:
        personality = "balanced"

    if traits['creativity'] > 0.7:
        creativity = "very creative"
    elif traits['creativity'] < 0.3:
        creativity = "practical"
    else:
        creativity = "moderately creative"

    if traits['analytical'] > 0.7:
        analytical = "analytical"
    else:
        analytical = "intuitive"

    explanation = f"""Your theme reflects your {personality} and {creativity} nature, with {ancestry_readable} 
    ancestry influences. The {theme['colors']['primary']} primary color represents your {personality} 
    tendencies, while the {theme['font']['name']} font was selected to complement your 
    {creativity} and {analytical} traits. The {theme['layout']['name']} layout style 
    brings everything together in a way that resonates with your unique personality profile."""

    return explanation

@app.route("/", methods=["POST"])
def generate_theme_route():
    file = request.files.get("dna_file")
    if file and allowed_file(file.filename):
        try:
            dna_data = json.load(file)  # Load the DNA data from the uploaded file
            theme, explanation = generate_theme(dna_data)  # Pass dna_data to the function
            if theme:
                session['theme'] = theme
                session['explanation'] = explanation
                return redirect(url_for('results'))
            else:
                flash("Failed to generate theme. Please check your DNA file.", "error")
        except Exception as e:
            flash(f"Error processing file: {e}", "error")
    else:
        flash("Invalid file. Please upload a valid DNA JSON file.", "error")
    return redirect(url_for("index"))
@app.route("/", methods=["POST"])
def generate_theme(dna_data):
    """Generate a theme based on the DNA data"""
    try:
        # Process dna_data to extract traits, ancestry, etc.
        traits = dna_data.get('personality_traits', {})
        ancestry = dna_data.get('ancestry', {})

        # Generate colors, font, and layout
        colors = get_color_from_traits(traits, ancestry)
        font = get_font_from_traits(traits)
        layout = get_layout_from_traits(traits)

        # Create the theme dictionary
        theme = {
            'colors': colors,
            'font': font,
            'layout': layout,
            'bg_color': colors['primary'],
            'accent_color': colors['accent'],
            'font_name': font['name'],
            'layout_style': layout['name'],
        }

        # Generate explanation
        explanation = generate_theme_explanation(theme, traits, ancestry)
        return theme, explanation

    except Exception as e:
        print(f"Error generating theme: {e}")
        return None, None
def mock_theme():
    primary = request.args.get("primary", "#ffffff")
    accent = request.args.get("accent", "#000000")
    font = request.args.get("font", "Default Font")
    layout = request.args.get("layout", "Default Layout")
    return render_template("mock_theme.html", primary=primary, accent=accent, font=font, layout=layout)

@app.route("/", methods=["GET", "POST"])

def index():
    theme = None
    explanation = ""
    if request.method == "POST":
        file = request.files.get("dna_file")
        if file and allowed_file(file.filename):
            try:
                dna_data = json.load(file)
                # generate_theme now returns both theme and explanation
                theme, explanation = generate_theme(dna_data)
                if not theme:
                    flash("Failed to generate theme. Please check your DNA file.", "error")
            except Exception as e:
                flash(f"Error processing file: {e}", "error")
        else:
            flash("Invalid file. Please upload a valid DNA JSON file.", "error")
    return render_template("index.html", theme=theme, explanation=explanation)
 
@app.route('/results')
def results():
    theme = session.get('theme')
    explanation = session.get('explanation')
    name = session.get('name', 'User')

    if not theme:
        flash('No theme data found. Please upload your DNA file first.', 'error')
        return redirect(url_for('index'))

    if not isinstance(theme, dict):
        theme = {}
    if 'colors' not in theme:
        theme['colors'] = {'primary': '#cccccc', 'accent': '#888888'}
    if 'font' not in theme:
        theme['font'] = {'name': 'Inter', 'description': 'Default font'}
    if 'layout' not in theme:
        theme['layout'] = {'name': 'Balanced', 'description': 'Default layout'}
    if 'bg_color' not in theme:
        theme['bg_color'] = theme['colors']['primary']
    if 'accent_color' not in theme:
        theme['accent_color'] = theme['colors']['accent']
    if 'font_name' not in theme:
        theme['font_name'] = theme['font']['name']

    return render_template('results.html', theme=theme, explanation=explanation, name=name)


@app.route('/examples')
def examples():
    example_themes = []
    example_dna_files = [
        'example1.json',
        'example2.json',
        'example3.json',
        'example4.json',
        'example5.json'
    ]

    for file in example_dna_files:
        try:
            with open(os.path.join('examples', file), 'r') as f:
                dna_data = json.load(f)
                theme, explanation = generate_theme(dna_data)
                if theme:
                    example_themes.append({
                        'name': dna_data.get('name', 'Example User'),
                        'theme': theme,
                        'explanation': explanation
                    })
        except Exception as e:
            print(f"Error loading example {file}: {e}")

    return render_template('examples.html', examples=example_themes)


if __name__ == '__main__':
    app.run(debug=True)