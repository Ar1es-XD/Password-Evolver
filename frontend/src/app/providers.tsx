"use client";

import { MotionConfig } from "framer-motion";
import { ReactNode } from "react";

export default function Providers({ children }: { children: ReactNode }) {
    return (
        <MotionConfig reducedMotion="user" transition={{ duration: 0.4, ease: "easeOut" }}>
            {children}
        </MotionConfig>
    );
}
