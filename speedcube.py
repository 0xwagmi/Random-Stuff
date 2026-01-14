#!/usr/bin/env python3
"""
Speedcube Timer - Track your solves and get statistics
Usage: python timer.py
"""

import sys
import tty
import termios
import time
import json
import random
from pathlib import Path
from datetime import datetime

SOLVES_FILE = Path("speedcube_solves.json")

# Scramble moves for 3x3 cube
MOVES = ['R', 'L', 'U', 'D', 'F', 'B']
MODIFIERS = ['', "'", '2']

# Algorithm tips
TIPS = {
    'f2l': [
        "Look ahead! While solving one pair, search for the next",
        "Practice corner-edge pairing - only 41 cases to learn",
        "Insert pairs from different angles to improve efficiency",
        "Reduce cube rotations - use U moves to bring pairs to front",
        "Learn 'sledgehammer' (R' F R F') and 'hedgeslammer' (F R' F' R)",
    ],
    'oll': [
        "Learn 2-look OLL first: edge orientation (7 algs) + corner orientation (7 algs)",
        "Full OLL has 57 algorithms - tackle similar patterns together",
        "Focus on recognition speed - the solve is faster than the alg",
        "Common patterns: T-shape, L-shape, Lightning bolt, Fish patterns",
        "Practice fingertricks: most OLLs use R U triggers heavily",
    ],
    'pll': [
        "Learn 2-look PLL first: corner permutation + edge permutation (6 algs total)",
        "Full PLL has 21 algorithms - learn recognition from multiple angles",
        "A-perm and U-perm are most common - learn these first",
        "G-perms are fastest but hardest - save for later",
        "Always do a U/U'/U2 AUF (adjust U face) before starting PLL",
    ]
}

