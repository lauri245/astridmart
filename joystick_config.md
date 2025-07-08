# Arcade Controller Configuration Guide

## Overview

Your arcade controller should now work with the game! The game supports both keyboard controls (for testing) and joystick controls (for the arcade experience).

## Default Button Mapping

The game uses this default button mapping for most arcade controllers:

| Physical Button | Joystick Button | Color  | Function |
|-----------------|----------------|--------|----------|
| K1              | Button 0       | GREEN  | Start/Go actions (Self-checkout, Remove last item) |
| K2              | Button 1       | BLUE   | Primary actions (Learning mode, Checkout) |
| K3              | Button 2       | YELLOW | Utility actions (Product manager, Clear cart) |
| K4              | Button 3       | RED    | Stop/Exit actions (Quit game, Return to menu) |

## Testing Your Controller

1. **Run the joystick test**:
   ```bash
   python3 test_joystick_simple.py
   ```

2. **Test with the game**:
   ```bash
   python3 main.py --debug --windowed
   ```

3. **Press each of your K1-K4 buttons** and note which button numbers they correspond to.

## Customizing Button Mapping

If your controller uses different button numbers, you can customize the mapping:

### Option 1: Edit the Game Code

In `main.py`, find this section in the `__init__` method:

```python
self.joystick_button_mapping = {
    # Default mapping for common arcade controllers
    # These can be adjusted based on your specific controller
    0: 'green',  # K1 - GREEN button (Start/Go actions)
    1: 'blue',   # K2 - BLUE button (Primary actions)
    2: 'yellow', # K3 - YELLOW button (Utility actions)
    3: 'red'     # K4 - RED button (Stop/Exit actions)
}
```

Change the numbers to match your controller. For example, if your buttons are 4, 5, 6, 7:

```python
self.joystick_button_mapping = {
    4: 'green',  # K1 - GREEN button (Start/Go actions)
    5: 'blue',   # K2 - BLUE button (Primary actions)
    6: 'yellow', # K3 - YELLOW button (Utility actions)
    7: 'red'     # K4 - RED button (Stop/Exit actions)
}
```

### Option 2: Create a Configuration File

You can also create a `joystick_config.json` file to customize the mapping without editing the code:

```json
{
    "button_mapping": {
        "0": "green",
        "1": "blue", 
        "2": "yellow",
        "3": "red"
    }
}
```

## Common Controller Types

### DragonRise Inc. Controllers
- Usually use buttons 0, 1, 2, 3 for the first four buttons
- Should work with the default mapping

### RetroPie Controllers
- May use buttons 0, 1, 2, 3 (Player 1 buttons)
- Or buttons 4, 5, 6, 7 (Player 2 buttons)

### Custom Arduino Controllers
- Button numbers depend on your specific wiring
- Use the test script to identify the correct numbers

## Troubleshooting

### Controller Not Detected
- Make sure the controller is plugged in before starting the game
- Try different USB ports
- Check if the controller works with other applications

### Wrong Button Mapping
- Use `test_joystick_simple.py` to identify the correct button numbers
- Update the `joystick_button_mapping` in the code
- Restart the game after making changes

### Game Still Uses Keyboard
- The game supports both keyboard and joystick simultaneously
- Keyboard controls are kept for testing purposes
- Joystick controls will override keyboard when pressed

## Debug Mode

Run the game with `--debug` to see detailed joystick information:

```bash
python3 main.py --debug --windowed
```

This will show:
- Which joystick is detected
- How many buttons it has
- Which button numbers are pressed
- The current button mapping

## Button Functions by Game Mode

### Menu
- **GREEN (K1)**: Start Self-checkout mode (Go/Start action)
- **BLUE (K2)**: Start Learning mode (Educational action)
- **YELLOW (K3)**: Open Product manager (Utility action)
- **RED (K4)**: Quit game (Stop/Exit action)

### Self-checkout Mode
- **GREEN (K1)**: Remove last item from cart (Quick undo action)
- **BLUE (K2)**: Proceed to checkout/payment (Primary action)
- **YELLOW (K3)**: Clear entire cart (Utility action)
- **RED (K4)**: Return to menu (Stop/Exit action)

### Learning Mode
- **RED (K4)**: Return to menu (Stop/Exit action)
- Barcode scanner is used to scan products

### Payment Mode
- **BLUE (K2)**: Advance through payment steps (Primary action)
- **RED (K4)**: Cancel payment, return to shopping (Stop/Exit action)

## Notes

- The game maintains keyboard shortcuts for development and testing
- Joystick controls are designed for the final arcade experience
- All game functions can be accessed through the four colored buttons
- The barcode scanner works independently of the joystick controls 