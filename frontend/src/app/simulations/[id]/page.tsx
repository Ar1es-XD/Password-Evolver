"use client";

import { useParams } from "next/navigation";

import { AppShell } from "@/components/layout/app-shell";
import { SimulationPanel } from "@/components/simulation/simulation-panel";

export default function SimulationPage() {
    const params = useParams();
    const simulationId = Array.isArray(params.id) ? params.id[0] : params.id;

    if (!simulationId) {
        return null;
    }

    return (
        <AppShell>
            <SimulationPanel simulationId={simulationId} />
        </AppShell>
    );
}