# Pro speedcuber algorithms
PRO_ALGS = {
    'pll': {
        'Aa': {
            'feliks': "x R' U R' D2 R U' R' D2 R2 x'",
            'tymon': "x R' U R' D2 R U' R' D2 R2 x'",
            'yiheng': "x R' U R' D2 R U' R' D2 R2 x'",
            'max': "x R' U R' D2 R U' R' D2 R2 R2 x'",
        },
        'Ab': {
            'feliks': "x R2 D2 R U R' D2 R U' R x'",
            'tymon': "x R2 D2 R U R' D2 R U' R x'",
            'yiheng': "x R2 D2 R U R' D2 R U' R x'",
            'max': "x R2 D2 R U R' D2 R U' R x'",
        },
        'T': {
            'feliks': "R U R' U' R' F R2 U' R' U' R U R' F'",
            'tymon': "R U R' U' R' F R2 U' R' U' R U R' F'",
            'yiheng': "R U R' U' R' F R2 U' R' U' R U R' F'",
            'max': "R U R' U' R' F R2 U' R' U' R U R' F'",
        },
        'Ja': {
            'feliks': "x R2 F R F' R U2 r' U r U2 x'",
            'tymon': "R' U L' U2 R U' R' U2 R L U'",
            'yiheng': "x R2 F R F' R U2 r' U r U2 x'",
            'max': "R' U L' U2 R U' R' U2 R L U'",
        },
        'Jb': {
            'feliks': "R U R' F' R U R' U' R' F R2 U' R' U'",
            'tymon': "R U R' F' R U R' U' R' F R2 U' R'",
            'yiheng': "R U R' F' R U R' U' R' F R2 U' R'",
            'max': "R U R' F' R U R' U' R' F R2 U' R'",
        },
        'Ra': {
            'feliks': "R U' R' U' R U R D R' U' R D' R' U2 R' U'",
            'tymon': "R U R' F' R U2 R' U2 R' F R U R U2 R' U'",
            'yiheng': "R U R' F' R U2 R' U2 R' F R U R U2 R' U'",
            'max': "R U' R' U' R U R D R' U' R D' R' U2 R'",
        },
        'Rb': {
            'feliks': "R' U2 R U2 R' F R U R' U' R' F' R2 U'",
            'tymon': "R' U2 R U2 R' F R U R' U' R' F' R2",
            'yiheng': "R' U2 R U2 R' F R U R' U' R' F' R2",
            'max': "R' U2 R U2 R' F R U R' U' R' F' R2 U'",
        },
        'F': {
            'feliks': "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
            'tymon': "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
            'yiheng': "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
            'max': "R' U' F' R U R' U' R' F R2 U' R' U' R U R' U R",
        },
        'Ga': {
            'feliks': "R2 U R' U R' U' R U' R2 D U' R' U R D'",
            'tymon': "R2 u R' U R' U' R u' R2 y' R' U R",
            'yiheng': "R2 u R' U R' U' R u' R2 y' R' U R",
            'max': "R2 U R' U R' U' R U' R2 D U' R' U R D'",
        },
        'Gc': {
            'feliks': "R2 U' R U' R U R' U R2 D' U R U' R' D",
            'tymon': "R2 F2 R U2 R U2 R' F R U R' U' R' F R2",
            'yiheng': "R2 u' R U' R U R' u R2 y R U' R'",
            'max': "R2 U' R U' R U R' U R2 D' U R U' R' D",
        },
        'H': {
            'feliks': "M2 U M2 U2 M2 U M2",
            'tymon': "M2 U M2 U2 M2 U M2",
            'yiheng': "M2 U M2 U2 M2 U M2",
            'max': "M2 U M2 U2 M2 U M2",
        },
        'Ua': {
            'feliks': "M2 U M U2 M' U M2",
            'tymon': "M2 U M U2 M' U M2",
            'yiheng': "M2 U M U2 M' U M2",
            'max': "R U' R U R U R U' R' U' R2",
        },
        'Ub': {
            'feliks': "M2 U' M U2 M' U' M2",
            'tymon': "M2 U' M U2 M' U' M2",
            'yiheng': "M2 U' M U2 M' U' M2",
            'max': "R2 U R U R' U' R' U' R' U R'",
        },
        'Z': {
            'feliks': "M' U M2 U M2 U M' U2 M2",
            'tymon': "M2 U M2 U M' U2 M2 U2 M' U2",
            'yiheng': "M2 U M2 U M' U2 M2 U2 M'",
            'max': "M' U M2 U M2 U M' U2 M2",
        },
    },
    'oll': {
        '21': {  # Cross
            'feliks': "R U2 R' U' R U R' U' R U' R'",
            'tymon': "R U2 R' U' R U R' U' R U' R'",
            'yiheng': "R U2 R' U' R U R' U' R U' R'",
        },
        '22': {  # Cross
            'feliks': "R U2 R2 U' R2 U' R2 U2 R",
            'tymon': "R U2 R2 U' R2 U' R2 U2 R",
            'yiheng': "R U2 R2 U' R2 U' R2 U2 R",
        },
        '23': {  # Cross
            'feliks': "R2 D' R U2 R' D R U2 R",
            'tymon': "R2 D' R U2 R' D R U2 R",
            'yiheng': "R2 D' R U2 R' D R U2 R",
        },
        '24': {  # Cross
            'feliks': "r U R' U' r' F R F'",
            'tymon': "r U R' U' r' F R F'",
            'yiheng': "r U R' U' r' F R F'",
        },
        '25': {  # Cross
            'feliks': "F' r U R' U' r' F R",
            'tymon': "F' r U R' U' r' F R",
            'yiheng': "F' r U R' U' r' F R",
        },
        '26': {  # Cross
            'feliks': "R U2 R' U' R U' R'",
            'tymon': "R U2 R' U' R U' R'",
            'yiheng': "R U2 R' U' R U' R'",
        },
        '27': {  # Cross
            'feliks': "R U R' U R U2 R'",
            'tymon': "R U R' U R U2 R'",
            'yiheng': "R U R' U R U2 R'",
        },
        '33': {  # T-shape
            'feliks': "R U R' U' R' F R F'",
            'tymon': "R U R' U' R' F R F'",
            'yiheng': "R U R' U' R' F R F'",
        },
        '43': {  # P-shape
            'feliks': "f' L' U' L U f",
            'tymon': "R' U' F' U F R",
            'yiheng': "f' L' U' L U f",
        },
        '44': {  # P-shape
            'feliks': "f R U R' U' f'",
            'tymon': "f R U R' U' f'",
            'yiheng': "f R U R' U' f'",
        },
        '45': {  # P-shape
            'feliks': "F R U R' U' F'",
            'tymon': "F R U R' U' F'",
            'yiheng': "F R U R' U' F'",
        },
    }
}

