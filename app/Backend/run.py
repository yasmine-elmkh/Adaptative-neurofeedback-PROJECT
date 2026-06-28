"""
Script de démarrage NeuroCap
=============================
Fix DNS Windows : le DNS système ne résout pas Supabase (Errno 11001).
UDP/8.8.8.8 fonctionne → on patche socket.getaddrinfo pour utiliser
dnspython avec Google DNS (8.8.8.8 / 1.1.1.1) pour tous les hostnames
Supabase, avant que uvicorn et le client HTTP soient chargés.

Lancement : python run.py  (depuis app/Backend/)
"""
import socket
import sys

# ── Patch DNS avant tout import réseau ──────────────────────────────────────────
def _install_dns_patch():
    """
    Remplace socket.getaddrinfo pour résoudre les hostnames Supabase
    via Google DNS (8.8.8.8 / 1.1.1.1) au lieu du DNS système Windows
    qui échoue avec [Errno 11001] getaddrinfo failed.
    """
    try:
        import dns.resolver as _dns

        _resolver = _dns.Resolver()
        _resolver.nameservers = ['8.8.8.8', '1.1.1.1']
        _resolver.lifetime = 5.0
        _cache: dict = {}

        _orig = socket.getaddrinfo

        def _patched(host, port, family=0, type=0, proto=0, flags=0):
            if isinstance(host, str) and 'supabase' in host:
                if host not in _cache:
                    try:
                        answers = _resolver.resolve(host, 'A')
                        _cache[host] = str(answers[0])
                        print(f"[DNS] {host} → {_cache[host]} (via 8.8.8.8)", flush=True)
                    except Exception as e:
                        print(f"[DNS] résolution {host} échouée: {e}", flush=True)
                if host in _cache:
                    return _orig(_cache[host], port, family, type, proto, flags)
            return _orig(host, port, family, type, proto, flags)

        socket.getaddrinfo = _patched
        print("[NeuroCap] Patch DNS actif — Supabase résolu via Google DNS", flush=True)

    except ImportError:
        print("[NeuroCap] dnspython absent — pip install dnspython", flush=True)
    except Exception as e:
        print(f"[NeuroCap] DNS patch ignoré: {e}", flush=True)


_install_dns_patch()

# ── Policy asyncio Windows (backup) ─────────────────────────────────────────────
import asyncio
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ── Imports APRÈS le patch ───────────────────────────────────────────────────────
import uvicorn

if __name__ == "__main__":
    config = uvicorn.Config(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=False,
        loop="asyncio",
    )
    server = uvicorn.Server(config)

    if sys.platform == "win32":
        loop = asyncio.SelectorEventLoop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(server.serve())
        finally:
            try:
                loop.close()
            except Exception:
                pass
    else:
        asyncio.run(server.serve())
