import * as React from "react";

import { cn } from "@/lib/utils/cn";

function Card({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
    return (
        <div
            className={cn("rounded-3xl border border-white/60 bg-white/70 backdrop-blur", className)}
            {...props}
        />
    );
}

export { Card };
