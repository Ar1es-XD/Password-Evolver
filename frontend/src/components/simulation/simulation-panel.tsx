"use client";

import { useEffect, useState } from "react";

import { getSimulation } from "@/lib/api/simulations";
import { SimulationStatus } from "@/lib/api/types";
import { useSimulationSocket } from "@/lib/ws/useSimulationSocket";
import { Card } from "@/components/ui/card";
import { ProgressBar } from "@/components/simulation/progress-bar";
import { StatsCard } from "@/components/simulation/stats-card";

export function SimulationPanel({ simulationId }: { simulationId: string }) {
    const [initialStatus, setInitialStatus] = useState<SimulationStatus | null>(null);
    const [error, setError] = useState<string | null>(null);
    const { status, connectionState } = useSimulationSocket(simulationId, initialStatus);

    useEffect(() => {
        let mounted = true;
        getSimulation(simulationId)
            .then((response) => {
                if (mounted) {
                    setInitialStatus(response);
                }
            })
            .catch((err) => {
                if (mounted) {
                    setError(err instanceof Error ? err.message : "Unable to load simulation.");
                }
            });
        return () => {
            mounted = false;
        };
    }, [simulationId]);

    const display = status ?? initialStatus;

    if (error) {
        return <Card className="p-6 text-sm text-red-600">{error}</Card>;
    }

    if (!display) {
        return <Card className="p-6 text-sm text-ink/60">Loading simulation...</Card>;
    }

    return (
        <section className="grid gap-6 lg:grid-cols-[2fr_1fr]">
            <Card className="space-y-6 p-6 shadow-glow">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs uppercase tracking-[0.3em] text-ink/60">Session</p>
                        <h3 className="font-display text-xl font-semibold text-ink">{display.id}</h3>
                    </div>
                    <div className="text-xs uppercase tracking-[0.3em] text-ink/60">
                        {connectionState}
                    </div>
                </div>
                <div className="rounded-2xl border border-ink/10 bg-white/90 p-4">
                    <p className="text-xs uppercase tracking-[0.3em] text-ink/60">Current string</p>
                    <p className="mt-3 break-all font-mono text-lg text-ink">{display.current}</p>
                </div>
                <ProgressBar progress={display.progress} />
                <div className="grid gap-4 md:grid-cols-2">
                    <StatsCard label="Target" value={display.target} />
                    <StatsCard label="Matched" value={`${display.matched} / ${display.target.length}`} />
                    <StatsCard label="Attempts" value={display.attempts.toLocaleString()} />
                    <StatsCard label="Speed" value={`${Math.round(display.speed).toLocaleString()} tries/sec`} />
                </div>
            </Card>
            <Card className="space-y-4 p-6 shadow-glow">
                <div>
                    <p className="text-xs uppercase tracking-[0.3em] text-ink/60">Status</p>
                    <h4 className="font-display text-lg font-semibold text-ink">
                        {display.completed ? "Completed" : "Running"}
                    </h4>
                </div>
                <div className="space-y-2 text-sm text-ink/70">
                    <p>Elapsed: {display.elapsed.toFixed(2)}s</p>
                    <p>Progress: {(display.progress * 100).toFixed(1)}%</p>
                </div>
                <div className="rounded-2xl border border-ink/10 bg-ink/95 p-4 text-sm text-white">
                    <p className="text-xs uppercase tracking-[0.3em] text-white/60">Tip</p>
                    <p className="mt-2">
                        Use short targets in production environments. Never submit real passwords.
                    </p>
                </div>
            </Card>
        </section>
    );
}
