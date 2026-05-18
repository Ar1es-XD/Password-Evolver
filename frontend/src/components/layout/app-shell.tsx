import { ReactNode } from "react";

export function AppShell({ children }: { children: ReactNode }) {
    return (
        <main className="main-grid min-h-screen px-6 py-10 md:px-12">
            <div className="mx-auto flex w-full max-w-6xl flex-col gap-12">
                <header className="flex flex-wrap items-center justify-between gap-4">
                    <div className="space-y-1">
                        <p className="text-xs uppercase tracking-[0.35em] text-ink/60">Password Evolver</p>
                        <h2 className="font-display text-2xl font-semibold text-ink">Realtime Simulation Studio</h2>
                    </div>
                    <div className="rounded-full border border-ink/10 bg-white/80 px-4 py-2 text-xs uppercase tracking-[0.3em] text-ink/60 shadow-glow">
                        FastAPI + WebSocket
                    </div>
                </header>
                {children}
            </div>
        </main>
    );
}
