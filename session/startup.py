"""
session/startup.py
===================
Startup flow shown once when the toolkit launches.
Returns a ready SessionManager to menu/main.py.
"""

import os
from config import list_clients, create_folder_structure, get_paths
from session import SessionManager
from session import state as state_mod
from session import archive as archive_mod


def run_startup():
    _print_banner()
    client, client_path = _select_client()
    if client is None:
        return None

    session  = SessionManager(client=client, client_path=client_path)
    existing = session.get_existing_state()

    if state_mod.is_in_progress(existing):
        choice = _prompt_continue_or_fresh(existing)
        if choice == 'continue':
            session.load_or_create()
        elif choice == 'fresh':
            _confirm_and_start_fresh(session)
        elif choice == 'archives':
            session.show_archives()
            input("\n  Press Enter to continue...")
            return run_startup()
    else:
        session.load_or_create()

    return session


def _print_banner():
    print("\n" + "="*60)
    print("         ML MODELING TOOLKIT")
    print("="*60)


def _select_client() -> tuple:
    clients = list_clients()
    print("\n  SELECT CLIENT\n  " + "-"*40)

    if clients:
        for i, c in enumerate(clients, 1):
            existing = state_mod.load(get_paths(c)['client'])
            if state_mod.is_in_progress(existing):
                m      = existing.get('models', {})
                lift   = m.get('best_lift')
                status = f"  ← in progress | models: {m.get('count', 0)}"
                if lift:
                    status += f" | best lift: {lift:.3f}"
            else:
                status = ""
            print(f"  {i}. {c}{status}")
        print("  N. New client\n  0. Exit\n")
        choice = input("  Enter number, N, or 0: ").strip()
    else:
        print("  No existing clients found.")
        choice = 'N'

    if choice == '0':
        return None, None
    if choice.upper() == 'N':
        name = input("  New client name: ").strip()
        if not name:
            return None, None
        create_folder_structure(name)
        return name, get_paths(name)['client']
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(clients):
            c = clients[idx]
            return c, get_paths(c)['client']
        print("  Invalid selection.")
        return None, None
    except ValueError:
        print("  Invalid input.")
        return None, None


def _prompt_continue_or_fresh(existing: dict) -> str:
    print(f"\n  {'─'*50}\n  EXISTING SESSION FOUND\n  {'─'*50}")
    print(f"  Started:     {existing.get('started', 'unknown')}")
    print(f"  Last active: {existing.get('last_active', 'unknown')}")

    chk = existing.get('active_checkpoint', 'scratch')
    chkpt = existing.get('checkpoints', {}).get(chk, {})
    if chkpt and chkpt.get('shape'):
        s = chkpt['shape']
        print(f"  Checkpoint:  {chk}  ({s[0]:,} × {s[1]:,})")

    fs = existing.get('feature_set', {})
    if fs.get('exists'):
        print(f"  Feature set: {fs.get('features')} features")

    m = existing.get('models', {})
    if m.get('count', 0) > 0:
        lift_str = f" — best lift: {m['best_lift']:.3f}" if m.get('best_lift') else ""
        print(f"  Models:      {m['count']} trained | winner: {m.get('winner','none')}{lift_str}")

    print(f"  {'─'*50}\n")
    print("  [1] Continue this session")
    print("  [2] Start fresh  (archives current session)")
    print("  [3] View past archives\n")
    return {'1': 'continue', '2': 'fresh', '3': 'archives'}.get(
        input("  Enter choice: ").strip(), 'continue')


def _confirm_and_start_fresh(session):
    print("\n  ⚠  This will archive the current session.")
    print("     Data files and models are preserved.")
    if input("\n  Type YES to confirm: ").strip().upper() == 'YES':
        session.start_fresh()
    else:
        print("  Cancelled — continuing existing session.")
        session.load_or_create()
