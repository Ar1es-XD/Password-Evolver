import { z } from "zod";

export const SimulationStatusSchema = z.object({
    id: z.string(),
    target: z.string(),
    current: z.string(),
    attempts: z.number().int(),
    matched: z.number().int(),
    progress: z.number(),
    elapsed: z.number(),
    speed: z.number(),
    completed: z.boolean()
});

export type SimulationStatus = z.infer<typeof SimulationStatusSchema>;

export const SimulationCreateSchema = z.object({
    target: z.string().min(1).max(256),
    charset: z.string().optional(),
    update_every: z.number().int().min(1).max(10000).optional()
});

export type SimulationCreate = z.infer<typeof SimulationCreateSchema>;
