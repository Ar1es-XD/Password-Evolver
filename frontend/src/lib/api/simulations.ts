import { apiFetch } from "@/lib/api/client";
import {
    SimulationCreate,
    SimulationCreateSchema,
    SimulationStatus,
    SimulationStatusSchema
} from "@/lib/api/types";

export async function createSimulation(payload: SimulationCreate): Promise<SimulationStatus> {
    const validated = SimulationCreateSchema.parse(payload);
    return apiFetch<SimulationCreate, SimulationStatus>("/simulations", {
        method: "POST",
        body: validated,
        schema: SimulationStatusSchema
    });
}

export async function getSimulation(simulationId: string): Promise<SimulationStatus> {
    return apiFetch<undefined, SimulationStatus>(`/simulations/${simulationId}`, {
        schema: SimulationStatusSchema
    });
}