# Cuber profiles
CUBER_INFO = {
    'feliks': 'Feliks Zemdegs - Former WR holder, 4.22 single',
    'tymon': 'Tymon Kolasiński - Current WR holder, 3.13 single',
    'yiheng': 'Yiheng Wang - Current 3x3 avg WR (4.09), youngest sub-5',
    'max': 'Max Park - Multi-WR holder, 3.13 single'
}

def format_time(seconds):
    """Format seconds to MM:SS.CS"""
    if seconds is None:
        return "DNF"
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    centis = int((seconds % 1) * 100)
    if mins > 0:
        return f"{mins}:{secs:02d}.{centis:02d}"
    return f"{secs}.{centis:02d}"

def generate_scramble(length=20):
    """Generate a random scramble"""
    scramble = []
    last_move = None
    
    for _ in range(length):
        # Don't repeat the same face
        available_moves = [m for m in MOVES if m != last_move]
        move = random.choice(available_moves)
        modifier = random.choice(MODIFIERS)
        scramble.append(move + modifier)
        last_move = move
    
    return ' '.join(scramble)

def load_solves():
    """Load previous solves from file"""
    if SOLVES_FILE.exists():
        with open(SOLVES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_solve(solve_time, dnf=False, plus_two=False, scramble=""):
    """Save a solve to file"""
    solves = load_solves()
    
    final_time = None if dnf else (solve_time + 2 if plus_two else solve_time)
    
    solves.append({
        'time': final_time,
        'raw_time': solve_time,
        'dnf': dnf,
        'plus_two': plus_two,
        'scramble': scramble,
        'timestamp': datetime.now().isoformat()
    })
    with open(SOLVES_FILE, 'w') as f:
        json.dump(solves, f, indent=2)

def delete_last_solve():
    """Delete the most recent solve"""
    solves = load_solves()
    if solves:
        solves.pop()
        with open(SOLVES_FILE, 'w') as f:
            json.dump(solves, f, indent=2)
        return True
    return False

def calculate_average(times, remove_extremes=False):
    """Calculate average, optionally removing best and worst"""
    if not times:
        return None
    
    valid_times = [t for t in times if t is not None]
    if not valid_times:
        return None
    
    if remove_extremes and len(valid_times) >= 3:
        sorted_times = sorted(valid_times)
        return sum(sorted_times[1:-1]) / len(sorted_times[1:-1])
    
    return sum(valid_times) / len(valid_times)

def show_statistics():
    """Display solve statistics"""
    solves = load_solves()
    if not solves:
        print("\n❌ No solves recorded yet!\n")
        return
    
    times = [s['time'] for s in solves]
    valid_times = [t for t in times if t is not None]
    
    if not valid_times:
        print("\n❌ No valid times (all DNF)!\n")
        return
    
    avg = sum(valid_times) / len(valid_times)
    best = min(valid_times)
    worst = max(valid_times)
    dnf_count = sum(1 for t in times if t is None)
    
    # Calculate Ao5
    ao5 = None
    if len(times) >= 5:
        ao5 = calculate_average(times[-5:], remove_extremes=True)
    
    # Calculate Ao12
    ao12 = None
    if len(times) >= 12:
        ao12 = calculate_average(times[-12:], remove_extremes=True)
    
    print(f"\n{'='*45}")
    print(f"  📊 STATISTICS ({len(solves)} solves)")
    print(f"{'='*45}")
    print(f"  Session Average:  {format_time(avg)}")
    print(f"  Best Single:      {format_time(best)}")
    print(f"  Worst:            {format_time(worst)}")
    if ao5:
        print(f"  Ao5:              {format_time(ao5)}")
    if ao12:
        print(f"  Ao12:             {format_time(ao12)}")
    if dnf_count > 0:
        print(f"  DNFs:             {dnf_count}")
    print(f"{'='*45}\n")

def show_recent_solves(n=10):
    """Show recent solves"""
    solves = load_solves()
    if not solves:
        print("\n❌ No solves recorded yet!\n")
        return
    
    print(f"\n  📝 Last {min(n, len(solves))} solves:")
    print("  " + "-" * 40)
    for i, solve in enumerate(reversed(solves[-n:]), 1):
        solve_num = len(solves) - i + 1
        time_str = format_time(solve['time'])
        
        penalty = ""
        if solve.get('dnf'):
            penalty = " (DNF)"
        elif solve.get('plus_two'):
            penalty = " (+2)"
        
        print(f"  {solve_num:3d}. {time_str:>8}{penalty}")
    print()

def show_tips(category):
    """Show algorithm tips"""
    if category not in TIPS:
        print("\n❌ Invalid category! Use: f2l, oll, or pll\n")
        return
    
    tips = TIPS[category]
    print(f"\n{'='*50}")
    print(f"  💡 {category.upper()} TIPS")
    print(f"{'='*50}")
    for i, tip in enumerate(tips, 1):
        print(f"  {i}. {tip}")
    print(f"{'='*50}\n")

def show_pro_algs(case_type):
    """Show algorithms used by top speedcubers"""
    if case_type not in PRO_ALGS:
        print("\n❌ Invalid type! Use: pll or oll\n")
        return
    
    print(f"\n{'='*60}")
    print(f"  🏆 PRO {case_type.upper()} ALGORITHMS")
    print(f"{'='*60}")
    print("\n  📌 Top Cubers:")
    for code, name in CUBER_INFO.items():
        print(f"     {code}: {name}")
    print()
    
    cases = PRO_ALGS[case_type]
    
    for case_name, algs in sorted(cases.items()):
        print(f"\n  ─── {case_name} {'─' * (50 - len(case_name))}")
        for cuber, alg in algs.items():
            cuber_name = cuber.capitalize()
            print(f"    {cuber_name:8} → {alg}")
    
    print(f"\n{'='*60}\n")

def get_char():
    """Get a single character from stdin"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

def inspection_countdown():
    """15 second inspection countdown"""
    print("\n🔍 INSPECTION (15 seconds)")
    print("Press SPACE when ready to start solve\n")
    
    start = time.time()
    
    while True:
        elapsed = time.time() - start
        remaining = 15 - elapsed
        
        if remaining <= 0:
            print("\r⏰ TIME'S UP! +2 penalty   ", end='\r')
            time.sleep(1)
            return True  # +2 penalty
        elif remaining <= 3:
            print(f"\r⚠️  {remaining:.1f}s         ", end='\r')
        else:
            print(f"\r⏱️  {remaining:.1f}s         ", end='\r')
        
        sys.stdout.flush()
        
        # Check for space (non-blocking)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            new_settings = termios.tcgetattr(fd)
            new_settings[6][termios.VMIN] = 0
            new_settings[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            
            char = sys.stdin.read(1)
            if char == ' ':
                print("\r                           ")
                return False  # No penalty
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        time.sleep(0.1)

def run_timer():
    """Main timer loop"""
    print("\n" + "="*50)
    print("  🎲 SPEEDCUBE TIMER")
    print("="*50)
    print("  SPACE   - Start/Stop timer")
    print("  i       - Toggle inspection (WCA 15s)")
    print("  s       - Statistics")
    print("  r       - Recent solves")
    print("  d       - Delete last solve")
    print("  t       - Tips (f2l/oll/pll)")
    print("  a       - Pro algorithms (pll/oll)")
    print("  q       - Quit")
    print("="*50 + "\n")
    
    use_inspection = False
    current_scramble = generate_scramble()
    
    while True:
        print(f"🔀 Scramble: {current_scramble}")
        print(f"{'🔍 Inspection: ON' if use_inspection else ''}")
        print("\nPress SPACE when ready...", end='\r')
        sys.stdout.flush()
        
        # Wait for command
        while True:
            char = get_char()
            if char == ' ':
                break
            elif char == 'q':
                print("\n👋 Goodbye!\n")
                return
            elif char == 's':
                show_statistics()
                print(f"🔀 Scramble: {current_scramble}")
                print("Press SPACE when ready...", end='\r')
            elif char == 'r':
                show_recent_solves()
                print(f"🔀 Scramble: {current_scramble}")
                print("Press SPACE when ready...", end='\r')
            elif char == 'd':
                if delete_last_solve():
                    print("\n✅ Last solve deleted!\n")
                else:
                    print("\n❌ No solves to delete!\n")
                print(f"🔀 Scramble: {current_scramble}")
                print("Press SPACE when ready...", end='\r')
            elif char == 'i':
                use_inspection = not use_inspection
                status = "ON" if use_inspection else "OFF"
                print(f"\n🔍 Inspection {status}\n")
                print(f"🔀 Scramble: {current_scramble}")
                print("Press SPACE when ready...", end='\r')
            elif char == 't':
                print("\n\nChoose category:")
                print("  1 - F2L tips")
                print("  2 - OLL tips")
                print("  3 - PLL tips")
                print("Choice: ", end='')
                sys.stdout.flush()
                choice = get_char()
                if choice == '1':
                    show_tips('f2l')
                elif choice == '2':
                    show_tips('oll')
                elif choice == '3':
                    show_tips('pll')
                print(f"🔀 Scramble: {current_scramble}")
                print("Press SPACE when ready...", end='\r')
            elif char == 'a':
                print("\n\nChoose algorithm type:")
                print("  1 - PLL algorithms (by pros)")
                print("  2 - OLL algorithms (by pros)")
                print("Choice: ", end='')
                sys.stdout.flush()
                choice = get_char()
                if choice == '1':
                    show_pro_algs('pll')
                elif choice == '2':
                    show_pro_algs('oll')
                print(f"🔀 Scramble: {current_scramble}")
                print("Press SPACE when ready...", end='\r')
        
        # Inspection phase
        inspection_penalty = False
        if use_inspection:
            inspection_penalty = inspection_countdown()
        
        # Countdown
        for i in range(3, 0, -1):
            print(f"{i}...    ", end='\r')
            sys.stdout.flush()
            time.sleep(1)
        
        print("GO!      ", end='\r')
        sys.stdout.flush()
        time.sleep(0.2)
        
        # Start timer
        start_time = time.time()
        
        # Set non-blocking input
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        
        try:
            tty.setraw(fd)
            new_settings = termios.tcgetattr(fd)
            new_settings[6][termios.VMIN] = 0
            new_settings[6][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSADRAIN, new_settings)
            
            while True:
                elapsed = time.time() - start_time
                print(f"  ⏱️  {format_time(elapsed)}      ", end='\r')
                sys.stdout.flush()
                
                char = sys.stdin.read(1)
                if char == ' ':
                    final_time = time.time() - start_time
                    break
                
                time.sleep(0.01)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
        # Post-solve options
        print(f"\n\n  ⏱️  TIME: {format_time(final_time)}")
        if inspection_penalty:
            print("  ⚠️  Inspection +2 penalty applied")
        print("\n  Enter: OK  |  2: +2  |  x: DNF")
        print("Choice: ", end='')
        sys.stdout.flush()
        
        choice = get_char()
        
        dnf = False
        plus_two = inspection_penalty
        
        if choice == 'x':
            dnf = True
            print("DNF")
        elif choice == '2':
            plus_two = True
            print("+2")
        else:
            print("OK")
        
        # Save solve
        save_solve(final_time, dnf=dnf, plus_two=plus_two, scramble=current_scramble)
        solves = load_solves()
        
        display_time = None if dnf else (final_time + 2 if plus_two else final_time)
        print(f"\n  ✅ Solve #{len(solves)}: {format_time(display_time)}")
        
        # Show quick Ao5
        if len(solves) >= 5:
            times = [s['time'] for s in solves]
            ao5 = calculate_average(times[-5:], remove_extremes=True)
            if ao5:
                print(f"  📊 Ao5: {format_time(ao5)}")
        
        print()
        time.sleep(1)
        
        # Generate new scramble
        current_scramble = generate_scramble()

if __name__ == "__main__":
    try:
        run_timer()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
