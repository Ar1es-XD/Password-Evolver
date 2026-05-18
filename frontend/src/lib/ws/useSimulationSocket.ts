"use client";

import { useEffect, useRef, useState } from "react";

import { env } from "@/lib/config/env";
import { SimulationStatus, SimulationStatusSchema } from "@/lib/api/types";

export function useSimulationSocket(simulationId: string, seed?: SimulationStatus | null) {
    const [status, setStatus] = useState<SimulationStatus | null>(seed ?? null);
    const [connectionState, setConnectionState] = useState("disconnected");
    const socketRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        setStatus(seed ?? null);
    }, [seed]);

    useEffect(() => {
        const socket = new WebSocket(`${env.wsBaseUrl}/ws/simulations/${simulationId}`);
        socketRef.current = socket;
        setConnectionState("connecting");

        socket.onopen = () => setConnectionState("connected");
        socket.onclose = () => setConnectionState("disconnected");
        socket.onerror = () => setConnectionState("error");
        socket.onmessage = (event) => {
            if (event.data === "ping") {
                socket.send("pong");
                return;
            }
            try {
                const parsed = SimulationStatusSchema.parse(JSON.parse(event.data));
                setStatus(parsed);
            } catch (_) {
                // Ignore malformed events.
            }
        };

        return () => {
            socket.close();
            socketRef.current = null;
        };
    }, [simulationId]);

    return { status, connectionState };
}
