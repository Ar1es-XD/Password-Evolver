import "./globals.css";

import type { Metadata } from "next";
import { Space_Grotesk, IBM_Plex_Sans } from "next/font/google";
import type { ReactNode } from "react";

import Providers from "@/app/providers";

const display = Space_Grotesk({ subsets: ["latin"], variable: "--font-display" });
const body = IBM_Plex_Sans({ subsets: ["latin"], variable: "--font-body", weight: ["300", "400", "500", "600"] });

export const metadata: Metadata = {
    title: "Password Evolver",
    description: "Realtime simulation UI for the Password Evolver backend."
};

export default function RootLayout({ children }: { children: ReactNode }) {
    return (
        <html lang="en">
            <body className={`${display.variable} ${body.variable} font-body text-ink`}>
                <Providers>{children}</Providers>
            </body>
        </html>
    );
}
