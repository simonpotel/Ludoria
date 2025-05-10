import sys
import os
import subprocess
import time

def run_tests():
    """
    procedure pour lancer les tests unitaires
    """
    print("==== Ludoria Tests ====")
    
    tests_dir = os.path.dirname(os.path.abspath(__file__)) # récupère le chemin du répertoire des tests
    
    test_files = [
        f for f in os.listdir(tests_dir)
        if f.endswith('.py') and f not in ['run_tests.py', 'test_base.py', '__init__.py']
    ] # tous les fichiers .py dans le répertoire des tests, sauf les fichiers run_tests.py, test_base.py et __init__.py
    
    if not test_files:
        # si aucun fichier de test n'est trouvé, on quitte le programme
        print("No test files found! Exiting.")
        return 1
    
    print(f"Found {len(test_files)} test files: {', '.join(test_files)}") # affiche le nombre de fichiers de test trouvés et leur nom
    
    all_passed = True # on initialise la variable all_passed à True et sera False si un test échoue
    passed_tests = 0
    failed_tests = 0
    
    for test_file in sorted(test_files): # on parcourt tous les fichiers de test
        test_path = os.path.join(tests_dir, test_file) # on construit le chemin complet du fichier de test
        print(f"\n{'='*60}")
        print(f"Running: {test_file}")
        print(f"{'='*60}")
        
        start_time = time.time() # on enregistre le temps de début de l'exécution du test
        result = subprocess.run([sys.executable, test_path], capture_output=True, text=True) # on exécute le test
        elapsed_time = time.time() - start_time # on calcule le temps d'exécution du test
        
        if result.stdout:
            print(result.stdout) # on affiche les résultats du test
        if result.stderr:  
            print(result.stderr) # on affiche les erreurs éventuelles
        
        if result.returncode == 0:
            print(f"✓ {test_file} PASSED ({elapsed_time:.2f}s)") # on affiche le résultat du test
            passed_tests += 1
        else:
            print(f"✗ {test_file} FAILED ({elapsed_time:.2f}s)") # on affiche le résultat du test
            failed_tests += 1
            all_passed = False # on met all_passed à False si un test échoue
    
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"{'='*60}")
    print(f"Total test files: {len(test_files)}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(run_tests()) 