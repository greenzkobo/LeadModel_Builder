"""
menu/main.py
=============
Main menu loop for the ML Modeling Toolkit.
Owns the MLToolkit app object, session, and dispatches to action handlers.

Entry point:
    python -m menu.main
    or
    from menu.main import main; main()
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import BASE_DIR
from session.startup import run_startup
from menu import actions
from menu.auto_run import run_auto_pipeline


class MLToolkit:
    """
    Holds all in-memory state for the current session.
    Passed to every action handler so they can read/write shared state.
    """

    def __init__(self):
        # Session (set by startup)
        self.session      = None
        self.client       = None
        self.client_path  = None

        # Data state
        self.df           = None
        self.df_clean     = None
        self.cleaner      = None
        self.selector     = None

        # Model state
        self.trainer      = None
        self.evaluator    = None

        # Settings
        self.test_size    = 0.30
        self.target       = "IsTarget"

    # ------------------------------------------------------------------
    # Display helpers
    # ------------------------------------------------------------------

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        print("\n" + "="*60)
        print("         ML MODELING TOOLKIT")
        print("="*60)

        if self.client:
            print(f"  Client : {self.client}")

        if self.session and self.session.state:
            st = self.session.state
            chk    = st.get('active_checkpoint', 'scratch')
            chkpts = st.get('checkpoints', {})
            if chkpts.get(chk):
                shape = chkpts[chk].get('shape', [])
                if shape:
                    print(f"  Data   : {shape[0]:,} × {shape[1]:,}  [{chk}]")

            fs = st.get('feature_set', {})
            if fs.get('exists'):
                print(f"  FS     : {fs.get('features')} features selected")

            models = st.get('models', {})
            if models.get('count', 0) > 0:
                lift_str = (f"  |  best lift: {models['best_lift']:.3f}"
                            if models.get('best_lift') else "")
                print(f"  Models : {models['count']} trained  "
                      f"|  winner: {models.get('winner', '?')}{lift_str}")
        elif self.df is not None:
            print(f"  Data   : {len(self.df):,} × {len(self.df.columns):,}")

        print("="*60)

    def print_menu(self):
        print("\n  SELECT AN ACTION:")
        print("  " + "─"*45)
        print("  A.  AUTO-RUN  (full pipeline)")
        print("  " + "─"*45)
        print("  1.  Select / Create Client")
        print("  2.  Data Ingestion")
        print("  3.  Data Profiling")
        print("  4.  Data Cleaning")
        print("  5.  Feature Selection")
        print("  6.  Model Training")
        print("  7.  Model Evaluation")
        print("  8.  Visualizations")
        print("  9.  Export Scoring Code")
        print("  10. Generate Report")
        print("  " + "─"*45)
        print("  L.  View Model Run Log")
        print("  D.  Data Dictionary")
        print("  S.  Settings")
        print("  0.  Exit")
        print()

    def get_input(self, prompt: str, valid: list = None) -> str:
        while True:
            choice = input(prompt).strip()
            if valid is None or choice.lower() in [str(v).lower() for v in valid]:
                return choice
            print(f"  Invalid. Options: {valid}")

    def pause(self):
        input("\n  Press Enter to continue...")

    # ------------------------------------------------------------------
    # Client selection (separate from startup — used for mid-session switch)
    # ------------------------------------------------------------------

    def action_select_client(self):
        from config import list_clients, create_folder_structure, get_paths
        from session import SessionManager
        from session import state as state_mod

        clients = list_clients()
        print("\n  EXISTING CLIENTS:")
        for i, c in enumerate(clients, 1):
            print(f"    {i}. {c}")
        print("    N. New client")
        print()

        choice = input("  Enter number or N: ").strip().upper()

        if choice == 'N':
            name = input("  New client name: ").strip()
            if not name:
                return
            create_folder_structure(name)
            self.client      = name
            self.client_path = get_paths(name)['client']
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(clients):
                    self.client      = clients[idx]
                    self.client_path = get_paths(self.client)['client']
                else:
                    print("  Invalid.")
                    return
            except ValueError:
                print("  Invalid.")
                return

        # Check for existing session on this client
        existing = state_mod.load(self.client_path)
        self.session = SessionManager(self.client, self.client_path)

        if state_mod.is_in_progress(existing):
            print(f"\n  Existing session found: {state_mod.format_summary(existing)}")
            cont = input("  Continue it? (y/n): ").strip().lower()
            if cont == 'y':
                self.session.load_or_create()
            else:
                self.session.start_fresh()
        else:
            self.session.load_or_create()

        # Reset in-memory data state
        self.df = self.df_clean = self.cleaner = None
        self.selector = self.trainer = self.evaluator = None
        print(f"\n  ✓ Client set to: {self.client}")

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self):
        """Startup flow then main menu loop."""

        # ── Startup ────────────────────────────────────────────────
        self.session = run_startup()
        if self.session is None:
            print("\n  Goodbye!\n")
            return

        self.client      = self.session.client
        self.client_path = self.session.client_path
        self.target      = self.session.target

        # ── Main loop ──────────────────────────────────────────────
        valid = ['0','1','2','3','4','5','6','7','8','9','10',
                 'a','d','l','s']

        while True:
            self.clear()
            self.print_header()
            self.print_menu()

            choice = self.get_input("  Enter choice: ", valid)

            if choice == '0':
                print("\n  Goodbye!\n")
                break

            elif choice.lower() == 'a':
                run_auto_pipeline(self)

            elif choice == '1':
                self.action_select_client()

            elif choice == '2':
                actions.action_data_ingestion(self)

            elif choice == '3':
                actions.action_data_profiling(self)

            elif choice == '4':
                actions.action_data_cleaning(self)

            elif choice == '5':
                actions.action_feature_selection(self)

            elif choice == '6':
                actions.action_model_training(self)

            elif choice == '7':
                actions.action_model_evaluation(self)

            elif choice == '8':
                actions.action_visualizations(self)

            elif choice == '9':
                actions.action_export(self)

            elif choice == '10':
                actions.action_generate_report(self)

            elif choice.lower() == 'l':
                actions.action_view_log(self)

            elif choice.lower() == 'd':
                self._action_data_dictionary()

            elif choice.lower() == 's':
                actions.action_settings(self)

            self.pause()

    # ------------------------------------------------------------------
    # Data dictionary (kept inline — small enough)
    # ------------------------------------------------------------------

    def _action_data_dictionary(self):
        from data.dictionary import DataDictionary

        dd = DataDictionary(client=self.client)
        while True:
            print("\n  DATA DICTIONARY")
            print("  1. Show all columns  2. Look up column  "
                  "3. Search keyword  4. By prefix  5. Save to Excel  0. Back\n")
            choice = input("  Enter choice: ").strip()
            if choice == '0':
                break
            elif choice == '1':
                df = self.df_clean if self.df_clean is not None else self.df
                if df is not None:
                    dd.show_columns(df)
                else:
                    print("  ⚠ Load data first.")
            elif choice == '2':
                col = input("  Column name: ").strip()
                print(f"\n  {col}: {dd.lookup(col)}")
            elif choice == '3':
                kw = input("  Keyword: ").strip()
                dd.search(kw)
            elif choice == '4':
                pfx = input("  Prefix (e.g. tw_): ").strip()
                dd.show_by_prefix(pfx)
            elif choice == '5':
                df = self.df_clean if self.df_clean is not None else self.df
                if df is not None:
                    dd.show_columns(df, save=True, client=self.client)
                else:
                    print("  ⚠ Load data first.")
            input("\n  Press Enter to continue...")


def main():
    toolkit = MLToolkit()
    toolkit.run()


if __name__ == "__main__":
    main()

