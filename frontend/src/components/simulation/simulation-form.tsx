"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

import { createSimulation } from "@/lib/api/simulations";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

export function SimulationForm() {
    const router = useRouter();
    const [target, setTarget] = useState("");
    const [updateEvery, setUpdateEvery] = useState("50");
    const [charset, setCharset] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError(null);
        setIsSubmitting(true);

        try {
            const payload = {
                target,
                update_every: updateEvery ? Number(updateEvery) : undefined,
                charset: charset || undefined
            };
            const simulation = await createSimulation(payload);
            router.push(`/simulations/${simulation.id}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to start simulation.");
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Card className="space-y-6 p-6 shadow-glow">
            <div>
                <h3 className="font-display text-xl font-semibold text-ink">Start a simulation</h3>
                <p className="text-sm text-ink/60">Keep targets short and non-sensitive.</p>
            </div>
            <form className="space-y-4" onSubmit={handleSubmit}>
                <div className="space-y-2">
                    <label className="text-xs uppercase tracking-[0.3em] text-ink/60">Target string</label>
                    <Input
                        value={target}
                        onChange={(event) => setTarget(event.target.value)}
                        placeholder="Type a target"
                        required
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-xs uppercase tracking-[0.3em] text-ink/60">Update every</label>
                    <Input
                        type="number"
                        min={1}
                        max={10000}
                        value={updateEvery}
                        onChange={(event) => setUpdateEvery(event.target.value)}
                    />
                </div>
                <div className="space-y-2">
                    <label className="text-xs uppercase tracking-[0.3em] text-ink/60">Custom charset</label>
                    <Input
                        value={charset}
                        onChange={(event) => setCharset(event.target.value)}
                        placeholder="Leave blank for default"
                    />
                </div>
                {error ? <p className="text-sm text-red-600">{error}</p> : null}
                <Button disabled={isSubmitting} type="submit" className="w-full">
                    {isSubmitting ? "Starting..." : "Launch simulation"}
                </Button>
            </form>
        </Card>
    );
}
