import { Card } from "@/components/ui/card";

export function StatsCard({ label, value }: { label: string; value: string }) {
    return (
        <Card className="space-y-2 border-ink/10 bg-white/80 p-4">
            <p className="text-xs uppercase tracking-[0.3em] text-ink/60">{label}</p>
            <p className="text-sm font-semibold text-ink">{value}</p>
        </Card>
    );
}
