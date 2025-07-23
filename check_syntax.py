"""Vérification de syntaxe des fichiers modifiés"""

import ast
import sys

def check_file_syntax(filename):
    """Vérifie la syntaxe d'un fichier Python"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Erreur de syntaxe: {e}"
    except Exception as e:
        return False, f"Erreur: {e}"

files_to_check = [
    'TennisRPG_v2/utils/constants.py',
    'TennisRPG_v2/utils/helpers.py',
    'TennisRPG_v2/entities/player.py',
    'TennisRPG_v2/managers/weekly_activity_manager.py'
]

print("Vérification de la syntaxe des fichiers modifiés:")
print("=" * 50)

all_ok = True
for filename in files_to_check:
    is_ok, message = check_file_syntax(filename)
    status = "✅" if is_ok else "❌"
    print(f"{status} {filename}: {message}")
    if not is_ok:
        all_ok = False

print("\n" + "=" * 50)
if all_ok:
    print("✅ TOUTES LES VÉRIFICATIONS DE SYNTAXE RÉUSSIES!")
else:
    print("❌ ERREURS DE SYNTAXE TROUVÉES!")