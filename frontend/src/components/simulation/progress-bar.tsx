import { motion } from "framer-motion";

export function ProgressBar({ progress }: { progress: number }) {
    const percent = Math.min(Math.max(progress, 0), 1) * 100;

    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between text-xs uppercase tracking-[0.3em] text-ink/60">
                <span>Progress</span>
                <span>{percent.toFixed(1)}%</span>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-ink/10">
                <motion.div
                    className="h-full rounded-full bg-gradient-to-r from-accent to-ocean"
                    initial={{ width: 0 }}
                    animate={{ width: `${percent}%` }}
                />
            </div>
        </div>
    );
}
