import { AppShell } from "@/components/layout/app-shell";
import { SimulationForm } from "@/components/simulation/simulation-form";

export default function HomePage() {
    return (
        <AppShell>
            <section className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr]">
                <div className="space-y-6">
                    <p className="text-sm uppercase tracking-[0.3em] text-ink/60">Simulation console</p>
                    <h1 className="font-display text-4xl font-semibold leading-tight text-ink md:text-5xl">
                        Build a live evolution stream without the terminal.
                    </h1>
                    <p className="text-base text-ink/70 md:text-lg">
                        Create a simulation session, watch the target converge, and stream metrics in real time.
                    </p>
                </div>
                <SimulationForm />
            </section>
        </AppShell>
    );
}
