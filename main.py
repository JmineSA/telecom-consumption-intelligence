# main.py - Master runner for all core scripts
import sys
from pathlib import Path

# Setup path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import subprocess
import argparse
from datetime import datetime

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def run_script(script_path, description):
    """Run a Python script and handle errors."""
    print_header(description)
    
    script_full_path = project_root / script_path
    
    if not script_full_path.exists():
        print(f" Script not found: {script_full_path}")
        print(f"   Please check the path and try again.")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_full_path)],
            cwd=str(project_root),
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"\n {description} completed successfully!")
            return True
        else:
            print(f"\n {description} failed with code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"\n Error running {description}: {e}")
        return False

def run_model_training():
    """Run mobile_data_consumption_model.py - Trains the model."""
    return run_script(
        "src/models/mobile_data_consumption_model.py",
        "MODEL TRAINING"
    )

def run_model_evaluation():
    """Run evaluate_model.py - Evaluates model performance."""
    return run_script(
        "src/evaluation/evaluate_model.py",  
        "MODEL EVALUATION"
    )

def run_model_insights():
    """Run model_insights.py - Generates insights and visualizations."""
    return run_script(
        "src/models/model_insignts.py",  # <- Match your misspelled filename
        " MODEL INSIGHTS"
    )

def run_scenario_tests():
    """Run test_model.py - Tests model on scenarios."""
    return run_script(
        "src/tests/test_model.py",
        "SCENARIO TESTS"
    )

def run_pipeline_test():
    """Run test_pipeline.py - Tests the pipeline."""
    return run_script(
        "src/tests/test_pipeline.py",
        "PIPELINE TEST"
    )

def run_preprocessing():
    """Run preprocessing_pipeline.py - Preprocesses data."""
    return run_script(
        "src/pipelines/preprocessing_pipeline.py",
        "DATA PREPROCESSING"
    )

def run_all():
    """Run all core scripts in sequence."""
    print("\n" + "=" * 70)
    print(" RUNNING ALL TASKS")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    scripts = [
        ("src/models/mobile_data_consumption_model.py", " Model Training"),
        ("src/evaluation/evaluate_model.py", " Model Evaluation"),  
        ("src/models/model_insights.py", " Model Insights"),
        ("src/tests/test_model.py", " Scenario Tests"),
    ]
    
    success = True
    for script_path, description in scripts:
        if not run_script(script_path, description):
            success = False
            print(f"\n Stopping due to failure in {description}")
            break
    
    print("\n" + "=" * 70)
    if success:
        print(" ALL TASKS COMPLETED SUCCESSFULLY!")
    else:
        print(" SOME TASKS FAILED")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    return success

def show_menu():
    """Display interactive menu."""
    print("\n" + "=" * 70)
    print(" TELECOM CONSUMPTION INTELLIGENCE")
    print("=" * 70)
    print("\n Available Commands:")
    print("  1. Train Model (mobile_data_consumption_model.py)")
    print("  2. Evaluate Model (evaluate_model.py)")
    print("  3. Generate Insights (model_insights.py)")
    print("  4. Run Scenario Tests (test_model.py)")
    print("  5. Test Pipeline (test_pipeline.py)")
    print("  6. Preprocess Data (preprocessing_pipeline.py)")
    print("  7. Run All (Training + Evaluation + Insights + Tests)")
    print("  8. Exit")
    print("-" * 70)

def main():
    parser = argparse.ArgumentParser(
        description="Telecom Consumption Intelligence - Master Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --train          # Train the model
  python main.py --evaluate       # Evaluate model performance
  python main.py --insights       # Generate model insights
  python main.py --scenario       # Run scenario tests
  python main.py --test           # Test pipeline
  python main.py --preprocess     # Preprocess data
  python main.py --all            # Run everything
        """
    )
    
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--evaluate", action="store_true", help="Evaluate model performance")
    parser.add_argument("--insights", action="store_true", help="Generate model insights")
    parser.add_argument("--scenario", action="store_true", help="Run scenario tests")
    parser.add_argument("--test", action="store_true", help="Test pipeline")
    parser.add_argument("--preprocess", action="store_true", help="Preprocess data")
    parser.add_argument("--all", action="store_true", help="Run everything in sequence")
    parser.add_argument("--menu", action="store_true", help="Show interactive menu")
    
    args = parser.parse_args()
    
    # If no arguments, show menu
    if not any(vars(args).values()):
        args.menu = True
    
    if args.menu:
        while True:
            show_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                run_model_training()
            elif choice == "2":
                run_model_evaluation()
            elif choice == "3":
                run_model_insights()
            elif choice == "4":
                run_scenario_tests()
            elif choice == "5":
                run_pipeline_test()
            elif choice == "6":
                run_preprocessing()
            elif choice == "7":
                run_all()
            elif choice == "8":
                print("\n Goodbye!")
                break
            else:
                print("\n Invalid choice. Please try again.")
            
            input("\nPress Enter to continue...")
    else:
        if args.train:
            run_model_training()
        if args.evaluate:
            run_model_evaluation()
        if args.insights:
            run_model_insights()
        if args.scenario:
            run_scenario_tests()
        if args.test:
            run_pipeline_test()
        if args.preprocess:
            run_preprocessing()
        if args.all:
            run_all()

if __name__ == "__main__":
    main()