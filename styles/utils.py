def format_dataframe(df):
    """
    Format a Pandas DataFrame with jazzy styling
    """
    from styles.jazzy_theme import get_jazzy_colors
    colors = get_jazzy_colors()

    # Return a styled dataframe
    return df.style.set_properties(**{
        'background-color': colors['background'],
        'color': colors['text'],
        'border-color': colors['accent1']
    })