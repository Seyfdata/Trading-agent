"""
Lance le serveur FastAPI et ouvre le dashboard dans le navigateur.

Usage :
    python launch_dashboard.py

Le serveur tourne jusqu'à Ctrl+C.
"""

import subprocess
import sys
import time
import webbrowser

PORT          = 8000
DASHBOARD_URL = f"http://localhost:{PORT}/dashboard"
DOCS_URL      = f"http://localhost:{PORT}/docs"


def kill_port(port=8000):
    """Tue tout processus utilisant le port spécifié (Windows)."""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{port}',
            shell=True, capture_output=True, text=True
        )
        for line in result.stdout.strip().split('\n'):
            if 'LISTENING' in line:
                pid = line.strip().split()[-1]
                subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                print(f"  Ancien serveur (PID {pid}) arrêté.")
    except Exception:
        pass


def main():
    print()
    print("  Libération du port 8000...")
    kill_port(PORT)
    print("  Démarrage du serveur FastAPI...")

    cmd = [
        sys.executable, "-m", "uvicorn",
        "dashboard.api:app",
        "--host", "0.0.0.0",
        "--port", str(PORT),
    ]

    # Uvicorn hérite de stdout/stderr → ses logs apparaissent directement
    proc = subprocess.Popen(cmd)

    print(f"  PID {proc.pid} — attente 2s...")
    time.sleep(2)

    if proc.poll() is not None:
        print()
        print(f"  [ERREUR] Le serveur n'a pas demarré (code {proc.returncode}).")
        print("     Vérifiez que fastapi et uvicorn sont installés :")
        print("     pip install fastapi uvicorn")
        sys.exit(1)

    # Ouvrir le navigateur
    webbrowser.open(DASHBOARD_URL)

    print()
    print("=" * 50)
    print("SMC-AI Dashboard lance !")
    print(f"Dashboard : {DASHBOARD_URL}")
    print(f"API       : {DOCS_URL}")
    print("   Ctrl+C pour arrêter")
    print("=" * 50)
    print()

    try:
        proc.wait()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n  Arrêt du serveur...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("  Serveur arrêté. À demain !")


if __name__ == "__main__":
    main()
